# -*- coding: utf-8 -*-
"""
수정된 DXF 파일 처리 모듈 - 속성 추출 문제 해결
ezdxf 라이브러리를 사용하여 DXF 파일에서 모든 속성을 정확히 추출
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field

try:
    import ezdxf
    from ezdxf.document import Drawing
    from ezdxf.entities import Insert, Attrib, AttDef, Text, MText
    from ezdxf.layouts import BlockLayout, Modelspace
    from ezdxf import bbox, disassemble
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False
    logging.warning("ezdxf 라이브러리가 설치되지 않았습니다. DXF 기능이 비활성화됩니다.")

from config import Config


@dataclass
class BoundingBox:
    """바운딩 박스 정보를 담는 데이터 클래스"""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    
    @property
    def width(self) -> float:
        return self.max_x - self.min_x
    
    @property
    def height(self) -> float:
        return self.max_y - self.min_y
    
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)
    
    def merge(self, other: 'BoundingBox') -> 'BoundingBox':
        """다른 바운딩 박스와 병합하여 가장 큰 외곽 박스 반환"""
        return BoundingBox(
            min_x=min(self.min_x, other.min_x),
            min_y=min(self.min_y, other.min_y),
            max_x=max(self.max_x, other.max_x),
            max_y=max(self.max_y, other.max_y)
        )


@dataclass
class AttributeInfo:
    """속성 정보를 담는 데이터 클래스"""
    tag: str
    text: str
    position: Tuple[float, float, float]
    height: float
    rotation: float
    layer: str
    prompt: Optional[str] = None
    style: Optional[str] = None
    invisible: bool = False
    const: bool = False
    bounding_box: Optional[BoundingBox] = None
    entity_handle: Optional[str] = None
    
    # 좌표 정보
    insert_x: float = 0.0
    insert_y: float = 0.0
    insert_z: float = 0.0


@dataclass
class BlockInfo:
    """블록 정보를 담는 데이터 클래스"""
    name: str
    position: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    rotation: float
    layer: str
    attributes: List[AttributeInfo]
    bounding_box: Optional[BoundingBox] = None


@dataclass
class TitleBlockInfo:
    """도곽 정보를 담는 데이터 클래스"""
    drawing_name: Optional[str] = None
    drawing_number: Optional[str] = None
    construction_field: Optional[str] = None
    construction_stage: Optional[str] = None
    scale: Optional[str] = None
    project_name: Optional[str] = None
    designer: Optional[str] = None
    date: Optional[str] = None
    revision: Optional[str] = None
    location: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    block_name: Optional[str] = None
    
    # 모든 attributes 정보 저장
    all_attributes: List[AttributeInfo] = field(default_factory=list)
    attributes_count: int = 0
    
    def __post_init__(self):
        """초기화 후 처리"""
        self.attributes_count = len(self.all_attributes)


class FixedDXFProcessor:
    """수정된 DXF 파일 처리기 - 속성 추출 문제 해결"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 도곽 식별을 위한 키워드 (한국어/영어)
        self.title_block_keywords = {
            '도면명': ['도면명', '도면', 'drawing', 'title', 'name', 'dwg'],
            '도면번호': ['도면번호', '번호', 'number', 'no', 'dwg_no'],
            '건설분야': ['건설분야', '분야', 'field', 'construction', 'civil'],
            '건설단계': ['건설단계', '단계', 'stage', 'phase', 'step'],
            '축척': ['축척', 'scale', 'ratio'],
            '설계자': ['설계자', '설계', 'designer', 'design', 'engineer'],
            '프로젝트': ['프로젝트', '사업', 'project', 'work'],
            '날짜': ['날짜', '일자', 'date', 'time'],
            '리비전': ['리비전', '개정', 'revision', 'rev'],
            '위치': ['위치', '장소', 'location', 'place', 'site']
        }
        
        if not EZDXF_AVAILABLE:
            self.logger.warning("ezdxf 라이브러리가 설치되지 않았습니다.")
    
    def validate_dxf_file(self, file_path: str) -> bool:
        """DXF 파일 유효성 검사"""
        if not EZDXF_AVAILABLE:
            self.logger.error("ezdxf 라이브러리가 설치되지 않음")
            return False
            
        if not os.path.exists(file_path):
            self.logger.error(f"DXF 파일이 존재하지 않음: {file_path}")
            return False
            
        if not file_path.lower().endswith('.dxf'):
            self.logger.error(f"DXF 파일이 아님: {file_path}")
            return False
            
        try:
            # 파일 열기 시도
            doc = ezdxf.readfile(file_path)
            self.logger.info(f"DXF 파일 유효성 검사 통과: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"DXF 파일 유효성 검사 실패: {e}")
            return False
    
    def load_dxf_document(self, file_path: str) -> Optional[Drawing]:
        """DXF 문서 로드"""
        try:
            doc = ezdxf.readfile(file_path)
            self.logger.info(f"DXF 문서 로드 성공: {file_path}")
            return doc
        except Exception as e:
            self.logger.error(f"DXF 문서 로드 실패: {e}")
            return None
    
    def extract_all_insert_attributes(self, doc: Drawing) -> List[BlockInfo]:
        """모든 INSERT 엔티티에서 속성 추출 - 수정된 로직"""
        block_refs = []
        
        try:
            # 모델스페이스에서 INSERT 엔티티 검색
            msp = doc.modelspace()
            inserts = msp.query('INSERT')
            
            self.logger.info(f"모델스페이스에서 {len(inserts)}개의 INSERT 엔티티 발견")
            
            for insert in inserts:
                block_info = self._process_insert_entity(insert, doc)
                if block_info:
                    block_refs.append(block_info)
            
            # 페이퍼스페이스에서도 검색
            for layout in doc.layouts:
                if layout.is_any_paperspace:
                    inserts = layout.query('INSERT')
                    self.logger.info(f"페이퍼스페이스 '{layout.name}'에서 {len(inserts)}개의 INSERT 엔티티 발견")
                    
                    for insert in inserts:
                        block_info = self._process_insert_entity(insert, doc)
                        if block_info:
                            block_refs.append(block_info)
            
            self.logger.info(f"총 {len(block_refs)}개의 블록 참조 처리 완료")
            return block_refs
            
        except Exception as e:
            self.logger.error(f"INSERT 속성 추출 중 오류: {e}")
            return []
    
    def _process_insert_entity(self, insert: Insert, doc: Drawing) -> Optional[BlockInfo]:
        """개별 INSERT 엔티티 처리 - 향상된 속성 추출"""
        try:
            attributes = []
            
            # 방법 1: INSERT에 연결된 ATTRIB 엔티티들 추출
            self.logger.debug(f"INSERT '{insert.dxf.name}'의 연결된 속성 추출 중...")
            
            # insert.attribs는 리스트를 반환
            insert_attribs = insert.attribs
            self.logger.debug(f"INSERT.attribs: {len(insert_attribs)}개 발견")
            
            for attrib in insert_attribs:
                attr_info = self._extract_attrib_info(attrib)
                if attr_info:
                    attributes.append(attr_info)
                    self.logger.debug(f"ATTRIB 추출: tag='{attr_info.tag}', text='{attr_info.text}'")
            
            # 방법 2: 블록 정의에서 ATTDEF 정보 추출 (search_const=True와 유사한 효과)
            try:
                block_layout = doc.blocks.get(insert.dxf.name)
                if block_layout:
                    # 블록 정의에서 ATTDEF 엔티티 검색
                    attdefs = block_layout.query('ATTDEF')
                    self.logger.debug(f"블록 정의에서 {len(attdefs)}개의 ATTDEF 발견")
                    
                    for attdef in attdefs:
                        # ATTDEF에서 기본값이나 상수 값 추출
                        if hasattr(attdef.dxf, 'text') and attdef.dxf.text.strip():
                            attr_info = self._extract_attdef_info(attdef, insert)
                            if attr_info:
                                # 중복 체크 (같은 tag가 이미 있으면 건너뛰기)
                                existing_tags = [attr.tag for attr in attributes]
                                if attr_info.tag not in existing_tags:
                                    attributes.append(attr_info)
                                    self.logger.debug(f"ATTDEF 추출: tag='{attr_info.tag}', text='{attr_info.text}'")
                    
                    # 방법 3: 블록 내부의 TEXT/MTEXT 엔티티도 추출
                    text_entities = block_layout.query('TEXT MTEXT')
                    self.logger.debug(f"블록 정의에서 {len(text_entities)}개의 TEXT/MTEXT 발견")
                    
                    for text_entity in text_entities:
                        attr_info = self._extract_text_as_attribute(text_entity, insert)
                        if attr_info:
                            attributes.append(attr_info)
                            self.logger.debug(f"TEXT 추출: text='{attr_info.text}'")
                            
            except Exception as e:
                self.logger.warning(f"블록 정의 처리 중 오류: {e}")
            
            # 방법 4: get_attrib_text 메서드를 사용한 확인
            try:
                # 일반적인 속성 태그들로 시도
                common_tags = ['TITLE', 'NAME', 'NUMBER', 'DATE', 'SCALE', 'DESIGNER', 
                              'PROJECT', 'DRAWING', 'DWG_NO', 'REV', 'REVISION']
                
                for tag in common_tags:
                    try:
                        # search_const=True로 ATTDEF도 검색
                        text_value = insert.get_attrib_text(tag, search_const=True)
                        if text_value and text_value.strip():
                            # 이미 있는 태그인지 확인
                            existing_tags = [attr.tag for attr in attributes]
                            if tag not in existing_tags:
                                attr_info = AttributeInfo(
                                    tag=tag,
                                    text=text_value.strip(),
                                    position=insert.dxf.insert,
                                    height=12.0,  # 기본값
                                    rotation=insert.dxf.rotation,
                                    layer=insert.dxf.layer,
                                    insert_x=insert.dxf.insert[0],
                                    insert_y=insert.dxf.insert[1],
                                    insert_z=insert.dxf.insert[2] if len(insert.dxf.insert) > 2 else 0.0
                                )
                                attributes.append(attr_info)
                                self.logger.debug(f"get_attrib_text 추출: tag='{tag}', text='{text_value.strip()}'")
                    except:
                        continue
                        
            except Exception as e:
                self.logger.warning(f"get_attrib_text 처리 중 오류: {e}")
            
            # BlockInfo 생성
            if attributes or True:  # 속성이 없어도 블록 정보는 수집
                block_info = BlockInfo(
                    name=insert.dxf.name,
                    position=insert.dxf.insert,
                    scale=(insert.dxf.xscale, insert.dxf.yscale, insert.dxf.zscale),
                    rotation=insert.dxf.rotation,
                    layer=insert.dxf.layer,
                    attributes=attributes
                )
                
                self.logger.info(f"INSERT '{insert.dxf.name}' 처리 완료: {len(attributes)}개 속성")
                return block_info
            
            return None
            
        except Exception as e:
            self.logger.error(f"INSERT 엔티티 처리 중 오류: {e}")
            return None
    
    def _extract_attrib_info(self, attrib: Attrib) -> Optional[AttributeInfo]:
        """ATTRIB 엔티티에서 속성 정보 추출"""
        try:
            # 텍스트가 비어있으면 건너뛰기
            text_value = attrib.dxf.text.strip()
            if not text_value:
                return None
            
            attr_info = AttributeInfo(
                tag=attrib.dxf.tag,
                text=text_value,
                position=attrib.dxf.insert,
                height=getattr(attrib.dxf, 'height', 12.0),
                rotation=getattr(attrib.dxf, 'rotation', 0.0),
                layer=getattr(attrib.dxf, 'layer', '0'),
                style=getattr(attrib.dxf, 'style', None),
                invisible=getattr(attrib, 'is_invisible', False),
                const=getattr(attrib, 'is_const', False),
                entity_handle=attrib.dxf.handle,
                insert_x=attrib.dxf.insert[0],
                insert_y=attrib.dxf.insert[1],
                insert_z=attrib.dxf.insert[2] if len(attrib.dxf.insert) > 2 else 0.0
            )
            
            return attr_info
            
        except Exception as e:
            self.logger.warning(f"ATTRIB 정보 추출 중 오류: {e}")
            return None
    
    def _extract_attdef_info(self, attdef: AttDef, insert: Insert) -> Optional[AttributeInfo]:
        """ATTDEF 엔티티에서 속성 정보 추출"""
        try:
            # 텍스트가 비어있으면 건너뛰기
            text_value = attdef.dxf.text.strip()
            if not text_value:
                return None
            
            # INSERT의 위치를 기준으로 실제 위치 계산
            actual_position = (
                insert.dxf.insert[0] + attdef.dxf.insert[0] * insert.dxf.xscale,
                insert.dxf.insert[1] + attdef.dxf.insert[1] * insert.dxf.yscale,
                insert.dxf.insert[2] + (attdef.dxf.insert[2] if len(attdef.dxf.insert) > 2 else 0.0)
            )
            
            attr_info = AttributeInfo(
                tag=attdef.dxf.tag,
                text=text_value,
                position=actual_position,
                height=getattr(attdef.dxf, 'height', 12.0),
                rotation=getattr(attdef.dxf, 'rotation', 0.0) + insert.dxf.rotation,
                layer=getattr(attdef.dxf, 'layer', insert.dxf.layer),
                prompt=getattr(attdef.dxf, 'prompt', None),
                style=getattr(attdef.dxf, 'style', None),
                invisible=getattr(attdef, 'is_invisible', False),
                const=getattr(attdef, 'is_const', False),
                entity_handle=attdef.dxf.handle,
                insert_x=actual_position[0],
                insert_y=actual_position[1],
                insert_z=actual_position[2]
            )
            
            return attr_info
            
        except Exception as e:
            self.logger.warning(f"ATTDEF 정보 추출 중 오류: {e}")
            return None
    
    def _extract_text_as_attribute(self, text_entity, insert: Insert) -> Optional[AttributeInfo]:
        """TEXT/MTEXT 엔티티를 속성으로 추출"""
        try:
            # 텍스트 내용 추출
            if hasattr(text_entity, 'text'):
                text_value = text_entity.text.strip()
            elif hasattr(text_entity.dxf, 'text'):
                text_value = text_entity.dxf.text.strip()
            else:
                return None
            
            if not text_value:
                return None
            
            # INSERT의 위치를 기준으로 실제 위치 계산
            text_pos = text_entity.dxf.insert
            actual_position = (
                insert.dxf.insert[0] + text_pos[0] * insert.dxf.xscale,
                insert.dxf.insert[1] + text_pos[1] * insert.dxf.yscale,
                insert.dxf.insert[2] + (text_pos[2] if len(text_pos) > 2 else 0.0)
            )
            
            # 태그는 텍스트 내용의 첫 단어나 전체 내용으로 설정
            tag = text_value.split()[0] if ' ' in text_value else text_value[:20]
            
            attr_info = AttributeInfo(
                tag=f"TEXT_{tag}",
                text=text_value,
                position=actual_position,
                height=getattr(text_entity.dxf, 'height', 12.0),
                rotation=getattr(text_entity.dxf, 'rotation', 0.0) + insert.dxf.rotation,
                layer=getattr(text_entity.dxf, 'layer', insert.dxf.layer),
                style=getattr(text_entity.dxf, 'style', None),
                entity_handle=text_entity.dxf.handle,
                insert_x=actual_position[0],
                insert_y=actual_position[1],
                insert_z=actual_position[2]
            )
            
            return attr_info
            
        except Exception as e:
            self.logger.warning(f"TEXT 엔티티 추출 중 오류: {e}")
            return None
    
    def identify_title_block(self, block_refs: List[BlockInfo]) -> Optional[TitleBlockInfo]:
        """도곽 블록 식별 및 정보 추출"""
        if not block_refs:
            return None
        
        title_block_candidates = []
        
        # 각 블록 참조에 대해 도곽 가능성 점수 계산
        for block_ref in block_refs:
            score = self._calculate_title_block_score(block_ref)
            if score > 0:
                title_block_candidates.append((block_ref, score))
        
        if not title_block_candidates:
            self.logger.warning("도곽 블록을 찾을 수 없습니다.")
            return None
        
        # 가장 높은 점수의 블록을 도곽으로 선택
        title_block_candidates.sort(key=lambda x: x[1], reverse=True)
        best_candidate = title_block_candidates[0][0]
        
        self.logger.info(f"도곽 블록 식별: '{best_candidate.name}' (점수: {title_block_candidates[0][1]})")
        
        # TitleBlockInfo 생성
        title_block = TitleBlockInfo(
            block_name=best_candidate.name,
            all_attributes=best_candidate.attributes
        )
        
        # 속성들을 분류하여 해당 필드에 할당
        for attr in best_candidate.attributes:
            self._assign_attribute_to_field(title_block, attr)
        
        title_block.attributes_count = len(best_candidate.attributes)
        
        return title_block
    
    def _calculate_title_block_score(self, block_ref: BlockInfo) -> int:
        """블록이 도곽일 가능성 점수 계산"""
        score = 0
        
        # 블록 이름에 도곽 관련 키워드가 있는지 확인
        name_lower = block_ref.name.lower()
        title_keywords = ['title', 'titleblock', 'title_block', '도곽', '타이틀', 'border', 'frame']
        
        for keyword in title_keywords:
            if keyword in name_lower:
                score += 10
                break
        
        # 속성 개수 (도곽은 보통 많은 속성을 가짐)
        if len(block_ref.attributes) >= 5:
            score += 5
        elif len(block_ref.attributes) >= 3:
            score += 3
        elif len(block_ref.attributes) >= 1:
            score += 1
        
        # 도곽 관련 속성이 있는지 확인
        for attr in block_ref.attributes:
            for field_name, keywords in self.title_block_keywords.items():
                if self._contains_any_keyword(attr.tag.lower(), keywords) or \
                   self._contains_any_keyword(attr.text.lower(), keywords):
                    score += 2
        
        return score
    
    def _contains_any_keyword(self, text: str, keywords: List[str]) -> bool:
        """텍스트에 키워드 중 하나라도 포함되어 있는지 확인"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    def _assign_attribute_to_field(self, title_block: TitleBlockInfo, attr: AttributeInfo):
        """속성을 도곽 정보의 해당 필드에 할당"""
        attr_text = attr.text.strip()
        
        if not attr_text:
            return
        
        # 태그나 텍스트에서 키워드 매칭
        attr_tag_lower = attr.tag.lower()
        attr_text_lower = attr_text.lower()
        
        # 각 필드별로 키워드 매칭
        for field_name, keywords in self.title_block_keywords.items():
            if self._contains_any_keyword(attr_tag_lower, keywords) or \
               self._contains_any_keyword(attr_text_lower, keywords):
                
                if field_name == '도면명' and not title_block.drawing_name:
                    title_block.drawing_name = attr_text
                elif field_name == '도면번호' and not title_block.drawing_number:
                    title_block.drawing_number = attr_text
                elif field_name == '건설분야' and not title_block.construction_field:
                    title_block.construction_field = attr_text
                elif field_name == '건설단계' and not title_block.construction_stage:
                    title_block.construction_stage = attr_text
                elif field_name == '축척' and not title_block.scale:
                    title_block.scale = attr_text
                elif field_name == '설계자' and not title_block.designer:
                    title_block.designer = attr_text
                elif field_name == '프로젝트' and not title_block.project_name:
                    title_block.project_name = attr_text
                elif field_name == '날짜' and not title_block.date:
                    title_block.date = attr_text
                elif field_name == '리비전' and not title_block.revision:
                    title_block.revision = attr_text
                elif field_name == '위치' and not title_block.location:
                    title_block.location = attr_text
                break
    
    def process_dxf_file_comprehensive(self, file_path: str) -> Dict[str, Any]:
        """DXF 파일 종합적인 처리 - 수정된 버전"""
        result = {
            'success': False,
            'error': None,
            'file_path': file_path,
            'title_block': None,
            'block_references': [],
            'summary': {}
        }
        
        try:
            # 파일 유효성 검사
            if not self.validate_dxf_file(file_path):
                result['error'] = "유효하지 않은 DXF 파일입니다."
                return result
            
            # DXF 문서 로드
            doc = self.load_dxf_document(file_path)
            if not doc:
                result['error'] = "DXF 문서를 로드할 수 없습니다."
                return result
            
            # 모든 INSERT 엔티티에서 속성 추출
            self.logger.info("INSERT 엔티티 속성 추출 중...")
            block_references = self.extract_all_insert_attributes(doc)
            
            # 도곽 정보 추출
            self.logger.info("도곽 정보 추출 중...")
            title_block = self.identify_title_block(block_references)
            
            # 요약 정보 생성
            total_attributes = sum(len(br.attributes) for br in block_references)
            non_empty_attributes = sum(len([attr for attr in br.attributes if attr.text.strip()]) 
                                     for br in block_references)
            
            summary = {
                'total_blocks': len(block_references),
                'title_block_found': title_block is not None,
                'title_block_name': title_block.block_name if title_block else None,
                'attributes_count': title_block.attributes_count if title_block else 0,
                'total_attributes': total_attributes,
                'non_empty_attributes': non_empty_attributes
            }
            
            # 결과 설정
            result['title_block'] = asdict(title_block) if title_block else None
            result['block_references'] = [asdict(br) for br in block_references]
            result['summary'] = summary
            result['success'] = True
            
            self.logger.info(f"DXF 파일 처리 완료: {file_path}")
            self.logger.info(f"처리 요약: 블록 {len(block_references)}개, 속성 {total_attributes}개 (비어있지 않은 속성: {non_empty_attributes}개)")
            
        except Exception as e:
            self.logger.error(f"DXF 파일 처리 중 오류: {e}")
            result['error'] = str(e)
        
        return result


# 기존 클래스명과의 호환성을 위한 별칭
DXFProcessor = FixedDXFProcessor


def main():
    """테스트용 메인 함수"""
    logging.basicConfig(level=logging.DEBUG)
    
    if not EZDXF_AVAILABLE:
        print("ezdxf 라이브러리가 설치되지 않았습니다.")
        return
    
    processor = FixedDXFProcessor()
    
    # 업로드 폴더에서 DXF 파일 찾기
    upload_dir = "uploads"
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            if file.lower().endswith('.dxf'):
                test_file = os.path.join(upload_dir, file)
                print(f"\n테스트 파일: {test_file}")
                
                result = processor.process_dxf_file_comprehensive(test_file)
                
                if result['success']:
                    print("✅ DXF 파일 처리 성공!")
                    summary = result['summary']
                    print(f"   블록 수: {summary['total_blocks']}")
                    print(f"   도곽 발견: {summary['title_block_found']}")
                    print(f"   도곽 속성 수: {summary['attributes_count']}")
                    print(f"   전체 속성 수: {summary['total_attributes']}")
                    print(f"   비어있지 않은 속성 수: {summary['non_empty_attributes']}")
                    
                    if summary['title_block_name']:
                        print(f"   도곽 블록명: {summary['title_block_name']}")
                else:
                    print(f"❌ 처리 실패: {result['error']}")
                
                break
    else:
        print("uploads 폴더를 찾을 수 없습니다.")


if __name__ == "__main__":
    main()
