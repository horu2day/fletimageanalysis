#!/usr/bin/env python3
"""
간단한 배치 처리 앱 실행기
getcode.py 스타일의 간단한 PDF 분석을 여러 파일에 적용

실행 방법:
python run_simple_batch.py
"""

import subprocess
import sys
import os

def run_simple_batch_app():
    """간단한 배치 분석 앱 실행"""
    try:
        # 현재 디렉토리로 이동
        os.chdir("D:/MYCLAUDE_PROJECT/fletimageanalysis")
        
        print("🚀 간단한 배치 PDF 분석기 시작 중...")
        print("📂 작업 디렉토리:", os.getcwd())
        
        # simple_batch_analyzer_app.py 실행
        result = subprocess.run([
            sys.executable, 
            "simple_batch_analyzer_app.py"
        ], check=True)
        
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        return False
    except FileNotFoundError:
        print("❌ simple_batch_analyzer_app.py 파일을 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"❌ 예기치 않은 오류: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("📊 간단한 PDF 배치 분석기")
    print("🎯 getcode.py 스타일 → 여러 파일 → CSV 출력")
    print("=" * 50)
    
    success = run_simple_batch_app()
    
    if success:
        print("✅ 애플리케이션이 성공적으로 실행되었습니다!")
    else:
        print("❌ 애플리케이션 실행에 실패했습니다.")
        print("\n🔧 해결 방법:")
        print("1. GEMINI_API_KEY 환경변수가 설정되어 있는지 확인")
        print("2. requirements.txt 패키지들이 설치되어 있는지 확인")
        print("3. D:/MYCLAUDE_PROJECT/fletimageanalysis 폴더에서 실행")
