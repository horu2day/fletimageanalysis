# -*- coding: utf-8 -*-
"""
포괄적 텍스트 추출 모듈
DXF 파일에서 도곽 블록 외의 모든 텍스트 엔티티를 추출하여 표시 및 저장
- 모델스페이스의 독립적인 TEXT/MTEXT 엔티티
- 페이퍼스페이스의 독립적인 TEXT/MTEXT 엔티티  
- 모든 블록 내부의 TEXT/MTEXT 엔티티
- 블록 속성(ATTRIB) 중 도곽이 아닌 것들
"""

import os
import csv
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

try:
    import ezdxf
    from ezdxf.document import Drawing
    from ezdxf.entities import Insert, Attrib, AttDef, Text, MText
    from ezdxf.layouts import BlockLayout, Modelspace, Paperspace
    from ezdxf import bbox
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False
    logging.warning("ezdxf 라이브러리가 설치되지 않았습니다.")

from config import Config


@dataclass
class ComprehensiveTextEntity:
    """포괄적인 텍스트 엔티티 정보"""
    entity_type: str  # TEXT, MTEXT, ATTRIB
    text: str
    position_x: float
    position_y: float
    position_z: float
    height: float
    rotation: float
    layer: str
    color: Optional[int] = None
    style: Optional[str] = None
    entity_handle: Optional[str] = None
    
    # 위치 정보
    location_type: str = "Unknown"  # ModelSpace, PaperSpace, Block
    parent_block: Optional[str] = None
    layout_name: Optional[str] = None
    
    # 블록 속성 정보 (ATTRIB인 경우)
    attribute_tag: Optional[str] = None
    is_title_block_attribute: bool = False
    
    # 바운딩 박스
    bbox_min_x: Optional[float] = None
    bbox_min_y: Optional[float] = None
    bbox_max_x: Optional[float] = None
    bbox_max_y: Optional[float] = None
    
    # 추가 속성
    width_factor: float = 1.0
    oblique_angle: float = 0.0
    text_generation_flag: int = 0


@dataclass
class ComprehensiveExtractionResult:
    """포괄적인 텍스트 추출 결과"""
    all_text_entities: List[ComprehensiveTextEntity] = field(default_factory=list)
    modelspace_texts: List[ComprehensiveTextEntity] = field(default_factory=list)
    paperspace_texts: List[ComprehensiveTextEntity] = field(default_factory=list)
    block_texts: List[ComprehensiveTextEntity] = field(default_factory=list)
    non_title_block_attributes: List[ComprehensiveTextEntity] = field(default_factory=list)
    
    # 통계 정보
    total_count: int = 0
    by_type_count: Dict[str, int] = field(default_factory=dict)
    by_location_count: Dict[str, int] = field(default_factory=dict)
    by_layer_count: Dict[str, int] = field(default_factory=dict)


