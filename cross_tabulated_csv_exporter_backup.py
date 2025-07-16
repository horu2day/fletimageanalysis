"""
Cross-Tabulated CSV 내보내기 모듈
JSON 형태의 분석 결과를 key-value 형태의 cross-tabulated CSV로 저장하는 기능을 제공합니다.

Author: Claude Assistant  
Created: 2025-07-15
Version: 1.0.0
"""

import pandas as pd
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import os
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossTabulatedCSVExporter:
    """Cross-Tabulated CSV 내보내기 클래스"""
    
    def __init__(self):
        """Cross-Tabulated CSV 내보내기 초기화"""
        self.coordinate_pattern = re.compile(r'\b(\d+)\s*,\s*(\d+)\b')  # x,y 좌표 패턴
        
    def export_cross_tabulated_csv(
        self,
        processing_results: List[Any],
        output_path: str,
        include_coordinates: bool = True,
        coordinate_source: str = "auto"  # "auto", "text_blocks", "analysis_result", "none"
    ) -> bool:
        """
        처리 결과를 cross-tabulated CSV 형태로 저장
        
        Args:
            processing_results: 다중 파일 처리 결과 리스트
            output_path: 출력 CSV 파일 경로
            include_coordinates: 좌표 정보 포함 여부
            coordinate_source: 좌표 정보 출처 ("auto", "text_blocks", "analysis_result", "none")
            
        Returns:
            저장 성공 여부
        """
        try:
            logger.info(f"Cross-tabulated CSV 저장 시작: {len(processing_results)}개 파일")
            
            # 모든 파일의 key-value 쌍을 수집
            all_data_rows = []
            
            for result in processing_results:
                if not result.success:
                    continue  # 실패한 파일은 제외
                    
                file_data = self._extract_key_value_pairs(result, include_coordinates, coordinate_source)
                all_data_rows.extend(file_data)
            
            if not all_data_rows:
                logger.warning("저장할 데이터가 없습니다")
                return False
            
            # DataFrame 생성
            df = pd.DataFrame(all_data_rows)
            
            # 컬럼 순서 정렬
            column_order = ['file_name', 'file_type', 'key', 'value']
            if include_coordinates and coordinate_source != "none":
                column_order.extend(['x', 'y'])
            
            # 추가 컬럼들을 뒤에 배치
            existing_columns = [col for col in column_order if col in df.columns]
            additional_columns = [col for col in df.columns if col not in existing_columns]
            df = df[existing_columns + additional_columns]
            
            # UTF-8 BOM으로 저장 (한글 호환성)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"Cross-tabulated CSV 저장 완료: {output_path}")
            logger.info(f"총 {len(all_data_rows)}개 key-value 쌍 저장")
            
            return True
            
        except Exception as e:
            logger.error(f"Cross-tabulated CSV 저장 오류: {str(e)}")
            return False
    
    def _extract_key_value_pairs(
        self,
        result: Any,
        include_coordinates: bool,
        coordinate_source: str
    ) -> List[Dict[str, Any]]:
        """
        단일 파일 결과에서 key-value 쌍 추출
        
        Args:
            result: 파일 처리 결과
            include_coordinates: 좌표 정보 포함 여부
            coordinate_source: 좌표 정보 출처
            
        Returns:
            key-value 쌍 리스트
        """
        data_rows = []
        
        try:
            # 기본 정보
            base_info = {
                'file_name': result.file_name,
                'file_type': result.file_type,
            }
            
            # PDF 분석 결과 처리
            if result.file_type.lower() == 'pdf' and result.pdf_analysis_result:
                data_rows.extend(
                    self._extract_pdf_key_values(result, base_info, include_coordinates, coordinate_source)
                )
            
            # DXF 분석 결과 처리
            elif result.file_type.lower() == 'dxf' and result.dxf_title_blocks:
                data_rows.extend(
                    self._extract_dxf_key_values(result, base_info, include_coordinates, coordinate_source)
                )
            
        except Exception as e:
            logger.error(f"Key-value 추출 오류 ({result.file_name}): {str(e)}")
        
        return data_rows
    
    def _extract_pdf_key_values(
        self,
        result: Any,
        base_info: Dict[str, str],
        include_coordinates: bool,
        coordinate_source: str
    ) -> List[Dict[str, Any]]:
        """PDF 분석 결과에서 key-value 쌍 추출"""
        data_rows = []
        
        try:
            # PDF 분석 결과를 JSON으로 파싱
            analysis_result = result.pdf_analysis_result
            if isinstance(analysis_result, str):
                try:
                    analysis_data = json.loads(analysis_result)
                except json.JSONDecodeError:
                    # JSON이 아닌 경우 텍스트로 처리
                    analysis_data = {"분석결과": analysis_result}
            else:
                analysis_data = analysis_result
            
            # 중첩된 구조를 평탄화하여 key-value 쌍 생성
            flattened_data = self._flatten_dict(analysis_data)
            
            for key, value in flattened_data.items():
                if value is None or str(value).strip() == "":
                    continue  # 빈 값 제외
                
                row_data = base_info.copy()
                row_data.update({
                    'key': key,
                    'value': str(value),
                })
                
                # 좌표 정보 추가
                if include_coordinates and coordinate_source != "none":
                    coordinates = self._extract_coordinates(key, value, coordinate_source)
                    row_data.update(coordinates)
                
                data_rows.append(row_data)
                
        except Exception as e:
            logger.error(f"PDF key-value 추출 오류: {str(e)}")
        
        return data_rows
    
    def _extract_dxf_key_values(
        self,
        result: Any,
        base_info: Dict[str, str],
        include_coordinates: bool,
        coordinate_source: str
    ) -> List[Dict[str, Any]]:
        """DXF 분석 결과에서 key-value 쌍 추출"""
        data_rows = []
        
        try:
            for title_block in result.dxf_title_blocks:
                block_name = title_block.get('block_name', 'Unknown')
                
                # 블록 정보
                row_data = base_info.copy()
                row_data.update({
                    'key': f"{block_name}_블록명",
                    'value': block_name,
                })
                
                if include_coordinates and coordinate_source != "none":
                    coordinates = self._extract_coordinates('블록명', block_name, coordinate_source)
                    row_data.update(coordinates)
                
                data_rows.append(row_data)
                
                # 속성 정보
                for attr in title_block.get('attributes', []):
                    if not attr.get('text') or str(attr.get('text')).strip() == "":
                        continue  # 빈 속성 제외
                    
                    # 속성별 key-value 쌍 생성
                    attr_key = attr.get('tag', attr.get('prompt', 'Unknown'))
                    attr_value = attr.get('text', '')
                    
                    row_data = base_info.copy()
                    row_data.update({
                        'key': attr_key,
                        'value': str(attr_value),
                    })
                    
                    # DXF 속성의 경우 insert 좌표 사용
                    if include_coordinates and coordinate_source != "none":
                        x_coord = attr.get('insert_x', '')
                        y_coord = attr.get('insert_y', '')
                        
                        if x_coord and y_coord:
                            row_data.update({
                                'x': round(float(x_coord), 2) if isinstance(x_coord, (int, float)) else x_coord,
                                'y': round(float(y_coord), 2) if isinstance(y_coord, (int, float)) else y_coord,
                            })
                        else:
                            row_data.update({'x': '', 'y': ''})
                    
                    data_rows.append(row_data)
                    
        except Exception as e:
            logger.error(f"DXF key-value 추출 오류: {str(e)}")
        
        return data_rows
    
    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        중첩된 딕셔너리를 평탄화
        
        Args:
            data: 평탄화할 딕셔너리
            parent_key: 부모 키
            sep: 구분자
            
        Returns:
            평탄화된 딕셔너리
        """
        items = []
        
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                # 중첩된 딕셔너리인 경우 재귀 호출
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # 리스트인 경우 인덱스와 함께 처리
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
                    else:
                        items.append((f"{new_key}_{i}", item))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def _extract_coordinates(self, key: str, value: str, coordinate_source: str) -> Dict[str, str]:
        """
        텍스트에서 좌표 정보 추출
        
        Args:
            key: 키
            value: 값
            coordinate_source: 좌표 정보 출처
            
        Returns:
            좌표 딕셔너리
        """
        coordinates = {'x': '', 'y': ''}
        
        try:
            # 값에서 좌표 패턴 찾기
            matches = self.coordinate_pattern.findall(str(value))
            
            if matches:
                # 첫 번째 매치 사용
                x, y = matches[0]
                coordinates = {'x': x, 'y': y}
            else:
                # 키에서 좌표 정보 찾기
                key_matches = self.coordinate_pattern.findall(str(key))
                if key_matches:
                    x, y = key_matches[0]
                    coordinates = {'x': x, 'y': y}
        
        except Exception as e:
            logger.warning(f"좌표 추출 오류: {str(e)}")
        
        return coordinates


def generate_cross_tabulated_csv_filename(base_name: str = "cross_tabulated_analysis") -> str:
    """기본 Cross-tabulated CSV 파일명 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_results_{timestamp}.csv"


# 사용 예시
if __name__ == "__main__":
    # 테스트용 예시
    exporter = CrossTabulatedCSVExporter()
    
    # 샘플 처리 결과 (실제 데이터 구조에 맞게 수정)
    sample_results = []
    
    # 실제 사용 시에는 processing_results를 전달
    # success = exporter.export_cross_tabulated_csv(
    #     sample_results,
    #     "test_cross_tabulated.csv",
    #     include_coordinates=True
    # )
    
    print("Cross-tabulated CSV 내보내기 모듈 테스트 완료")
