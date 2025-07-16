"""
설정 관리 모듈
환경 변수 및 애플리케이션 설정을 관리합니다.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드
load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    
    # 기본 애플리케이션 설정
    APP_TITLE = os.getenv("APP_TITLE", "PDF/DXF 도면 분석기")
    APP_VERSION = os.getenv("APP_VERSION", "1.1.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # API 설정
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    DEFAULT_PROMPT = os.getenv(
        "DEFAULT_PROMPT", 
        "pdf 이미지 분석하여 도면인지 어떤 정보들이 있는지 알려줘.structured_output 이외에 정보도 기타에 넣어줘."
    )
    
    # 파일 업로드 설정
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,dxf").split(",")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    
    # 경로 설정
    BASE_DIR = Path(__file__).parent
    UPLOAD_DIR = BASE_DIR / UPLOAD_FOLDER
    ASSETS_DIR = BASE_DIR / "assets"
    RESULTS_FOLDER = BASE_DIR / "results"
    
    @classmethod
    def validate_config(cls):
        """설정 유효성 검사"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY가 설정되지 않았습니다.")
            
        if not cls.UPLOAD_DIR.exists():
            try:
                cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"업로드 폴더 생성 실패: {e}")
                
        return errors
    
    @classmethod
    def get_file_size_limit_bytes(cls):
        """파일 크기 제한을 바이트로 반환"""
        return cls.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @classmethod
    def get_gemini_api_key(cls):
        """Gemini API 키 반환"""
        return cls.GEMINI_API_KEY

# 설정 검증
if __name__ == "__main__":
    config_errors = Config.validate_config()
    if config_errors:
        print("설정 오류:")
        for error in config_errors:
            print(f"  - {error}")
    else:
        print("설정이 올바르게 구성되었습니다.")
