"""
Cross-Tabulated CSV 내보내기 모듈 (수정 버전)
JSON 형태의 분석 결과를 key-value 형태의 cross-tabulated CSV로 저장하는 기능을 제공합니다.

Author: Claude Assistant  
Created: 2025-07-15
Updated: 2025-07-16 (디버깅 개선 버전)
Version: 1.1.0
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
    """Cross-Tabulated CSV 내보내기 클래스 (수정 버전)"""
    
    def __init__(self):
        """Cross-Tabulated CSV 내보내기 초기화"""
        self.coordinate_pattern = re.compile(r'\b(\d+)\s*,\s*(\d+)\b')  # x,y 좌표 패턴
        self.debug_mode = True  # 디버깅 모드 활성화
        
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
            if self.debug_mode:
                logger.info(f"=== Cross-tabulated CSV 저장 시작 ===")
                logger.info(f"입력된 결과 수: {len(processing_results)}")
                logger.info(f"출력 경로: {output_path}")
                logger.info(f"좌표 포함: {include_coordinates}, 좌표 출처: {coordinate_source}")
            
            # 입력 데이터 검증
            if not processing_results:
                logger.warning("입력된 처리 결과가 비어있습니다.")
                return False
            
            # 각 결과 객체의 구조 분석
            for i, result in enumerate(processing_results):
                if self.debug_mode:
                    logger.info(f"결과 {i+1}: {self._analyze_result_structure(result)}")
            
            # 모든 파일의 key-value 쌍을 수집
            all_data_rows = []
            
            for i, result in enumerate(processing_results):
                try:
                    if not hasattr(result, 'success'):
                        logger.warning(f"결과 {i+1}: 'success' 속성이 없습니다. 스킵합니다.")
                        continue
                        
                    if not result.success:
                        if self.debug_mode:
                            logger.info(f"결과 {i+1}: 실패한 파일, 스킵합니다 ({getattr(result, 'error_message', 'Unknown error')})")
                        continue  # 실패한 파일은 제외
                        
                    file_data = self._extract_key_value_pairs(result, include_coordinates, coordinate_source)
                    if file_data:
                        all_data_rows.extend(file_data)
                        if self.debug_mode:
                            logger.info(f"결과 {i+1}: {len(file_data)}개 key-value 쌍 추출")
                    else:
                        if self.debug_mode:
                            logger.warning(f"결과 {i+1}: key-value 쌍을 추출할 수 없습니다")
                            
                except Exception as e:
                    logger.error(f"결과 {i+1} 처리 중 오류: {str(e)}")
                    continue
            
            if not all_data_rows:
                logger.warning("저장할 데이터가 없습니다. 모든 파일에서 유효한 key-value 쌍을 추출할 수 없었습니다.")
                if self.debug_mode:
                    self._print_debug_summary(processing_results)
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
            
            # 출력 디렉토리 생성
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # UTF-8 BOM으로 저장 (한글 호환성)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"Cross-tabulated CSV 저장 완료: {output_path}")
            logger.info(f"총 {len(all_data_rows)}개 key-value 쌍 저장")
            
            return True
            
        except Exception as e:
            logger.error(f"Cross-tabulated CSV 저장 오류: {str(e)}")
            return False
    
    def _analyze_result_structure(self, result: Any) -> str:
        """결과 객체의 구조를 분석하여 문자열로 반환"""
        try:
            info = []
            
            # 기본 속성들 확인
            if hasattr(result, 'file_name'):
                info.append(f"file_name='{result.file_name}'")
            if hasattr(result, 'file_type'):
                info.append(f"file_type='{result.file_type}'")
            if hasattr(result, 'success'):
                info.append(f"success={result.success}")
            
            # PDF 관련 속성
            if hasattr(result, 'pdf_analysis_result'):
                pdf_result = result.pdf_analysis_result
                if pdf_result:
                    if isinstance(pdf_result, str):
                        info.append(f"pdf_analysis_result=str({len(pdf_result)} chars)")
                    else:
                        info.append(f"pdf_analysis_result={type(pdf_result).__name__}")
                else:
                    info.append("pdf_analysis_result=None")
            
            # DXF 관련 속성
            if hasattr(result, 'dxf_title_blocks'):
                dxf_blocks = result.dxf_title_blocks
                if dxf_blocks:
                    info.append(f"dxf_title_blocks=list({len(dxf_blocks)} blocks)")
                else:
                    info.append("dxf_title_blocks=None")
            
            return " | ".join(info) if info else "구조 분석 실패"
            
        except Exception as e:
            return f"분석 오류: {str(e)}"
    
    def _print_debug_summary(self, processing_results: List[Any]):
        """디버깅을 위한 요약 정보 출력"""
        logger.info("=== 디버깅 요약 ===")
        
        success_count = 0
        pdf_count = 0
        dxf_count = 0
        has_pdf_data = 0
        has_dxf_data = 0
        
        for i, result in enumerate(processing_results):
            try:
                if hasattr(result, 'success') and result.success:
                    success_count += 1
                    
                    file_type = getattr(result, 'file_type', 'unknown').lower()
                    if file_type == 'pdf':
                        pdf_count += 1
                        if getattr(result, 'pdf_analysis_result', None):
                            has_pdf_data += 1
                    elif file_type == 'dxf':
                        dxf_count += 1
                        if getattr(result, 'dxf_title_blocks', None):
                            has_dxf_data += 1
                            
            except Exception as e:
                logger.error(f"결과 {i+1} 분석 중 오류: {str(e)}")
        
        logger.info(f"총 결과: {len(processing_results)}개")
        logger.info(f"성공한 결과: {success_count}개")
        logger.info(f"PDF 파일: {pdf_count}개 (분석 데이터 있음: {has_pdf_data}개)")
        logger.info(f"DXF 파일: {dxf_count}개 (타이틀블록 데이터 있음: {has_dxf_data}개)")
    
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
            # 기본 정보 확인
            file_name = getattr(result, 'file_name', 'Unknown')
            file_type = getattr(result, 'file_type', 'Unknown')
            
            base_info = {
                'file_name': file_name,
                'file_type': file_type,
            }
            
            if self.debug_mode:
                logger.info(f"처리 중: {file_name} ({file_type})")
            
            # PDF 분석 결과 처리
            if file_type.lower() == 'pdf':
                pdf_result = getattr(result, 'pdf_analysis_result', None)
                if pdf_result:
                    pdf_rows = self._extract_pdf_key_values(result, base_info, include_coordinates, coordinate_source)
                    data_rows.extend(pdf_rows)
                    if self.debug_mode:
                        logger.info(f"PDF에서 {len(pdf_rows)}개 key-value 쌍 추출")
                else:
                    if self.debug_mode:
                        logger.warning(f"PDF 분석 결과가 없습니다: {file_name}")
            
            # DXF 분석 결과 처리
            elif file_type.lower() == 'dxf':
                dxf_blocks = getattr(result, 'dxf_title_blocks', None)
                if dxf_blocks:
                    dxf_rows = self._extract_dxf_key_values(result, base_info, include_coordinates, coordinate_source)
                    data_rows.extend(dxf_rows)
                    if self.debug_mode:
                        logger.info(f"DXF에서 {len(dxf_rows)}개 key-value 쌍 추출")
                else:
                    if self.debug_mode:
                        logger.warning(f"DXF 타이틀블록 데이터가 없습니다: {file_name}")
            
            else:
                if self.debug_mode:
                    logger.warning(f"지원하지 않는 파일 형식: {file_type}")
            
        except Exception as e:
            logger.error(f"Key-value 추출 오류 ({getattr(result, 'file_name', 'Unknown')}): {str(e)}")
        
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
            analysis_result = getattr(result, 'pdf_analysis_result', None)
            
            if not analysis_result:
                return data_rows
            
            if isinstance(analysis_result, str):
                try:
                    analysis_data = json.loads(analysis_result)
                except json.JSONDecodeError:
                    # JSON이 아닌 경우 텍스트로 처리
                    analysis_data = {"분석결과": analysis_result}
            else:
                analysis_data = analysis_result
            
            if self.debug_mode:
                logger.info(f"PDF 분석 데이터 구조: {type(analysis_data).__name__}")
                if isinstance(analysis_data, dict):
                    logger.info(f"PDF 분석 데이터 키: {list(analysis_data.keys())}")
            
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
            title_blocks = getattr(result, 'dxf_title_blocks', None)
            
            if not title_blocks:
                return data_rows
            
            if self.debug_mode:
                logger.info(f"DXF 타이틀블록 수: {len(title_blocks)}")
            
            for block_idx, title_block in enumerate(title_blocks):
                if not isinstance(title_block, dict):
                    continue
                    
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
                attributes = title_block.get('attributes', [])
                if self.debug_mode:
                    logger.info(f"블록 {block_idx+1} ({block_name}): {len(attributes)}개 속성")
                
                for attr_idx, attr in enumerate(attributes):
                    if not isinstance(attr, dict):
                        continue
                        
                    attr_text = attr.get('text', '')
                    if not attr_text or str(attr_text).strip() == "":
                        continue  # 빈 속성 제외
                    
                    # 속성별 key-value 쌍 생성
                    attr_key = attr.get('tag', attr.get('prompt', f'Unknown_Attr_{attr_idx}'))
                    attr_value = str(attr_text)
                    
                    row_data = base_info.copy()
                    row_data.update({
                        'key': attr_key,
                        'value': attr_value,
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
    
    print("Cross-tabulated CSV 내보내기 모듈 (수정 버전) 테스트 완료")
