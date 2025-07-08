"""
유틸리티 함수 모듈
공통으로 사용되는 유틸리티 함수들을 제공합니다.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class FileUtils:
    """파일 관련 유틸리티 클래스"""
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """디렉토리가 존재하지 않으면 생성"""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"디렉토리 생성 실패 {directory_path}: {e}")
            return False
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """안전한 파일명 생성 (특수문자 제거)"""
        import re
        # 특수문자를 언더스코어로 치환
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 연속된 언더스코어를 하나로 축약
        safe_name = re.sub(r'_+', '_', safe_name)
        # 앞뒤 언더스코어 제거
        return safe_name.strip('_')
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """파일 크기를 MB 단위로 반환"""
        try:
            size_bytes = os.path.getsize(file_path)
            return round(size_bytes / (1024 * 1024), 2)
        except Exception:
            return 0.0
    
    @staticmethod
    def save_text_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """텍스트 파일 저장"""
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            logger.info(f"텍스트 파일 저장 완료: {file_path}")
            return True
        except Exception as e:
            logger.error(f"텍스트 파일 저장 실패 {file_path}: {e}")
            return False
    
    @staticmethod
    def save_json_file(file_path: str, data: Dict[str, Any], indent: int = 2) -> bool:
        """JSON 파일 저장"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            logger.info(f"JSON 파일 저장 완료: {file_path}")
            return True
        except Exception as e:
            logger.error(f"JSON 파일 저장 실패 {file_path}: {e}")
            return False

class AnalysisResultSaver:
    """분석 결과 저장 클래스"""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        FileUtils.ensure_directory_exists(str(self.output_dir))
    
    def save_analysis_results(
        self, 
        pdf_filename: str,
        analysis_results: Dict[int, str],
        pdf_info: Dict[str, Any],
        analysis_settings: Dict[str, Any]
    ) -> Optional[str]:
        """분석 결과를 파일로 저장"""
        try:
            # 안전한 파일명 생성
            safe_filename = FileUtils.get_safe_filename(
                Path(pdf_filename).stem
            )
            
            # 타임스탬프 추가
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"{safe_filename}_analysis_{timestamp}.txt"
            result_path = self.output_dir / result_filename
            
            # 결과 텍스트 구성
            content = self._format_analysis_content(
                pdf_filename, analysis_results, pdf_info, analysis_settings
            )
            
            # 파일 저장
            if FileUtils.save_text_file(str(result_path), content):
                return str(result_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"분석 결과 저장 중 오류: {e}")
            return None
    
    def save_analysis_json(
        self,
        pdf_filename: str,
        analysis_results: Dict[int, str],
        pdf_info: Dict[str, Any],
        analysis_settings: Dict[str, Any]
    ) -> Optional[str]:
        """분석 결과를 JSON으로 저장"""
        try:
            safe_filename = FileUtils.get_safe_filename(
                Path(pdf_filename).stem
            )
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{safe_filename}_analysis_{timestamp}.json"
            json_path = self.output_dir / json_filename
            
            # JSON 데이터 구성
            json_data = {
                "analysis_info": {
                    "pdf_filename": pdf_filename,
                    "analysis_date": datetime.datetime.now().isoformat(),
                    "total_pages_analyzed": len(analysis_results)
                },
                "pdf_info": pdf_info,
                "analysis_settings": analysis_settings,
                "results": {
                    f"page_{page_num + 1}": result 
                    for page_num, result in analysis_results.items()
                }
            }
            
            if FileUtils.save_json_file(str(json_path), json_data):
                return str(json_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"JSON 결과 저장 중 오류: {e}")
            return None
    
    def _format_analysis_content(
        self,
        pdf_filename: str,
        analysis_results: Dict[int, str],
        pdf_info: Dict[str, Any],
        analysis_settings: Dict[str, Any]
    ) -> str:
        """분석 결과를 텍스트 형식으로 포맷팅"""
        
        content = []
        
        # 헤더
        content.append("=" * 80)
        content.append("PDF 도면 분석 결과 보고서")
        content.append("=" * 80)
        content.append("")
        
        # 기본 정보
        content.append("📄 파일 정보")
        content.append("-" * 40)
        content.append(f"파일명: {pdf_filename}")
        content.append(f"총 페이지 수: {pdf_info.get('page_count', 'N/A')}")
        content.append(f"파일 크기: {pdf_info.get('file_size', 'N/A')} bytes")
        content.append(f"분석 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # 분석 설정
        content.append("⚙️ 분석 설정")
        content.append("-" * 40)
        for key, value in analysis_settings.items():
            content.append(f"{key}: {value}")
        content.append("")
        
        # 분석 결과
        content.append("🔍 분석 결과")
        content.append("-" * 40)
        
        for page_num, result in analysis_results.items():
            content.append(f"\n📋 페이지 {page_num + 1} 분석 결과:")
            content.append("=" * 50)
            content.append(result)
            content.append("")
        
        # 푸터
        content.append("=" * 80)
        content.append("분석 완료")
        content.append("=" * 80)
        
        return "\n".join(content)

class DateTimeUtils:
    """날짜/시간 관련 유틸리티 클래스"""
    
    @staticmethod
    def get_timestamp() -> str:
        """현재 타임스탬프 반환 (YYYY-MM-DD HH:MM:SS 형식)"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_filename_timestamp() -> str:
        """파일명용 타임스탬프 반환 (YYYYMMDD_HHMMSS 형식)"""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """초를 읽기 쉬운 형식으로 변환"""
        if seconds < 60:
            return f"{seconds:.1f}초"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}분"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}시간"

class TextUtils:
    """텍스트 처리 유틸리티 클래스"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """텍스트를 지정된 길이로 자르기"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def clean_text(text: str) -> str:
        """텍스트 정리 (불필요한 공백 제거 등)"""
        import re
        # 연속된 공백을 하나로 축약
        text = re.sub(r'\s+', ' ', text)
        # 앞뒤 공백 제거
        return text.strip()
    
    @staticmethod
    def word_count(text: str) -> int:
        """단어 수 계산"""
        return len(text.split())
    
    @staticmethod
    def char_count(text: str, exclude_spaces: bool = False) -> int:
        """문자 수 계산"""
        if exclude_spaces:
            return len(text.replace(' ', ''))
        return len(text)

class ValidationUtils:
    """검증 관련 유틸리티 클래스"""
    
    @staticmethod
    def is_valid_api_key(api_key: str) -> bool:
        """API 키 형식 검증"""
        if not api_key or not isinstance(api_key, str):
            return False
        # 기본적인 형식 검증 (실제 검증은 API 호출 시 수행)
        return len(api_key.strip()) > 10
    
    @staticmethod
    def is_valid_file_size(file_size_bytes: int, max_size_mb: int) -> bool:
        """파일 크기 검증"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size_bytes <= max_size_bytes
    
    @staticmethod
    def is_valid_pdf_extension(filename: str) -> bool:
        """PDF 파일 확장자 검증"""
        return Path(filename).suffix.lower() == '.pdf'

# 사용 예시
if __name__ == "__main__":
    # 파일 유틸리티 테스트
    print("유틸리티 함수 테스트:")
    print(f"타임스탬프: {DateTimeUtils.get_timestamp()}")
    print(f"파일명 타임스탬프: {DateTimeUtils.get_filename_timestamp()}")
    print(f"안전한 파일명: {FileUtils.get_safe_filename('test<file>name.pdf')}")
    print(f"텍스트 축약: {TextUtils.truncate_text('이것은 긴 텍스트입니다' * 10, 50)}")