class ComprehensiveTextExtractor:
    """포괄적 텍스트 추출기"""
    
    # 도곽 블록 식별을 위한 키워드
    TITLE_BLOCK_KEYWORDS = {
        '건설분야', '건설단계', '도면명', '축척', '도면번호', '설계자', 
        '프로젝트', '날짜', '리비전', '위치', 'title', 'scale', 'drawing',
        'project', 'designer', 'date', 'revision', 'dwg', 'construction'
    }
    
    def __init__(self):
        """텍스트 추출기 초기화"""
        self.logger = logging.getLogger(__name__)
        if not EZDXF_AVAILABLE:
            raise ImportError("ezdxf 라이브러리가 필요합니다.")
    
    def extract_all_texts_comprehensive(self, file_path: str) -> ComprehensiveExtractionResult:
        """DXF 파일에서 모든 텍스트를 포괄적으로 추출"""
        try:
            self.logger.info(f"포괄적 텍스트 추출 시작: {file_path}")
            
            # DXF 문서 로드
            doc = ezdxf.readfile(file_path)
            result = ComprehensiveExtractionResult()
            
            # 1. 모델스페이스에서 독립적인 텍스트 추출
            self._extract_layout_texts(doc.modelspace(), "ModelSpace", "Model", result)
            
            # 2. 모든 페이퍼스페이스에서 텍스트 추출
            for layout_name in doc.layout_names_in_taborder():
                if layout_name != "Model":  # 모델스페이스 제외
                    try:
                        layout = doc.paperspace(layout_name)
                        self._extract_layout_texts(layout, "PaperSpace", layout_name, result)
                    except Exception as e:
                        self.logger.warning(f"페이퍼스페이스 {layout_name} 처리 실패: {e}")
            
            # 3. 모든 블록 정의에서 텍스트 추출
            for block_layout in doc.blocks:
                if not block_layout.name.startswith('*'):  # 시스템 블록 제외
                    self._extract_block_texts(block_layout, result)
            
            # 4. 모든 블록 참조의 속성 추출 (도곽 제외)
            self._extract_block_attributes(doc, result)
            
            # 5. 결과 분류 및 통계 생성
            self._classify_and_analyze(result)
            
            self.logger.info(f"포괄적 텍스트 추출 완료: 총 {result.total_count}개")
            return result
            
        except Exception as e:
            self.logger.error(f"포괄적 텍스트 추출 실패: {e}")
            raise
    
    def _extract_layout_texts(self, layout, location_type: str, layout_name: str, result: ComprehensiveExtractionResult):
        """레이아웃(모델스페이스/페이퍼스페이스)에서 텍스트 추출"""
        try:
            # TEXT 엔티티 추출
            for text_entity in layout.query('TEXT'):
                text_info = self._create_text_entity_info(
                    text_entity, 'TEXT', location_type, layout_name
                )
                if text_info and text_info.text.strip():
                    result.all_text_entities.append(text_info)
                    if location_type == "ModelSpace":
                        result.modelspace_texts.append(text_info)
                    else:
                        result.paperspace_texts.append(text_info)
            
            # MTEXT 엔티티 추출
            for mtext_entity in layout.query('MTEXT'):
                text_info = self._create_text_entity_info(
                    mtext_entity, 'MTEXT', location_type, layout_name
                )
                if text_info and text_info.text.strip():
                    result.all_text_entities.append(text_info)
                    if location_type == "ModelSpace":
                        result.modelspace_texts.append(text_info)
                    else:
                        result.paperspace_texts.append(text_info)
            
            # 독립적인 ATTRIB 엔티티 추출 (블록 외부)
            for attrib_entity in layout.query('ATTRIB'):
                text_info = self._create_text_entity_info(
                    attrib_entity, 'ATTRIB', location_type, layout_name
                )
                if text_info and text_info.text.strip():
                    result.all_text_entities.append(text_info)
                    if location_type == "ModelSpace":
                        result.modelspace_texts.append(text_info)
                    else:
                        result.paperspace_texts.append(text_info)
                        
        except Exception as e:
            self.logger.warning(f"레이아웃 {layout_name} 텍스트 추출 실패: {e}")
    
    def _extract_block_texts(self, block_layout: BlockLayout, result: ComprehensiveExtractionResult):
        """블록 정의 내부의 TEXT/MTEXT 엔티티 추출"""
        try:
            block_name = block_layout.name
            
            # TEXT 엔티티 추출
            for text_entity in block_layout.query('TEXT'):
                text_info = self._create_text_entity_info(
                    text_entity, 'TEXT', "Block", None, block_name
                )
                if text_info and text_info.text.strip():
                    result.all_text_entities.append(text_info)
                    result.block_texts.append(text_info)
            
            # MTEXT 엔티티 추출
            for mtext_entity in block_layout.query('MTEXT'):
                text_info = self._create_text_entity_info(
                    mtext_entity, 'MTEXT', "Block", None, block_name
                )
                if text_info and text_info.text.strip():
                    result.all_text_entities.append(text_info)
                    result.block_texts.append(text_info)
                    
        except Exception as e:
            self.logger.warning(f"블록 {block_layout.name} 텍스트 추출 실패: {e}")
    
    def _extract_block_attributes(self, doc: Drawing, result: ComprehensiveExtractionResult):
        """모든 블록 참조의 속성 추출 (도곽 블록 제외)"""
        try:
            # 모델스페이스의 블록 참조
            self._process_layout_block_references(doc.modelspace(), "ModelSpace", "Model", result)
            
            # 페이퍼스페이스의 블록 참조
            for layout_name in doc.layout_names_in_taborder():
                if layout_name != "Model":
                    try:
                        layout = doc.paperspace(layout_name)
                        self._process_layout_block_references(layout, "PaperSpace", layout_name, result)
                    except Exception as e:
                        self.logger.warning(f"페이퍼스페이스 {layout_name} 블록 참조 처리 실패: {e}")
                        
        except Exception as e:
            self.logger.warning(f"블록 속성 추출 실패: {e}")
    
    def _process_layout_block_references(self, layout, location_type: str, layout_name: str, result: ComprehensiveExtractionResult):
        """레이아웃의 블록 참조 처리"""
        for insert in layout.query('INSERT'):
            block_name = insert.dxf.name
            
            # 도곽 블록인지 확인
            is_title_block = self._is_title_block(insert)
            
            # 블록의 속성들 추출
            for attrib in insert.attribs:
                text_info = self._create_attrib_entity_info(
                    attrib, location_type, layout_name, block_name, is_title_block
                )
                if text_info and text_info.text.strip():
                    result.all_text_entities.append(text_info)
                    if not is_title_block:
                        result.non_title_block_attributes.append(text_info)
    
    def _is_title_block(self, insert: Insert) -> bool:
        """블록이 도곽 블록인지 판단"""
        try:
            # 블록 이름에서 도곽 키워드 확인
            block_name = insert.dxf.name.lower()
            if any(keyword in block_name for keyword in ['title', 'border', '도곽', '표제']):
                return True
            
            # 속성에서 도곽 키워드 확인
            title_block_attrs = 0
            for attrib in insert.attribs:
                tag = attrib.dxf.tag.lower()
                text = attrib.dxf.text.lower()
                
                if any(keyword in tag or keyword in text for keyword in self.TITLE_BLOCK_KEYWORDS):
                    title_block_attrs += 1
            
            # 2개 이상의 도곽 관련 속성이 있으면 도곽으로 판단
            return title_block_attrs >= 2
            
        except Exception:
            return False
    
    def _create_text_entity_info(self, entity, entity_type: str, location_type: str, 
                                layout_name: Optional[str], parent_block: Optional[str] = None) -> Optional[ComprehensiveTextEntity]:
        """텍스트 엔티티 정보 생성"""
        try:
            # 텍스트 내용 추출
            if entity_type == 'MTEXT':
                text_content = getattr(entity, 'text', '') or getattr(entity.dxf, 'text', '')
            else:
                text_content = getattr(entity.dxf, 'text', '')
            
            if not text_content.strip():
                return None
            
            # 위치 정보
            insert_point = getattr(entity.dxf, 'insert', (0, 0, 0))
            if hasattr(insert_point, 'x'):
                position = (insert_point.x, insert_point.y, insert_point.z)
            else:
                position = (insert_point[0], insert_point[1], insert_point[2] if len(insert_point) > 2 else 0)
            
            # 속성 정보
            height = getattr(entity.dxf, 'height', 1.0)
            if entity_type == 'MTEXT':
                height = getattr(entity.dxf, 'char_height', height)
            
            rotation = getattr(entity.dxf, 'rotation', 0.0)
            layer = getattr(entity.dxf, 'layer', '0')
            color = getattr(entity.dxf, 'color', None)
            style = getattr(entity.dxf, 'style', None)
            entity_handle = getattr(entity.dxf, 'handle', None)
            width_factor = getattr(entity.dxf, 'width_factor', 1.0)
            oblique_angle = getattr(entity.dxf, 'oblique_angle', 0.0)
            text_generation_flag = getattr(entity.dxf, 'text_generation_flag', 0)
            
            # 바운딩 박스 계산
            bbox_info = self._calculate_entity_bbox(entity)
            
            return ComprehensiveTextEntity(
                entity_type=entity_type,
                text=text_content,
                position_x=position[0],
                position_y=position[1],
                position_z=position[2],
                height=height,
                rotation=rotation,
                layer=layer,
                color=color,
                style=style,
                entity_handle=entity_handle,
                location_type=location_type,
                parent_block=parent_block,
                layout_name=layout_name,
                bbox_min_x=bbox_info[0] if bbox_info else None,
                bbox_min_y=bbox_info[1] if bbox_info else None,
                bbox_max_x=bbox_info[2] if bbox_info else None,
                bbox_max_y=bbox_info[3] if bbox_info else None,
                width_factor=width_factor,
                oblique_angle=oblique_angle,
                text_generation_flag=text_generation_flag
            )
            
        except Exception as e:
            self.logger.warning(f"텍스트 엔티티 정보 생성 실패: {e}")
            return None
    
    def _create_attrib_entity_info(self, attrib: Attrib, location_type: str, layout_name: Optional[str], 
                                  parent_block: str, is_title_block: bool) -> Optional[ComprehensiveTextEntity]:
        """속성 엔티티 정보 생성"""
        try:
            text_content = getattr(attrib.dxf, 'text', '')
            if not text_content.strip():
                return None
            
            # 위치 정보
            insert_point = getattr(attrib.dxf, 'insert', (0, 0, 0))
            if hasattr(insert_point, 'x'):
                position = (insert_point.x, insert_point.y, insert_point.z)
            else:
                position = (insert_point[0], insert_point[1], insert_point[2] if len(insert_point) > 2 else 0)
            
            # 속성 정보
            tag = getattr(attrib.dxf, 'tag', '')
            height = getattr(attrib.dxf, 'height', 1.0)
            rotation = getattr(attrib.dxf, 'rotation', 0.0)
            layer = getattr(attrib.dxf, 'layer', '0')
            color = getattr(attrib.dxf, 'color', None)
            style = getattr(attrib.dxf, 'style', None)
            entity_handle = getattr(attrib.dxf, 'handle', None)
            width_factor = getattr(attrib.dxf, 'width_factor', 1.0)
            oblique_angle = getattr(attrib.dxf, 'oblique_angle', 0.0)
            text_generation_flag = getattr(attrib.dxf, 'text_generation_flag', 0)
            
            # 바운딩 박스 계산
            bbox_info = self._calculate_entity_bbox(attrib)
            
            return ComprehensiveTextEntity(
                entity_type='ATTRIB',
                text=text_content,
                position_x=position[0],
                position_y=position[1],
                position_z=position[2],
                height=height,
                rotation=rotation,
                layer=layer,
                color=color,
                style=style,
                entity_handle=entity_handle,
                location_type=location_type,
                parent_block=parent_block,
                layout_name=layout_name,
                attribute_tag=tag,
                is_title_block_attribute=is_title_block,
                bbox_min_x=bbox_info[0] if bbox_info else None,
                bbox_min_y=bbox_info[1] if bbox_info else None,
                bbox_max_x=bbox_info[2] if bbox_info else None,
                bbox_max_y=bbox_info[3] if bbox_info else None,
                width_factor=width_factor,
                oblique_angle=oblique_angle,
                text_generation_flag=text_generation_flag
            )
            
        except Exception as e:
            self.logger.warning(f"속성 엔티티 정보 생성 실패: {e}")
            return None
    
    def _calculate_entity_bbox(self, entity) -> Optional[Tuple[float, float, float, float]]:
        """엔티티의 바운딩 박스 계산"""
        try:
            entity_bbox = bbox.extents([entity])
            if entity_bbox:
                return (entity_bbox.extmin.x, entity_bbox.extmin.y, 
                       entity_bbox.extmax.x, entity_bbox.extmax.y)
        except Exception:
            # 대안: 추정 계산
            try:
                insert_point = getattr(entity.dxf, 'insert', (0, 0, 0))
                height = getattr(entity.dxf, 'height', 1.0)
                
                if hasattr(entity, 'text'):
                    text_content = entity.text
                elif hasattr(entity.dxf, 'text'):
                    text_content = entity.dxf.text
                else:
                    text_content = ""
                
                estimated_width = len(text_content) * height * 0.6
                x, y = insert_point[0], insert_point[1]
                
                return (x, y, x + estimated_width, y + height)
            except Exception:
                pass
        
        return None
    
    def _classify_and_analyze(self, result: ComprehensiveExtractionResult):
        """결과 분류 및 통계 분석"""
        result.total_count = len(result.all_text_entities)
        
        # 타입별 개수
        for entity in result.all_text_entities:
            entity_type = entity.entity_type
            result.by_type_count[entity_type] = result.by_type_count.get(entity_type, 0) + 1
        
        # 위치별 개수
        for entity in result.all_text_entities:
            location = entity.location_type
            result.by_location_count[location] = result.by_location_count.get(location, 0) + 1
        
        # 레이어별 개수
        for entity in result.all_text_entities:
            layer = entity.layer
            result.by_layer_count[layer] = result.by_layer_count.get(layer, 0) + 1
    
    def save_to_csv(self, result: ComprehensiveExtractionResult, output_path: str) -> bool:
        """결과를 CSV 파일로 저장"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'Entity_Type', 'Text', 'Position_X', 'Position_Y', 'Position_Z',
                    'Height', 'Rotation', 'Layer', 'Color', 'Style', 'Entity_Handle',
                    'Location_Type', 'Parent_Block', 'Layout_Name', 'Attribute_Tag',
                    'Is_Title_Block_Attribute', 'BBox_Min_X', 'BBox_Min_Y', 
                    'BBox_Max_X', 'BBox_Max_Y', 'Width_Factor', 'Oblique_Angle'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for entity in result.all_text_entities:
                    writer.writerow({
                        'Entity_Type': entity.entity_type,
                        'Text': entity.text,
                        'Position_X': entity.position_x,
                        'Position_Y': entity.position_y,
                        'Position_Z': entity.position_z,
                        'Height': entity.height,
                        'Rotation': entity.rotation,
                        'Layer': entity.layer,
                        'Color': entity.color,
                        'Style': entity.style,
                        'Entity_Handle': entity.entity_handle,
                        'Location_Type': entity.location_type,
                        'Parent_Block': entity.parent_block,
                        'Layout_Name': entity.layout_name,
                        'Attribute_Tag': entity.attribute_tag,
                        'Is_Title_Block_Attribute': entity.is_title_block_attribute,
                        'BBox_Min_X': entity.bbox_min_x,
                        'BBox_Min_Y': entity.bbox_min_y,
                        'BBox_Max_X': entity.bbox_max_x,
                        'BBox_Max_Y': entity.bbox_max_y,
                        'Width_Factor': entity.width_factor,
                        'Oblique_Angle': entity.oblique_angle
                    })
            
            self.logger.info(f"CSV 저장 완료: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV 저장 실패: {e}")
            return False
    
    def save_to_json(self, result: ComprehensiveExtractionResult, output_path: str) -> bool:
        """결과를 JSON 파일로 저장"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(asdict(result), jsonfile, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"JSON 저장 완료: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"JSON 저장 실패: {e}")
            return False


