"""
테스트 스크립트
프로젝트의 핵심 기능들을 테스트합니다.
"""

import sys
import os
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """설정 모듈 테스트"""
    print("=" * 50)
    print("설정 모듈 테스트")
    print("=" * 50)
    
    try:
        from config import Config
        
        print(f"✅ 앱 제목: {Config.APP_TITLE}")
        print(f"✅ 앱 버전: {Config.APP_VERSION}")
        print(f"✅ 업로드 폴더: {Config.UPLOAD_FOLDER}")
        print(f"✅ 최대 파일 크기: {Config.MAX_FILE_SIZE_MB}MB")
        print(f"✅ 허용 확장자: {Config.ALLOWED_EXTENSIONS}")
        print(f"✅ Gemini 모델: {Config.GEMINI_MODEL}")
        
        # 설정 검증
        errors = Config.validate_config()
        if errors:
            print("❌ 설정 오류:")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ 모든 설정이 올바릅니다.")
            return True
            
    except Exception as e:
        print(f"❌ 설정 모듈 테스트 실패: {e}")
        return False

def test_pdf_processor():
    """PDF 처리 모듈 테스트"""
    print("\\n" + "=" * 50)
    print("PDF 처리 모듈 테스트")
    print("=" * 50)
    
    try:
        from pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        print("✅ PDF 처리기 초기화 성공")
        
        # 테스트용 임시 PDF 생성 (실제로는 존재하지 않음)
        test_pdf = "test_sample.pdf"
        
        # 존재하지 않는 파일 테스트
        result = processor.validate_pdf_file(test_pdf)
        if not result:
            print("✅ 존재하지 않는 파일 검증: 정상 동작")
        else:
            print("❌ 존재하지 않는 파일 검증: 비정상 동작")
            
        # 확장자 검증 테스트
        if not processor.validate_pdf_file("test.txt"):
            print("✅ 잘못된 확장자 검증: 정상 동작")
        else:
            print("❌ 잘못된 확장자 검증: 비정상 동작")
            
        # base64 변환 테스트 (PIL Image 사용)
        try:
            from PIL import Image
            import io
            
            # 작은 테스트 이미지 생성
            test_image = Image.new('RGB', (100, 100), color='red')
            base64_result = processor.image_to_base64(test_image)
            
            if base64_result and len(base64_result) > 0:
                print("✅ Base64 변환: 정상 동작")
            else:
                print("❌ Base64 변환: 실패")
                
        except Exception as e:
            print(f"❌ Base64 변환 테스트 실패: {e}")
            
        print("✅ PDF 처리 모듈 기본 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ PDF 처리 모듈 테스트 실패: {e}")
        return False

def test_gemini_analyzer():
    """Gemini 분석기 테스트"""
    print("\\n" + "=" * 50)
    print("Gemini 분석기 테스트")
    print("=" * 50)
    
    try:
        from config import Config
        
        # API 키 확인
        if not Config.GEMINI_API_KEY:
            print("❌ Gemini API 키가 설정되지 않았습니다.")
            print("   .env 파일에 GEMINI_API_KEY를 설정하세요.")
            return False
            
        from gemini_analyzer import GeminiAnalyzer
        
        analyzer = GeminiAnalyzer()
        print("✅ Gemini 분석기 초기화 성공")
        
        # API 연결 테스트
        if analyzer.validate_api_connection():
            print("✅ Gemini API 연결 테스트 성공")
        else:
            print("❌ Gemini API 연결 테스트 실패")
            return False
            
        # 모델 정보 확인
        model_info = analyzer.get_model_info()
        print(f"✅ 사용 모델: {model_info['model']}")
        print(f"✅ API 키 길이: {model_info['api_key_length']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini 분석기 테스트 실패: {e}")
        return False

