"""
다중 파일 처리 모듈
여러 PDF/DXF 파일을 배치로 처리하고 결과를 CSV로 저장하는 기능을 제공합니다.

Author: Claude Assistant
Created: 2025-07-14
Version: 1.0.0
"""

import asyncio
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import logging

from pdf_processor import PDFProcessor
from dxf_processor import EnhancedDXFProcessor
from gemini_analyzer import GeminiAnalyzer
from csv_exporter import TitleBlockCSVExporter
import json # Added import

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FileProcessingResult:
    """단일 파일 처리 결과"""
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    
    # PDF 분석 결과
    pdf_analysis_result: Optional[str] = None
    
    # DXF 분석 결과
    dxf_title_blocks: Optional[List[Dict]] = None
    dxf_total_attributes: Optional[int] = None
    dxf_total_text_entities: Optional[int] = None
    
    # 공통 메타데이터
    processed_at: Optional[str] = None


@dataclass
class BatchProcessingConfig:
    """배치 처리 설정"""
    organization_type: str = "국토교통부"
    enable_gemini_batch_mode: bool = False
    max_concurrent_files: int = 3
    save_intermediate_results: bool = True
    output_csv_path: Optional[str] = None
    include_error_files: bool = True


class MultiFileProcessor:
    """다중 파일 처리기"""
    
    def __init__(self, gemini_api_key: str):
        """
        다중 파일 처리기 초기화
        
        Args:
            gemini_api_key: Gemini API 키
        """
        self.gemini_api_key = gemini_api_key
        self.pdf_processor = PDFProcessor()
        self.dxf_processor = EnhancedDXFProcessor()
        self.gemini_analyzer = GeminiAnalyzer(gemini_api_key)
        self.csv_exporter = TitleBlockCSVExporter()  # CSV 내보내기 추가
        
        self.processing_results: List[FileProcessingResult] = []
        self.current_progress = 0
        self.total_files = 0
        
    async def process_multiple_files(
        self,
        file_paths: List[str],
        config: BatchProcessingConfig,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[FileProcessingResult]:
        """
        여러 파일을 배치로 처리
        
        Args:
            file_paths: 처리할 파일 경로 리스트
            config: 배치 처리 설정
            progress_callback: 진행률 콜백 함수 (current, total, status)
            
        Returns:
            처리 결과 리스트
        """
        self.processing_results = []
        self.total_files = len(file_paths)
        self.current_progress = 0
        
        logger.info(f"배치 처리 시작: {self.total_files}개 파일")
        
        # 동시 처리 제한을 위한 세마포어
        semaphore = asyncio.Semaphore(config.max_concurrent_files)
        
        # 각 파일에 대한 처리 태스크 생성
        tasks = []
        for i, file_path in enumerate(file_paths):
            task = self._process_single_file_with_semaphore(
                semaphore, file_path, config, progress_callback, i + 1
            )
            tasks.append(task)
        
        # 모든 파일 처리 완료까지 대기
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 발생한 결과 처리
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = FileProcessingResult(
                    file_path=file_paths[i],
                    file_name=os.path.basename(file_paths[i]),
                    file_type="unknown",
                    file_size=0,
                    processing_time=0,
                    success=False,
                    error_message=str(result),
                    processed_at=datetime.now().isoformat()
                )
                self.processing_results.append(error_result)
        
        logger.info(f"배치 처리 완료: {len(self.processing_results)}개 결과")
        
        # CSV 저장
        if config.output_csv_path:
            await self.save_results_to_csv(config.output_csv_path)
        
        return self.processing_results
    
    async def _process_single_file_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        file_path: str,
        config: BatchProcessingConfig,
        progress_callback: Optional[Callable[[int, int, str], None]],
        file_number: int
    ) -> None:
        """세마포어를 사용하여 단일 파일 처리"""
        async with semaphore:
            result = await self._process_single_file(file_path, config)
            self.processing_results.append(result)
            
            self.current_progress += 1
            if progress_callback:
                status = f"처리 완료: {result.file_name}"
                if not result.success:
                    status = f"처리 실패: {result.file_name} - {result.error_message}"
                progress_callback(self.current_progress, self.total_files, status)
    
    async def _process_single_file(
        self,
        file_path: str,
        config: BatchProcessingConfig
    ) -> FileProcessingResult:
        """
        단일 파일 처리
        
        Args:
            file_path: 파일 경로
            config: 처리 설정
            
        Returns:
            처리 결과
        """
        start_time = asyncio.get_event_loop().time()
        file_name = os.path.basename(file_path)
        
        try:
            # 파일 정보 수집
            file_size = os.path.getsize(file_path)
            file_type = self._detect_file_type(file_path)
            
            logger.info(f"파일 처리 시작: {file_name} ({file_type})")
            
            result = FileProcessingResult(
                file_path=file_path,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                processing_time=0,
                success=False,
                processed_at=datetime.now().isoformat()
            )
            
            # 파일 유형에 따른 처리
            if file_type.lower() == 'pdf':
                await self._process_pdf_file(file_path, result, config)
            elif file_type.lower() == 'dxf':
                await self._process_dxf_file(file_path, result, config)
            else:
                raise ValueError(f"지원하지 않는 파일 형식: {file_type}")
            
            result.success = True
            
        except Exception as e:
            logger.error(f"파일 처리 오류 ({file_name}): {str(e)}")
            result.success = False
            result.error_message = str(e)
        
        finally:
            # 처리 시간 계산
            end_time = asyncio.get_event_loop().time()
            result.processing_time = round(end_time - start_time, 2)
            
        return result
    
    async def _process_pdf_file(
        self,
        file_path: str,
        result: FileProcessingResult,
        config: BatchProcessingConfig
    ) -> None:
        """PDF 파일 처리"""
        # PDF 이미지 변환
        images = self.pdf_processor.convert_to_images(file_path)
        if not images:
            raise ValueError("PDF를 이미지로 변환할 수 없습니다")
        
        # 첫 번째 페이지만 분석 (다중 페이지 처리는 향후 개선)
        first_page = images[0]
        base64_image = self.pdf_processor.image_to_base64(first_page)
        
        # PDF에서 텍스트 블록 추출
        text_blocks = self.pdf_processor.extract_text_with_coordinates(file_path, 0)
        
        # Gemini API로 분석
        # 실제 구현에서는 batch mode 사용 가능
        analysis_result = await self._analyze_with_gemini(
            base64_image, text_blocks, config.organization_type
        )
        
        result.pdf_analysis_result = analysis_result
    
    async def _process_dxf_file(
        self,
        file_path: str,
        result: FileProcessingResult,
        config: BatchProcessingConfig
    ) -> None:
        """DXF 파일 처리"""
        # DXF 파일 분석
        extraction_result = self.dxf_processor.extract_comprehensive_data(file_path)
        
        # 타이틀 블록 정보를 딕셔너리 리스트로 변환
        title_blocks = []
        for tb_info in extraction_result.title_blocks:
            tb_dict = {
                'block_name': tb_info.block_name,
                'block_position': f"{tb_info.block_position[0]:.2f}, {tb_info.block_position[1]:.2f}",
                'attributes_count': tb_info.attributes_count,
                'attributes': [
                    {
                        'tag': attr.tag,
                        'text': attr.text,
                        'prompt': attr.prompt,
                        'insert_x': attr.insert_x,
                        'insert_y': attr.insert_y
                    }
                    for attr in tb_info.all_attributes
                ]
            }
            title_blocks.append(tb_dict)
        
        result.dxf_title_blocks = title_blocks
        result.dxf_total_attributes = sum(tb['attributes_count'] for tb in title_blocks)
        result.dxf_total_text_entities = len(extraction_result.text_entities)
        
        # 상세한 title block attributes CSV 생성
        if extraction_result.title_blocks:
            await self._save_detailed_dxf_csv(file_path, extraction_result)
    
    async def _analyze_with_gemini(
        self,
        base64_image: str,
        text_blocks: list,
        organization_type: str
    ) -> str:
        """Gemini API로 이미지 분석"""
        try:
            # 비동기 처리를 위해 동기 함수를 태스크로 실행
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.gemini_analyzer.analyze_pdf_page,
                base64_image,
                text_blocks,
                None,  # prompt (default 사용)
                "image/png",  # mime_type
                organization_type
            )
            return result
        except Exception as e:
            logger.error(f"Gemini 분석 오류: {str(e)}")
            return f"분석 실패: {str(e)}"
    
    async def _save_detailed_dxf_csv(
        self,
        file_path: str,
        extraction_result
    ) -> None:
        """상세한 DXF title block attributes CSV 저장"""
        try:
            # 파일명에서 확장자 제거
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 출력 디렉토리 확인 및 생성
            output_dir = os.path.join(os.path.dirname(file_path), '..', 'results')
            os.makedirs(output_dir, exist_ok=True)
            
            # CSV 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"detailed_title_blocks_{file_name}_{timestamp}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            
            # TitleBlockCSVExporter를 사용하여 CSV 생성
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.csv_exporter.save_title_block_info_to_csv,
                extraction_result.title_blocks,
                csv_path
            )
            
            logger.info(f"상세 DXF CSV 저장 완료: {csv_path}")
            
        except Exception as e:
            logger.error(f"상세 DXF CSV 저장 오류: {str(e)}")
    
    def _detect_file_type(self, file_path: str) -> str:
        """파일 확장자로 파일 유형 검출"""
        _, ext = os.path.splitext(file_path.lower())
        if ext == '.pdf':
            return 'PDF'
        elif ext == '.dxf':
            return 'DXF'
        else:
            return ext.upper().lstrip('.')
    
    async def save_results_to_csv(self, output_path: str) -> None:
        """
        처리 결과를 CSV 파일로 저장
        
        Args:
            output_path: 출력 CSV 파일 경로
        """
        try:
            # 결과를 DataFrame으로 변환
            data_rows = []
            
            for result in self.processing_results:
                # 기본 정보
                row = {
                    'file_name': result.file_name,
                    'file_path': result.file_path,
                    'file_type': result.file_type,
                    'file_size_bytes': result.file_size,
                    'file_size_mb': round(result.file_size / (1024 * 1024), 2),
                    'processing_time_seconds': result.processing_time,
                    'success': result.success,
                    'error_message': result.error_message or '',
                    'processed_at': result.processed_at
                }
                
                # PDF 분석 결과
                if result.file_type.lower() == 'pdf':
                    row['pdf_analysis_result'] = result.pdf_analysis_result or ''
                    row['dxf_total_attributes'] = ''
                    row['dxf_total_text_entities'] = ''
                    row['dxf_title_blocks_summary'] = ''
                
                # DXF 분석 결과
                elif result.file_type.lower() == 'dxf':
                    row['pdf_analysis_result'] = ''
                    row['dxf_total_attributes'] = result.dxf_total_attributes or 0
                    row['dxf_total_text_entities'] = result.dxf_total_text_entities or 0
                    
                    # 타이틀 블록 요약
                    if result.dxf_title_blocks:
                        summary = f"{len(result.dxf_title_blocks)}개 타이틀블록"
                        for tb in result.dxf_title_blocks[:3]:  # 처음 3개만 표시
                            summary += f" | {tb['block_name']}({tb['attributes_count']}속성)"
                        if len(result.dxf_title_blocks) > 3:
                            summary += f" | ...외 {len(result.dxf_title_blocks)-3}개"
                        row['dxf_title_blocks_summary'] = summary
                    else:
                        row['dxf_title_blocks_summary'] = '타이틀블록 없음'
                
                data_rows.append(row)
            
            # DataFrame 생성 및 CSV 저장
            df = pd.DataFrame(data_rows)

            # pdf_analysis_result 컬럼 평탄화
            if 'pdf_analysis_result' in df.columns:
                # JSON 문자열을 딕셔너리로 변환 (이미 딕셔너리인 경우도 처리)
                df['pdf_analysis_result'] = df['pdf_analysis_result'].apply(lambda x: json.loads(x) if isinstance(x, str) and x.strip() else {}).fillna({})
                
                # 평탄화된 데이터를 새로운 DataFrame으로 생성
                # errors='ignore'를 사용하여 JSON이 아닌 값은 무시
                # record_prefix를 사용하여 컬럼 이름에 접두사 추가
                pdf_analysis_df = pd.json_normalize(df['pdf_analysis_result'], errors='ignore', record_prefix='pdf_analysis_result_')
                
                # 원본 df에서 pdf_analysis_result 컬럼 제거
                df = df.drop(columns=['pdf_analysis_result'])
                
                # 원본 df와 평탄화된 DataFrame을 병합
                df = pd.concat([df, pdf_analysis_df], axis=1)

            # 컬럼 순서 정렬을 위한 기본 순서 정의
            column_order = [
                'file_name', 'file_type', 'file_size_mb', 'processing_time_seconds',
                'success', 'error_message', 'processed_at', 'file_path', 'file_size_bytes',
                'dxf_total_attributes', 'dxf_total_text_entities', 'dxf_title_blocks_summary'
            ]

            # 기존 컬럼 순서를 유지하면서 새로운 컬럼을 추가
            existing_columns = [col for col in column_order if col in df.columns]
            new_columns = [col for col in df.columns if col not in existing_columns]
            df = df[existing_columns + sorted(new_columns)]
            
            # UTF-8 BOM으로 저장 (한글 호환성)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"CSV 저장 완료: {output_path}")
            logger.info(f"총 {len(data_rows)}개 파일 결과 저장")
            
        except Exception as e:
            logger.error(f"CSV 저장 오류: {str(e)}")
            raise
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """처리 결과 요약 정보 반환"""
        if not self.processing_results:
            return {}
        
        total_files = len(self.processing_results)
        success_files = sum(1 for r in self.processing_results if r.success)
        failed_files = total_files - success_files
        
        pdf_files = sum(1 for r in self.processing_results if r.file_type.lower() == 'pdf')
        dxf_files = sum(1 for r in self.processing_results if r.file_type.lower() == 'dxf')
        
        total_processing_time = sum(r.processing_time for r in self.processing_results)
        avg_processing_time = total_processing_time / total_files if total_files > 0 else 0
        
        total_file_size = sum(r.file_size for r in self.processing_results)
        
        return {
            'total_files': total_files,
            'success_files': success_files,
            'failed_files': failed_files,
            'pdf_files': pdf_files,
            'dxf_files': dxf_files,
            'total_processing_time': round(total_processing_time, 2),
            'avg_processing_time': round(avg_processing_time, 2),
            'total_file_size_mb': round(total_file_size / (1024 * 1024), 2),
            'success_rate': round((success_files / total_files) * 100, 1) if total_files > 0 else 0
        }


def generate_default_csv_filename() -> str:
    """기본 CSV 파일명 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"batch_analysis_results_{timestamp}.csv"


# 사용 예시
if __name__ == "__main__":
    async def main():
        # 테스트용 예시
        processor = MultiFileProcessor("your-gemini-api-key")
        
        config = BatchProcessingConfig(
            organization_type="국토교통부",
            max_concurrent_files=2,
            output_csv_path="test_results.csv"
        )
        
        # 진행률 콜백 함수
        def progress_callback(current: int, total: int, status: str):
            print(f"진행률: {current}/{total} ({current/total*100:.1f}%) - {status}")
        
        # 파일 경로 리스트 (실제 파일 경로로 교체 필요)
        file_paths = [
            "sample1.pdf",
            "sample2.dxf",
            "sample3.pdf"
        ]
        
        results = await processor.process_multiple_files(
            file_paths, config, progress_callback
        )
        
        summary = processor.get_processing_summary()
        print("처리 요약:", summary)
    
    # asyncio.run(main())
