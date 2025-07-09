#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 저장 유틸리티 모듈
DXF 타이틀블럭 Attribute 정보를 CSV 형식으로 저장
"""

import csv
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import Config

logger = logging.getLogger(__name__)


class TitleBlockCSVExporter:
    """타이틀블럭 속성 정보 CSV 저장 클래스"""
    
    def __init__(self, output_dir: str = None):
        """CSV 저장기 초기화"""
        self.output_dir = output_dir or Config.RESULTS_FOLDER
        os.makedirs(self.output_dir, exist_ok=True)
        
    def export_title_block_attributes(
        self, 
        title_block_info: Dict[str, Any], 
        filename: str = None
    ) -> Optional[str]:
        """
        타이틀블럭 속성 정보를 CSV 파일로 저장
        
        Args:
            title_block_info: 타이틀블럭 정보 딕셔너리
            filename: 저장할 파일명 (없으면 자동 생성)
            
        Returns:
            저장된 파일 경로 또는 None (실패시)
        """
        try:
            if not title_block_info or not title_block_info.get('all_attributes'):
                logger.warning("타이틀블럭 속성 정보가 없습니다.")
                return None
            
            # 파일명 생성
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                block_name = title_block_info.get('block_name', 'Unknown_Block')
                filename = f"title_block_attributes_{block_name}_{timestamp}.csv"
            
            # 확장자 확인
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            filepath = os.path.join(self.output_dir, filename)
            
            # CSV 헤더 정의
            headers = [
                'block_name',           # block_ref.name
                'attr_prompt',          # attr.prompt
                'attr_text',            # attr.text
                'attr_tag',             # attr.tag
                'attr_insert_x',        # attr.insert_x
                'attr_insert_y',        # attr.insert_y
                'bounding_box_min_x',   # attr.bounding_box.min_x
                'bounding_box_min_y',   # attr.bounding_box.min_y
                'bounding_box_max_x',   # attr.bounding_box.max_x
                'bounding_box_max_y',   # attr.bounding_box.max_y
                'bounding_box_width',   # attr.bounding_box.width
                'bounding_box_height',  # attr.bounding_box.height
                'attr_height',          # 추가: 텍스트 높이
                'attr_rotation',        # 추가: 회전각
                'attr_layer',           # 추가: 레이어
                'attr_style',           # 추가: 스타일
                'entity_handle'         # 추가: 엔티티 핸들
            ]
            
            # CSV 데이터 준비
            csv_rows = []
            block_name = title_block_info.get('block_name', '')
            
            for attr in title_block_info.get('all_attributes', []):
                row = {
                    'block_name': block_name,
                    'attr_prompt': attr.get('prompt', '') or '',
                    'attr_text': attr.get('text', '') or '',
                    'attr_tag': attr.get('tag', '') or '',
                    'attr_insert_x': attr.get('insert_x', '') or '',
                    'attr_insert_y': attr.get('insert_y', '') or '',
                    'attr_height': attr.get('height', '') or '',
                    'attr_rotation': attr.get('rotation', '') or '',
                    'attr_layer': attr.get('layer', '') or '',
                    'attr_style': attr.get('style', '') or '',
                    'entity_handle': attr.get('entity_handle', '') or '',
                }
                
                # 바운딩 박스 정보 추가
                bbox = attr.get('bounding_box')
                if bbox:
                    row.update({
                        'bounding_box_min_x': bbox.get('min_x', ''),
                        'bounding_box_min_y': bbox.get('min_y', ''),
                        'bounding_box_max_x': bbox.get('max_x', ''),
                        'bounding_box_max_y': bbox.get('max_y', ''),
                        'bounding_box_width': bbox.get('max_x', 0) - bbox.get('min_x', 0) if bbox.get('max_x') and bbox.get('min_x') else '',
                        'bounding_box_height': bbox.get('max_y', 0) - bbox.get('min_y', 0) if bbox.get('max_y') and bbox.get('min_y') else '',
                    })
                else:
                    row.update({
                        'bounding_box_min_x': '',
                        'bounding_box_min_y': '',
                        'bounding_box_max_x': '',
                        'bounding_box_max_y': '',
                        'bounding_box_width': '',
                        'bounding_box_height': '',
                    })
                
                csv_rows.append(row)
            
            # CSV 파일 저장
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                
                # 헤더 작성
                writer.writeheader()
                
                # 데이터 작성
                writer.writerows(csv_rows)
            
            logger.info(f"타이틀블럭 속성 CSV 저장 완료: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"CSV 저장 중 오류: {e}")
            return None
    
    def create_attribute_table_data(
        self, 
        title_block_info: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        UI 테이블 표시용 데이터 생성
        
        Args:
            title_block_info: 타이틀블럭 정보 딕셔너리
            
        Returns:
            테이블 표시용 데이터 리스트
        """
        try:
            if not title_block_info or not title_block_info.get('all_attributes'):
                return []
            
            table_data = []
            block_name = title_block_info.get('block_name', '')
            
            for i, attr in enumerate(title_block_info.get('all_attributes', [])):
                # 바운딩 박스 정보 포맷팅
                bbox_str = ""
                bbox = attr.get('bounding_box')
                if bbox:
                    bbox_str = f"({bbox.get('min_x', 0):.1f}, {bbox.get('min_y', 0):.1f}) - ({bbox.get('max_x', 0):.1f}, {bbox.get('max_y', 0):.1f})"
                
                row = {
                    'No.': str(i + 1),
                    'Block Name': block_name,
                    'Tag': attr.get('tag', ''),
                    'Text': attr.get('text', '')[:30] + ('...' if len(attr.get('text', '')) > 30 else ''),  # 텍스트 길이 제한
                    'Prompt': attr.get('prompt', '') or 'N/A',
                    'X': f"{attr.get('insert_x', 0):.1f}",
                    'Y': f"{attr.get('insert_y', 0):.1f}",
                    'Bounding Box': bbox_str or 'N/A',
                    'Height': f"{attr.get('height', 0):.1f}",
                    'Layer': attr.get('layer', ''),
                }
                
                table_data.append(row)
            
            return table_data
            
        except Exception as e:
            logger.error(f"테이블 데이터 생성 중 오류: {e}")
            return []