def main():
    """테스트용 메인 함수"""
    logging.basicConfig(level=logging.INFO)
    
    if not EZDXF_AVAILABLE:
        print("ezdxf 라이브러리가 설치되지 않았습니다.")
        return
    
    extractor = ComprehensiveTextExtractor()
    test_file = "test_drawing.dxf"
    
    if os.path.exists(test_file):
        try:
            result = extractor.extract_all_texts_comprehensive(test_file)
            
            print(f"포괄적 텍스트 추출 결과:")
            print(f"총 텍스트 엔티티: {result.total_count}")
            print(f"모델스페이스: {len(result.modelspace_texts)}")
            print(f"페이퍼스페이스: {len(result.paperspace_texts)}")
            print(f"블록 내부: {len(result.block_texts)}")
            print(f"비도곽 속성: {len(result.non_title_block_attributes)}")
            
            print("\n타입별 개수:")
            for entity_type, count in result.by_type_count.items():
                print(f"  {entity_type}: {count}")
            
            print("\n위치별 개수:")
            for location, count in result.by_location_count.items():
                print(f"  {location}: {count}")
                
            # CSV 저장 테스트
            csv_path = "test_comprehensive_texts.csv"
            if extractor.save_to_csv(result, csv_path):
                print(f"\nCSV 저장 성공: {csv_path}")
                
        except Exception as e:
            print(f"추출 실패: {e}")
    else:
        print(f"테스트 파일을 찾을 수 없습니다: {test_file}")


if __name__ == "__main__":
    main()
