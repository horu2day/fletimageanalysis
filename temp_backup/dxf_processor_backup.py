# -*- coding: utf-8 -*-
"""
DXF 파일 처리 모듈
ezdxf 라이브러리를 사용하여 DXF 파일에서 도곽 정보 및 Block Reference/Attribute Reference를 추출
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict, field

try:
    import ezdxf
    from ezdxf.document import Drawing
    from ezdxf.entities import Insert, Attrib, AttDef, Text, MText
    from ezdxf.layouts import BlockLayout, Modelspace
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


@dataclass
class AttributeInfo:
    """속성 정보를 담는 데이터 클래스 - 모든 DXF 속성 포함"""
    tag: str
    text: str
    position: Tuple[float, float, float]  # insert point (x, y, z)
    height: float
    width: float
    rotation: float
    layer: str
    bounding_box: Optional[BoundingBox] = None
    
    # 추가 DXF 속성들
    prompt: Optional[str] = None          # 프롬프트 문자열 (ATTDEF에서 가져옴)
    style: Optional[str] = None           # 텍스트 스타일
    invisible: bool = False              # 보이지 않는 속성
    const: bool = False                  # 상수 속성
    verify: bool = False                 # 검증 필요
    preset: bool = False                 # 프롬프트 없이 삽입
    align_point: Optional[Tuple[float, float, float]] = None  # 정렬점
    halign: int = 0                      # 수평 정렬 (0=LEFT, 2=RIGHT, etc.)
    valign: int = 0                      # 수직 정렬 (0=BASELINE, 1=BOTTOM, etc.) 
    text_generation_flag: int = 0         # 텍스트 생성 플래그
    oblique_angle: float = 0.0           # 기울기 각도
    width_factor: float = 1.0            # 폭 비율
    color: Optional[int] = None          # 색상 코드
    linetype: Optional[str] = None       # 선 타입
    lineweight: Optional[int] = None     # 선 굵기
    
    # 좌표 정보
    insert_x: float = 0.0                # X 좌표
    insert_y: float = 0.0                # Y 좌표
    insert_z: float = 0.0                # Z 좌표
    
    # 계산된 정보
    estimated_width: float = 0.0         # 추정 텍스트 폭
    entity_handle: Optional[str] = None   # DXF 엔티티 핸들


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
    drawing_name: Optional[str] = None          # 도면명
    drawing_number: Optional[str] = None        # 도면번호
    construction_field: Optional[str] = None    # 건설분야
    construction_stage: Optional[str] = None    # 건설단계
    scale: Optional[str] = None                 # 축척
    project_name: Optional[str] = None          # 프로젝트명
    designer: Optional[str] = None              # 설계자
    date: Optional[str] = None                  # 날짜
    revision: Optional[str] = None              # 리비전
    location: Optional[str] = None              # 위치
    bounding_box: Optional[BoundingBox] = None  # 도곽 전체 바운딩 박스
    block_name: Optional[str] = None            # 도곽 블록 이름
    
    # 모든 attributes 정보 저장
    all_attributes: List[AttributeInfo] = field(default_factory=list)  # 도곽의 모든 속성 정보 리스트
    attributes_count: int = 0                   # 속성 개수
    
    # 추가 메타데이터
    block_position: Optional[Tuple[float, float, float]] = None  # 블록 위치
    block_scale: Optional[Tuple[float, float, float]] = None     # 블록 스케일
    block_rotation: float = 0.0                                  # 블록 회전각
    block_layer: Optional[str] = None                            # 블록 레이어
    
    def __post_init__(self):
        """초기화 후 처리"""
        self.attributes_count = len(self.all_attributes)


class DXFProcessor:
    """DXF 파일 처리 클래스"""
    
    # 도곽 식별을 위한 키워드 정의
    TITLE_BLOCK_KEYWORDS = {
        '건설분야': ['construction_field', 'field', '분야', '공사', 'category'],
        '건설단계': ['construction_stage', 'stage', '단계', 'phase'],
        '도면명': ['drawing_name', 'title', '제목', 'name', '명'],
        '축척': ['scale', '축척', 'ratio', '비율'],
        '도면번호': ['drawing_number', 'number', '번호', 'no', 'dwg'],
        '설계자': ['designer', '설계', 'design', 'drawn'],
        '프로젝트': ['project', '사업', '공사명'],
        '날짜': ['date', '일자', '작성일'],
        '리비전': ['revision', 'rev', '개정'],
        '위치': ['location', '위치', '지역']
    }
    
    def __init__(self):
        """DXF 처리기 초기화"""
        self.logger = logging.getLogger(__name__)
        
        if not EZDXF_AVAILABLE:
            raise ImportError("ezdxf 라이브러리가 필요합니다. 'pip install ezdxf'로 설치하세요.")
    
    def validate_dxf_file(self, file_path: str) -> bool:
        """DXF 파일 유효성 검사"""
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"파일이 존재하지 않습니다: {file_path}")
                return False
            
            if not file_path.lower().endswith('.dxf'):
                self.logger.error(f"DXF 파일이 아닙니다: {file_path}")
                return False
            
            # ezdxf로 파일 읽기 시도
            doc = ezdxf.readfile(file_path)
            if doc is None:
                return False
                
            self.logger.info(f"DXF 파일 유효성 검사 성공: {file_path}")
            return True
            
        except ezdxf.DXFStructureError as e:
            self.logger.error(f"DXF 구조 오류: {e}")
            return False
        except Exception as e:
            self.logger.error(f"DXF 파일 검증 중 오류: {e}")
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
    
    def calculate_text_bounding_box(self, entity: Union[Text, MText, Attrib]) -> Optional[BoundingBox]:
        """텍스트 엔티티의 바운딩 박스 계산"""
        try:
            if hasattr(entity, 'dxf'):
                # 텍스트 위치 가져오기
                insert_point = getattr(entity.dxf, 'insert', (0, 0, 0))
                height = getattr(entity.dxf, 'height', 1.0)
                
                # 텍스트 내용 길이 추정 (폰트에 따라 다르지만 대략적으로)
                text_content = ""
                if hasattr(entity.dxf, 'text'):
                    text_content = entity.dxf.text
                elif hasattr(entity, 'plain_text'):
                    text_content = entity.plain_text()
                
                # 텍스트 너비 추정 (높이의 0.6배 * 글자 수)
                estimated_width = len(text_content) * height * 0.6
                
                # 회전 고려 (기본값)
                rotation = getattr(entity.dxf, 'rotation', 0)
                
                # 바운딩 박스 계산
                x, y = insert_point[0], insert_point[1]
                
                return BoundingBox(
                    min_x=x,
                    min_y=y,
                    max_x=x + estimated_width,
                    max_y=y + height
                )
        except Exception as e:
            self.logger.warning(f"텍스트 바운딩 박스 계산 실패: {e}")
            return None
    
    def extract_block_references(self, doc: Drawing) -> List[BlockInfo]:
        """문서에서 모든 Block Reference 추출"""
        block_refs = []
        
        try:
            # 모델스페이스에서 INSERT 엔티티 찾기
            msp = doc.modelspace()
            
            for insert in msp.query('INSERT'):
                block_info = self._process_block_reference(doc, insert)
                if block_info:
                    block_refs.append(block_info)
            
            # 페이퍼스페이스도 확인
            for layout_name in doc.layout_names_in_taborder():
                if layout_name.startswith('*'):  # 모델스페이스 제외
                    continue
                try:
                    layout = doc.paperspace(layout_name)
                    for insert in layout.query('INSERT'):
                        block_info = self._process_block_reference(doc, insert)
                        if block_info:
                            block_refs.append(block_info)
                except Exception as e:
                    self.logger.warning(f"레이아웃 {layout_name} 처리 중 오류: {e}")
            
            self.logger.info(f"총 {len(block_refs)}개의 블록 참조를 찾았습니다.")
            return block_refs
            
        except Exception as e:
            self.logger.error(f"블록 참조 추출 중 오류: {e}")
            return []
    
    def _process_block_reference(self, doc: Drawing, insert: Insert) -> Optional[BlockInfo]:
        """개별 Block Reference 처리 - ATTDEF 정보도 함께 수집"""
        try:
            # 블록 정보 추출
            block_name = insert.dxf.name
            position = (insert.dxf.insert.x, insert.dxf.insert.y, insert.dxf.insert.z)
            scale = (
                getattr(insert.dxf, 'xscale', 1.0),
                getattr(insert.dxf, 'yscale', 1.0), 
                getattr(insert.dxf, 'zscale', 1.0)
            )
            rotation = getattr(insert.dxf, 'rotation', 0.0)
            layer = getattr(insert.dxf, 'layer', '0')
            
            # ATTDEF 정보 수집 (프롬프트 정보 포함)
            attdef_info = {}
            try:
                block_layout = doc.blocks.get(block_name)
                if block_layout:
                    for attdef in block_layout.query('ATTDEF'):
                        tag = getattr(attdef.dxf, 'tag', '')
                        prompt = getattr(attdef.dxf, 'prompt', '')
                        if tag:
                            attdef_info[tag] = {
                                'prompt': prompt,
                                'default_text': getattr(attdef.dxf, 'text', ''),
                                'position': (attdef.dxf.insert.x, attdef.dxf.insert.y, attdef.dxf.insert.z),
                                'height': getattr(attdef.dxf, 'height', 1.0),
                                'style': getattr(attdef.dxf, 'style', 'Standard'),
                                'invisible': getattr(attdef.dxf, 'invisible', False),
                                'const': getattr(attdef.dxf, 'const', False),
                                'verify': getattr(attdef.dxf, 'verify', False),
                                'preset': getattr(attdef.dxf, 'preset', False)
                            }
            except Exception as e:
                self.logger.debug(f"ATTDEF 정보 수집 실패: {e}")
            
            # ATTRIB 속성 추출 및 ATTDEF 정보와 결합
            attributes = []
            for attrib in insert.attribs:
                attr_info = self._extract_attribute_info(attrib)
                if attr_info and attr_info.tag in attdef_info:
                    # ATTDEF에서 프롬프트 정보 추가
                    attr_info.prompt = attdef_info[attr_info.tag]['prompt']
                
                if attr_info:
                    attributes.append(attr_info)
            
            return BlockInfo(
                name=block_name,
                position=position,
                scale=scale,
                rotation=rotation,
                layer=layer,
                attributes=attributes
            )
            
        except Exception as e:
            self.logger.warning(f"블록 참조 처리 중 오류: {e}")
            return None
    
    def _extract_attribute_info(self, attrib: Attrib) -> Optional[AttributeInfo]:
        """Attribute Reference에서 모든 정보 추출"""
        try:
            # 기본 속성
            tag = getattr(attrib.dxf, 'tag', '')
            text = getattr(attrib.dxf, 'text', '')
            
            # 위치 정보
            insert_point = getattr(attrib.dxf, 'insert', (0, 0, 0))
            position = (insert_point.x if hasattr(insert_point, 'x') else insert_point[0],
                       insert_point.y if hasattr(insert_point, 'y') else insert_point[1],
                       insert_point.z if hasattr(insert_point, 'z') else insert_point[2])
            
            # 텍스트 속성
            height = getattr(attrib.dxf, 'height', 1.0)
            width = getattr(attrib.dxf, 'width', 1.0)
            rotation = getattr(attrib.dxf, 'rotation', 0.0)
            
            # 레이어 및 스타일
            layer = getattr(attrib.dxf, 'layer', '0')
            style = getattr(attrib.dxf, 'style', 'Standard')
            
            # 속성 플래그
            invisible = getattr(attrib.dxf, 'invisible', False)
            const = getattr(attrib.dxf, 'const', False)
            verify = getattr(attrib.dxf, 'verify', False)
            preset = getattr(attrib.dxf, 'preset', False)
            
            # 정렬 정보
            align_point_data = getattr(attrib.dxf, 'align_point', None)
            align_point = None
            if align_point_data:
                align_point = (align_point_data.x if hasattr(align_point_data, 'x') else align_point_data[0],
                             align_point_data.y if hasattr(align_point_data, 'y') else align_point_data[1],
                             align_point_data.z if hasattr(align_point_data, 'z') else align_point_data[2])
            
            halign = getattr(attrib.dxf, 'halign', 0)
            valign = getattr(attrib.dxf, 'valign', 0)
            
            # 텍스트 형식
            text_generation_flag = getattr(attrib.dxf, 'text_generation_flag', 0)
            oblique_angle = getattr(attrib.dxf, 'oblique_angle', 0.0)
            width_factor = getattr(attrib.dxf, 'width_factor', 1.0)
            
            # 시각적 속성
            color = getattr(attrib.dxf, 'color', None)
            linetype = getattr(attrib.dxf, 'linetype', None)
            lineweight = getattr(attrib.dxf, 'lineweight', None)
            
            # 엔티티 핸들
            entity_handle = getattr(attrib.dxf, 'handle', None)
            
            # 텍스트 폭 추정 (높이의 0.6배 * 글자 수)
            estimated_width = len(text) * height * 0.6 * width_factor
            
            # 바운딩 박스 계산
            bounding_box = self.calculate_text_bounding_box(attrib)
            
            # 프롬프트 정보는 ATTDEF에서 가져와야 함 (필요시 별도 처리)
            prompt = None
            
            return AttributeInfo(
                tag=tag,
                text=text,
                position=position,
                height=height,
                width=width,
                rotation=rotation,
                layer=layer,
                bounding_box=bounding_box,
                prompt=prompt,
                style=style,
                invisible=invisible,
                const=const,
                verify=verify,
                preset=preset,
                align_point=align_point,
                halign=halign,
                valign=valign,
                text_generation_flag=text_generation_flag,
                oblique_angle=oblique_angle,
                width_factor=width_factor,
                color=color,
                linetype=linetype,
                lineweight=lineweight,
                insert_x=position[0],
                insert_y=position[1],
                insert_z=position[2],
                estimated_width=estimated_width,
                entity_handle=entity_handle
            )
            
        except Exception as e:
            self.logger.warning(f"속성 정보 추출 중 오류: {e}")
            return None
    
    def identify_title_block(self, block_refs: List[BlockInfo]) -> Optional[TitleBlockInfo]:
        """블록 참조들 중에서 도곽을 식별하고 정보 추출"""
        title_block_candidates = []
        
        for block_ref in block_refs:
            # 도곽 키워드를 포함한 속성이 있는지 확인
            keyword_matches = 0
            
            for attr in block_ref.attributes:
                for keyword_group in self.TITLE_BLOCK_KEYWORDS.keys():
                    if self._contains_keyword(attr.tag, keyword_group) or \
                       self._contains_keyword(attr.text, keyword_group):
                        keyword_matches += 1
                        break
            
            # 충분한 키워드가 매칭되면 도곽 후보로 추가
            if keyword_matches >= 2:  # 최소 2개 이상의 키워드 매칭
                title_block_candidates.append((block_ref, keyword_matches))
        
        if not title_block_candidates:
            self.logger.warning("도곽 블록을 찾을 수 없습니다.")
            return None
        
        # 가장 많은 키워드를 포함한 블록을 도곽으로 선택
        title_block_candidates.sort(key=lambda x: x[1], reverse=True)
        best_candidate = title_block_candidates[0][0]
        
        self.logger.info(f"도곽 블록 발견: {best_candidate.name} (키워드 매칭: {title_block_candidates[0][1]})")
        
        return self._extract_title_block_info(best_candidate)
    
    def _contains_keyword(self, text: str, keyword_group: str) -> bool:
        """텍스트에 특정 키워드 그룹의 단어가 포함되어 있는지 확인"""
        if not text:
            return False
        
        text_lower = text.lower()
        keywords = self.TITLE_BLOCK_KEYWORDS.get(keyword_group, [])
        
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    def _extract_title_block_info(self, block_ref: BlockInfo) -> TitleBlockInfo:
        """도곽 블록에서 상세 정보 추출 - 모든 attributes 정보 포함"""
        # TitleBlockInfo 객체 생성
        title_block = TitleBlockInfo(
            block_name=block_ref.name,
            all_attributes=block_ref.attributes.copy(),  # 모든 attributes 정보 저장
            block_position=block_ref.position,
            block_scale=block_ref.scale,
            block_rotation=block_ref.rotation,
            block_layer=block_ref.layer
        )
        
        # 속성들을 분석하여 도곽 정보 매핑
        for attr in block_ref.attributes:
            tag_lower = attr.tag.lower()
            text_value = attr.text.strip()
            
            if not text_value:
                continue
            
            # 각 키워드 그룹별로 매칭 시도
            if self._contains_keyword(attr.tag, '도면명') or self._contains_keyword(attr.text, '도면명'):
                title_block.drawing_name = text_value
            elif self._contains_keyword(attr.tag, '도면번호') or self._contains_keyword(attr.text, '도면번호'):
                title_block.drawing_number = text_value
            elif self._contains_keyword(attr.tag, '건설분야') or self._contains_keyword(attr.text, '건설분야'):
                title_block.construction_field = text_value
            elif self._contains_keyword(attr.tag, '건설단계') or self._contains_keyword(attr.text, '건설단계'):
                title_block.construction_stage = text_value
            elif self._contains_keyword(attr.tag, '축척') or self._contains_keyword(attr.text, '축척'):
                title_block.scale = text_value
            elif self._contains_keyword(attr.tag, '설계자') or self._contains_keyword(attr.text, '설계자'):
                title_block.designer = text_value
            elif self._contains_keyword(attr.tag, '프로젝트') or self._contains_keyword(attr.text, '프로젝트'):
                title_block.project_name = text_value
            elif self._contains_keyword(attr.tag, '날짜') or self._contains_keyword(attr.text, '날짜'):
                title_block.date = text_value
            elif self._contains_keyword(attr.tag, '리비전') or self._contains_keyword(attr.text, '리비전'):
                title_block.revision = text_value
            elif self._contains_keyword(attr.tag, '위치') or self._contains_keyword(attr.text, '위치'):
                title_block.location = text_value
        
        # 도곽 전체 바운딩 박스 계산
        title_block.bounding_box = self._calculate_title_block_bounding_box(block_ref)
        
        # 속성 개수 업데이트
        title_block.attributes_count = len(title_block.all_attributes)
        
        # 디버깅 로그 - 모든 attributes 정보 출력
        self.logger.info(f"도곽 '{block_ref.name}'에서 {title_block.attributes_count}개의 속성 추출:")
        for i, attr in enumerate(title_block.all_attributes):
            self.logger.debug(f"  [{i+1}] Tag: '{attr.tag}', Text: '{attr.text}', "
                             f"Position: ({attr.insert_x:.2f}, {attr.insert_y:.2f}, {attr.insert_z:.2f}), "
                             f"Height: {attr.height:.2f}, Prompt: '{attr.prompt or 'N/A'}'")
        
        return title_block
    
    def _calculate_title_block_bounding_box(self, block_ref: BlockInfo) -> Optional[BoundingBox]:
        """도곽의 전체 바운딩 박스 계산"""
        try:
            valid_boxes = [attr.bounding_box for attr in block_ref.attributes 
                          if attr.bounding_box is not None]
            
            if not valid_boxes:
                self.logger.warning("유효한 바운딩 박스가 없습니다.")
                return None
            
            # 모든 바운딩 박스를 포함하는 최외곽 박스 계산
            min_x = min(box.min_x for box in valid_boxes)
            min_y = min(box.min_y for box in valid_boxes)
            max_x = max(box.max_x for box in valid_boxes)
            max_y = max(box.max_y for box in valid_boxes)
            
            return BoundingBox(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)
            
        except Exception as e:
            self.logger.warning(f"도곽 바운딩 박스 계산 실패: {e}")
            return None
    
    def process_dxf_file(self, file_path: str) -> Dict[str, Any]:
        """DXF 파일 전체 처리"""
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
            
            # Block Reference 추출
            block_refs = self.extract_block_references(doc)
            result['block_references'] = [asdict(block_ref) for block_ref in block_refs]
            
            # 도곽 정보 추출
            title_block = self.identify_title_block(block_refs)
            if title_block:
                result['title_block'] = asdict(title_block)
            
            # 요약 정보
            result['summary'] = {
                'total_blocks': len(block_refs),
                'title_block_found': title_block is not None,
                'title_block_name': title_block.block_name if title_block else None,
                'attributes_count': sum(len(br.attributes) for br in block_refs)
            }
            
            result['success'] = True
            self.logger.info(f"DXF 파일 처리 완료: {file_path}")
            
        except Exception as e:
            self.logger.error(f"DXF 파일 처리 중 오류: {e}")
            result['error'] = str(e)
        
        return result
    
    def save_analysis_result(self, result: Dict[str, Any], output_file: str) -> bool:
        """분석 결과를 JSON 파일로 저장"""
        try:
            os.makedirs(Config.RESULTS_FOLDER, exist_ok=True)
            output_path = os.path.join(Config.RESULTS_FOLDER, output_file)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"분석 결과 저장 완료: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"분석 결과 저장 실패: {e}")
            return False


def main():
    """테스트용 메인 함수"""
    logging.basicConfig(level=logging.INFO)
    
    if not EZDXF_AVAILABLE:
        print("ezdxf 라이브러리가 설치되지 않았습니다.")
        return
    
    processor = DXFProcessor()
    
    # 테스트 파일 경로 (실제 파일 경로로 변경 필요)
    test_file = "test_drawing.dxf"
    
    if os.path.exists(test_file):
        result = processor.process_dxf_file(test_file)
        
        if result['success']:
            print("DXF 파일 처리 성공!")
            print(f"블록 수: {result['summary']['total_blocks']}")
            print(f"도곽 발견: {result['summary']['title_block_found']}")
            
            if result['title_block']:
                print("\n도곽 정보:")
                title_block = result['title_block']
                for key, value in title_block.items():
                    if value and key != 'bounding_box':
                        print(f"  {key}: {value}")
        else:
            print(f"처리 실패: {result['error']}")
    else:
        print(f"테스트 파일을 찾을 수 없습니다: {test_file}")


if __name__ == "__main__":
    main()