def main():
    """테스트용 메인 함수"""
    logging.basicConfig(level=logging.INFO)
    
    # 테스트 데이터
    test_title_block = {
        'block_name': 'TEST_TITLE_BLOCK',
        'all_attributes': [
            {
                'tag': 'DRAWING_NAME',
                'text': '테스트 도면',
                'prompt': '도면명을 입력하세요',
                'insert_x': 100.0,
                'insert_y': 200.0,
                'height': 5.0,
                'rotation': 0.0,
                'layer': '0',
                'style': 'Standard',
                'entity_handle': 'ABC123',
                'bounding_box': {
                    'min_x': 100.0,
                    'min_y': 200.0,
                    'max_x': 180.0,
                    'max_y': 210.0
                }
            },
            {
                'tag': 'DRAWING_NUMBER',
                'text': 'TEST-001',
                'prompt': '도면번호를 입력하세요',
                'insert_x': 100.0,
                'insert_y': 190.0,
                'height': 4.0,
                'rotation': 0.0,
                'layer': '0',
                'style': 'Standard',
                'entity_handle': 'DEF456',
                'bounding_box': {
                    'min_x': 100.0,
                    'min_y': 190.0,
                    'max_x': 150.0,
                    'max_y': 198.0
                }
            }
        ]
    }
    
    # CSV 저장 테스트
    exporter = TitleBlockCSVExporter()
    
    # 테이블 데이터 생성 테스트
    table_data = exporter.create_attribute_table_data(test_title_block)
    print("테이블 데이터:")
    for row in table_data:
        print(row)
    
    # CSV 저장 테스트
    saved_path = exporter.export_title_block_attributes(test_title_block, "test_export.csv")
    if saved_path:
        print(f"\nCSV 저장 성공: {saved_path}")
    else:
        print("\nCSV 저장 실패")


if __name__ == "__main__":
    main()