def test_utils():
    """유틸리티 모듈 테스트"""
    print("\\n" + "=" * 50)
    print("유틸리티 모듈 테스트")
    print("=" * 50)
    
    try:
        from utils import FileUtils, DateTimeUtils, TextUtils, ValidationUtils
        
        # 파일 유틸리티 테스트
        safe_name = FileUtils.get_safe_filename("test<file>name?.pdf")
        print(f"✅ 안전한 파일명 생성: '{safe_name}'")
        
        # 날짜/시간 유틸리티 테스트
        timestamp = DateTimeUtils.get_timestamp()
        filename_timestamp = DateTimeUtils.get_filename_timestamp()
        print(f"✅ 타임스탬프: {timestamp}")
        print(f"✅ 파일명 타임스탬프: {filename_timestamp}")
        
        # 텍스트 유틸리티 테스트
        long_text = "이것은 긴 텍스트입니다. " * 10
        truncated = TextUtils.truncate_text(long_text, 50)
        print(f"✅ 텍스트 축약: '{truncated}'")
        
        # 검증 유틸리티 테스트
        is_valid_pdf = ValidationUtils.is_valid_pdf_extension("test.pdf")
        is_invalid_pdf = ValidationUtils.is_valid_pdf_extension("test.txt")
        print(f"✅ PDF 확장자 검증: {is_valid_pdf} / {not is_invalid_pdf}")
        
        return True
        
    except Exception as e:
        print(f"❌ 유틸리티 모듈 테스트 실패: {e}")
        return False

def test_file_structure():
    """파일 구조 테스트"""
    print("\\n" + "=" * 50)
    print("파일 구조 테스트")
    print("=" * 50)
    
    required_files = [
        "main.py",
        "config.py", 
        "pdf_processor.py",
        "gemini_analyzer.py",
        "ui_components.py",
        "utils.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "project_plan.md"
    ]
    
    required_dirs = [
        "uploads",
        "assets",
        "docs"
    ]
    
    missing_files = []
    missing_dirs = []
    
    # 파일 확인
    for file in required_files:
        if not (project_root / file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    # 디렉토리 확인
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            missing_dirs.append(dir_name)
        else:
            print(f"✅ {dir_name}/")
    
    if missing_files:
        print("❌ 누락된 파일:")
        for file in missing_files:
            print(f"   - {file}")
    
    if missing_dirs:
        print("❌ 누락된 디렉토리:")
        for dir_name in missing_dirs:
            print(f"   - {dir_name}/")
    
    return len(missing_files) == 0 and len(missing_dirs) == 0

def test_dependencies():
    """의존성 테스트"""
    print("\\n" + "=" * 50)
    print("의존성 테스트")
    print("=" * 50)
    
    required_packages = [
        "flet",
        "google.genai",
        "fitz",  # PyMuPDF
        "PIL",   # Pillow
        "dotenv" # python-dotenv
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "fitz":
                import fitz
            elif package == "PIL":
                import PIL
            elif package == "dotenv":
                import dotenv
            elif package == "google.genai":
                import google.genai
            else:
                __import__(package)
                
            print(f"✅ {package}")
            
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 설치되지 않음")
    
    if missing_packages:
        print("\\n설치가 필요한 패키지:")
        print("pip install " + " ".join(missing_packages))
        return False
    else:
        print("\\n✅ 모든 의존성이 설치되어 있습니다.")
        return True

def main():
    """메인 테스트 함수"""
    print("PDF 도면 분석기 - 테스트 스크립트")
    print("=" * 80)
    
    tests = [
        ("파일 구조", test_file_structure),
        ("의존성", test_dependencies),
        ("설정 모듈", test_config),
        ("PDF 처리 모듈", test_pdf_processor),
        ("유틸리티 모듈", test_utils),
        ("Gemini 분석기", test_gemini_analyzer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\\n✅ {test_name} 테스트 통과")
            else:
                print(f"\\n❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"\\n❌ {test_name} 테스트 오류: {e}")
    
    print("\\n" + "=" * 80)
    print(f"테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 통과했습니다!")
        print("애플리케이션 실행 준비가 완료되었습니다.")
        print("\\n실행 방법:")
        print("python main.py")
    else:
        print("⚠️  일부 테스트가 실패했습니다.")
        print("실패한 테스트를 확인하고 문제를 해결하세요.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
