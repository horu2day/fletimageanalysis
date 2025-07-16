"""
간단한 다중 파일 배치 처리 모듈
getcode.py 스타일의 간단한 분석을 여러 파일에 적용하고 결과를 CSV로 저장합니다.

Author: Claude Assistant
Created: 2025-07-14
Version: 1.0.0
"""

import asyncio
import os
import pandas as pd
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import logging

from simple_gemini_analyzer import SimpleGeminiAnalyzer
from pdf_processor import PDFProcessor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SimpleBatchResult:
    """간단한 배치 처리 결과"""
    file_path: str
    file_name: str
    file_size_mb: float
    processing_time_seconds: float
    success: bool
    
    # 분석 결과
    analysis_result: Optional[str] = None
    analysis_timestamp: Optional[str] = None
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    error_message: Optional[str] = None
    
    # 메타데이터
    processed_at: Optional[str] = None


class SimpleBatchProcessor:
    """
    간단한 다중 파일 배치 처리기
    getcode.py 스타일의 분석을 여러 PDF 파일에 적용합니다.
    """
    
    def __init__(self, gemini_api_key: str):
        """
        배치 처리기 초기화
        
        Args:
            gemini_api_key: Gemini API 키
        """
        self.gemini_api_key = gemini_api_key
        self.analyzer = SimpleGeminiAnalyzer(gemini_api_key)
        self.pdf_processor = PDFProcessor()
        
        self.results: List[SimpleBatchResult] = []
        self.current_progress = 0
        self.total_files = 0
        
        logger.info("간단한 배치 처리기 초기화 완료")
    
    async def process_multiple_pdf_files(
        self,
        pdf_file_paths: List[str],
        output_csv_path: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        max_concurrent_files: int = 3,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[SimpleBatchResult]:
        """
        여러 PDF 파일을 배치로 처리하고 결과를 CSV로 저장
        
        Args:
            pdf_file_paths: 처리할 PDF 파일 경로 리스트
            output_csv_path: 출력 CSV 파일 경로 (None인 경우 자동 생성)
            custom_prompt: 사용자 정의 프롬프트 (None인 경우 기본 프롬프트 사용)
            max_concurrent_files: 동시 처리할 최대 파일 수
            progress_callback: 진행률 콜백 함수 (current, total, status)
            
        Returns:
            처리 결과 리스트
        """
        self.results = []
        self.total_files = len(pdf_file_paths)
        self.current_progress = 0
        
        logger.info(f"간단한 배치 처리 시작: {self.total_files}개 PDF 파일")
        
        if not pdf_file_paths:
            logger.warning("처리할 파일이 없습니다.")
            return []
        
        # 동시 처리 제한을 위한 세마포어
        semaphore = asyncio.Semaphore(max_concurrent_files)
        
        # 각 파일에 대한 처리 태스크 생성
        tasks = []
        for i, file_path in enumerate(pdf_file_paths):
            task = self._process_single_pdf_with_semaphore(
                semaphore, file_path, custom_prompt, progress_callback, i + 1
            )
            tasks.append(task)
        
        # 모든 파일 처리 완료까지 대기
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"배치 처리 완료: {len(self.results)}개 결과")
        
        # CSV 저장
        if output_csv_path or self.results:
            csv_path = output_csv_path or self._generate_default_csv_path()
            await self.save_results_to_csv(csv_path)
        
        return self.results
    
    async def _process_single_pdf_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        file_path: str,
        custom_prompt: Optional[str],
        progress_callback: Optional[Callable[[int, int, str], None]],
        file_number: int
    ) -> None:
        """세마포어를 사용하여 단일 PDF 파일 처리"""
        async with semaphore:
            result = await self._process_single_pdf_file(file_path, custom_prompt)
            self.results.append(result)
            
            self.current_progress += 1
            if progress_callback:
                status = f"처리 완료: {result.file_name}"
                if not result.success:
                    status = f"처리 실패: {result.file_name}"
                progress_callback(self.current_progress, self.total_files, status)
    
    async def _process_single_pdf_file(
        self,
        file_path: str,
        custom_prompt: Optional[str] = None
    ) -> SimpleBatchResult:
        """
        단일 PDF 파일 처리
        
        Args:
            file_path: PDF 파일 경로
            custom_prompt: 사용자 정의 프롬프트
            
        Returns:
            처리 결과
        """
        start_time = asyncio.get_event_loop().time()
        file_name = os.path.basename(file_path)
        
        try:
            # 파일 정보 수집
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            logger.info(f"PDF 파일 처리 시작: {file_name} ({file_size_mb}MB)")
            
            # PDF를 이미지로 변환 (첫 번째 페이지만)
            images = self.pdf_processor.convert_to_images(file_path, max_pages=1)
            if not images:
                raise ValueError("PDF를 이미지로 변환할 수 없습니다")
            
            # 첫 번째 페이지 이미지를 바이트로 변환
            first_page_image = images[0]
            image_bytes = self.pdf_processor.image_to_bytes(first_page_image)
            
            # Gemini API로 분석 (비동기 처리)
            loop = asyncio.get_event_loop()
            analysis_result = await loop.run_in_executor(
                None,
                self.analyzer.analyze_image_from_bytes,
                image_bytes,
                custom_prompt,
                "image/png"
            )
            
            if analysis_result and analysis_result['success']:
                result = SimpleBatchResult(
                    file_path=file_path,
                    file_name=file_name,
                    file_size_mb=file_size_mb,
                    processing_time_seconds=0,  # 나중에 계산
                    success=True,
                    analysis_result=analysis_result['analysis_result'],
                    analysis_timestamp=analysis_result['timestamp'],
                    prompt_used=analysis_result['prompt_used'],
                    model_used=analysis_result['model'],
                    error_message=None,
                    processed_at=datetime.now().isoformat()
                )
                logger.info(f"분석 성공: {file_name}")
            else:
                error_msg = analysis_result['error_message'] if analysis_result else "알 수 없는 오류"
                result = SimpleBatchResult(
                    file_path=file_path,
                    file_name=file_name,
                    file_size_mb=file_size_mb,
                    processing_time_seconds=0,
                    success=False,
                    analysis_result=None,
                    error_message=error_msg,
                    processed_at=datetime.now().isoformat()
                )
                logger.error(f"분석 실패: {file_name} - {error_msg}")
        
        except Exception as e:
            error_msg = f"파일 처리 오류: {str(e)}"
            logger.error(f"파일 처리 오류 ({file_name}): {error_msg}")
            result = SimpleBatchResult(
                file_path=file_path,
                file_name=file_name,
                file_size_mb=0,
                processing_time_seconds=0,
                success=False,
                error_message=error_msg,
                processed_at=datetime.now().isoformat()
            )
        
        finally:
            # 처리 시간 계산
            end_time = asyncio.get_event_loop().time()
            result.processing_time_seconds = round(end_time - start_time, 2)
        
        return result
    
    async def save_results_to_csv(self, csv_path: str) -> None:
        """
        처리 결과를 CSV 파일로 저장
        
        Args:
            csv_path: 출력 CSV 파일 경로
        """
        try:
            if not self.results:
                logger.warning("저장할 결과가 없습니다.")
                return
            
            # 결과를 DataFrame으로 변환
            data_rows = []
            for result in self.results:
                row = {
                    'file_name': result.file_name,
                    'file_path': result.file_path,
                    'file_size_mb': result.file_size_mb,
                    'processing_time_seconds': result.processing_time_seconds,
                    'success': result.success,
                    'analysis_result': result.analysis_result or '',
                    'analysis_timestamp': result.analysis_timestamp or '',
                    'prompt_used': result.prompt_used or '',
                    'model_used': result.model_used or '',
                    'error_message': result.error_message or '',
                    'processed_at': result.processed_at or ''
                }
                data_rows.append(row)
            
            # DataFrame 생성
            df = pd.DataFrame(data_rows)
            
            # 컬럼 순서 정렬
            column_order = [
                'file_name', 'success', 'file_size_mb', 'processing_time_seconds',
                'analysis_result', 'prompt_used', 'model_used', 'analysis_timestamp',
                'error_message', 'processed_at', 'file_path'
            ]
            
            df = df[column_order]
            
            # 출력 디렉토리 생성
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            
            # UTF-8 BOM으로 저장 (한글 호환성)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"CSV 저장 완료: {csv_path}")
            logger.info(f"총 {len(data_rows)}개 파일 결과 저장")
            
            # 처리 요약 로그
            success_count = sum(1 for r in self.results if r.success)
            failure_count = len(self.results) - success_count
            logger.info(f"처리 요약 - 성공: {success_count}개, 실패: {failure_count}개")
            
        except Exception as e:
            logger.error(f"CSV 저장 오류: {str(e)}")
            raise
    
    def _generate_default_csv_path(self) -> str:
        """기본 CSV 파일 경로 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = "D:/MYCLAUDE_PROJECT/fletimageanalysis/results"
        os.makedirs(results_dir, exist_ok=True)
        return os.path.join(results_dir, f"simple_batch_analysis_{timestamp}.csv")
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """처리 결과 요약 정보 반환"""
        if not self.results:
            return {}
        
        total_files = len(self.results)
        success_files = sum(1 for r in self.results if r.success)
        failed_files = total_files - success_files
        
        total_processing_time = sum(r.processing_time_seconds for r in self.results)
        avg_processing_time = total_processing_time / total_files if total_files > 0 else 0
        
        total_file_size = sum(r.file_size_mb for r in self.results)
        
        return {
            'total_files': total_files,
            'success_files': success_files,
            'failed_files': failed_files,
            'total_processing_time': round(total_processing_time, 2),
            'avg_processing_time': round(avg_processing_time, 2),
            'total_file_size_mb': round(total_file_size, 2),
            'success_rate': round((success_files / total_files) * 100, 1) if total_files > 0 else 0
        }


# 사용 예시
async def main():
    """사용 예시 함수"""
    # API 키 설정 (실제 사용 시에는 .env 파일이나 환경변수 사용)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수를 설정해주세요.")
        return
    
    # 배치 처리기 초기화
    processor = SimpleBatchProcessor(api_key)
    
    # 진행률 콜백 함수
    def progress_callback(current: int, total: int, status: str):
        percentage = (current / total) * 100
        print(f"진행률: {current}/{total} ({percentage:.1f}%) - {status}")
    
    # 샘플 PDF 파일 경로 (실제 사용 시에는 실제 파일 경로로 교체)
    pdf_files = [
        "D:/MYCLAUDE_PROJECT/fletimageanalysis/testsample/sample1.pdf",
        "D:/MYCLAUDE_PROJECT/fletimageanalysis/testsample/sample2.pdf",
        # 더 많은 파일 추가 가능
    ]
    
    # 실제 존재하는 PDF 파일만 필터링
    existing_files = [f for f in pdf_files if os.path.exists(f)]
    
    if not existing_files:
        print("❌ 처리할 PDF 파일이 없습니다.")
        return
    
    # 배치 처리 실행
    results = await processor.process_multiple_pdf_files(
        pdf_file_paths=existing_files,
        custom_prompt=None,  # 기본 프롬프트 사용
        max_concurrent_files=2,
        progress_callback=progress_callback
    )
    
    # 처리 요약 출력
    summary = processor.get_processing_summary()
    print("\n=== 처리 요약 ===")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    # 비동기 메인 함수 실행
    asyncio.run(main())
