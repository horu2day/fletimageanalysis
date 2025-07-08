"""
설치 및 설정 가이드 스크립트
프로젝트 설치와 초기 설정을 도와주는 스크립트입니다.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """헤더 출력"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_step(step_num, title):
    """단계 출력"""
    print(f"\n📋 단계 {step_num}: {title}")
    print("-" * 40)

def check_python_version():
    """Python 버전 확인"""
    print_step(1, "Python 버전 확인")
    
    version = sys.version_info
    print(f"현재 Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 이상이 필요합니다.")
        print("https://www.python.org/downloads/ 에서 최신 버전을 다운로드하세요.")
        return False
    else:
        print("✅ Python 버전이 요구사항을 만족합니다.")
        return True

def check_pip():
    """pip 확인 및 업그레이드"""
    print_step(2, "pip 확인 및 업그레이드")
    
    try:
        # pip 버전 확인
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        print(f"pip 버전: {result.stdout.strip()}")
        
        # pip 업그레이드
        print("pip를 최신 버전으로 업그레이드 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        print("✅ pip 업그레이드 완료")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ pip 업그레이드 실패: {e}")
        return False

def create_virtual_environment():
    """가상 환경 생성 (선택 사항)"""
    print_step(3, "가상 환경 생성 (권장)")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("⚠️  가상 환경이 이미 존재합니다.")
        response = input("기존 가상 환경을 삭제하고 새로 만드시겠습니까? (y/N): ")
        if response.lower() == 'y':
            shutil.rmtree(venv_path)
        else:
            print("기존 가상 환경을 사용합니다.")
            return True
    
    try:
        print("가상 환경 생성 중...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ 가상 환경 생성 완료")
        
        # 활성화 안내
        if os.name == 'nt':  # Windows
            print("\n가상 환경 활성화 방법:")
            print("  venv\\Scripts\\activate")
        else:  # macOS/Linux
            print("\n가상 환경 활성화 방법:")
            print("  source venv/bin/activate")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 가상 환경 생성 실패: {e}")
        return False

def install_dependencies():
    """의존성 설치"""
    print_step(4, "의존성 설치")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt 파일을 찾을 수 없습니다.")
        return False
    
    try:
        print("의존성 패키지 설치 중...")
        print("(이 과정은 몇 분 정도 걸릴 수 있습니다)")
        
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ 모든 의존성 설치 완료")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 의존성 설치 실패: {e}")
        return False

def setup_environment_file():
    """환경 변수 파일 설정"""
    print_step(5, "환경 변수 설정")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ .env.example 파일을 찾을 수 없습니다.")
        return False
    
    if env_file.exists():
        print("⚠️  .env 파일이 이미 존재합니다.")
        response = input("기존 .env 파일을 덮어쓰시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("기존 .env 파일을 사용합니다.")
            return True
    
    try:
        # .env.example을 .env로 복사
        shutil.copy2(env_example, env_file)
        print("✅ .env 파일 생성 완료")
        
        print("\n⚠️  중요: Gemini API 키를 설정해야 합니다!")
        print("1. Google AI Studio에서 API 키를 발급받으세요:")
        print("   https://makersuite.google.com/app/apikey")
        print("2. .env 파일을 열어 GEMINI_API_KEY를 설정하세요:")
        print("   GEMINI_API_KEY=your_actual_api_key_here")
        
        return True
        
    except Exception as e:
        print(f"❌ .env 파일 설정 실패: {e}")
        return False

def create_directories():
    """필요한 디렉토리 생성"""
    print_step(6, "필요한 디렉토리 생성")
    
    directories = ["uploads", "results", "assets", "docs"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {dir_name}/ 디렉토리 생성")
        else:
            print(f"✅ {dir_name}/ 디렉토리 이미 존재")
    
    return True

def run_tests():
    """테스트 실행"""
    print_step(7, "설치 확인 테스트")
    
    test_script = Path("test_project.py")
    
    if not test_script.exists():
        print("❌ 테스트 스크립트를 찾을 수 없습니다.")
        return False
    
    try:
        print("설치 상태를 확인하는 테스트를 실행합니다...")
        result = subprocess.run([sys.executable, "test_project.py"], 
                               capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("오류:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 테스트 실행 실패: {e}")
        return False

def print_final_instructions():
    """최종 안내사항 출력"""
    print_header("설치 완료!")
    
    print("🎉 PDF 도면 분석기 설치가 완료되었습니다!")
    print("\n다음 단계:")
    print("1. .env 파일을 열어 Gemini API 키를 설정하세요")
    print("2. 가상 환경을 활성화하세요 (사용하는 경우)")
    print("3. 애플리케이션을 실행하세요:")
    print("   python main.py")
    
    print("\n📚 추가 정보:")
    print("- README.md: 사용법 및 문제 해결")
    print("- project_plan.md: 프로젝트 계획 및 진행 상황")
    print("- test_project.py: 테스트 스크립트")
    
    print("\n🔧 문제가 발생하면:")
    print("1. python test_project.py 를 실행하여 문제를 확인하세요")
    print("2. .env 파일의 API 키 설정을 확인하세요")
    print("3. 가상 환경이 활성화되어 있는지 확인하세요")

def main():
    """메인 설치 함수"""
    print_header("PDF 도면 분석기 설치 스크립트")
    print("이 스크립트는 PDF 도면 분석기 설치를 도와드립니다.")
    print("각 단계를 순차적으로 진행합니다.")
    
    response = input("\n설치를 시작하시겠습니까? (Y/n): ")
    if response.lower() == 'n':
        print("설치가 취소되었습니다.")
        return
    
    # 설치 단계들
    steps = [
        ("Python 버전 확인", check_python_version),
        ("pip 확인 및 업그레이드", check_pip),
        ("가상 환경 생성", create_virtual_environment),
        ("의존성 설치", install_dependencies),
        ("환경 변수 설정", setup_environment_file),
        ("디렉토리 생성", create_directories),
        ("설치 확인 테스트", run_tests)
    ]
    
    completed = 0
    
    for step_name, step_func in steps:
        try:
            if step_func():
                completed += 1
            else:
                print(f"\n❌ {step_name} 단계에서 문제가 발생했습니다.")
                response = input("계속 진행하시겠습니까? (y/N): ")
                if response.lower() != 'y':
                    break
        except KeyboardInterrupt:
            print("\n\n설치가 중단되었습니다.")
            return
        except Exception as e:
            print(f"\n❌ {step_name} 단계에서 예상치 못한 오류가 발생했습니다: {e}")
            response = input("계속 진행하시겠습니까? (y/N): ")
            if response.lower() != 'y':
                break
    
    print(f"\n설치 진행률: {completed}/{len(steps)} 단계 완료")
    
    if completed == len(steps):
        print_final_instructions()
    else:
        print("\n⚠️  설치가 완전히 완료되지 않았습니다.")
        print("문제를 해결한 후 다시 실행하거나 수동으로 남은 단계를 진행하세요.")

if __name__ == "__main__":
    main()
