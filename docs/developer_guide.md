# 개발자 가이드

PDF 도면 분석기의 개발 및 확장을 위한 가이드입니다.

## 목차
1. [프로젝트 구조](#프로젝트-구조)
2. [개발 환경 설정](#개발-환경-설정)
3. [모듈 구조](#모듈-구조)
4. [API 참조](#api-참조)
5. [확장 가이드](#확장-가이드)
6. [기여하기](#기여하기)

## 프로젝트 구조

```
fletimageanalysis/
├── main.py                 # 메인 애플리케이션 진입점
├── config.py               # 설정 관리 모듈
├── pdf_processor.py        # PDF 처리 및 이미지 변환
├── gemini_analyzer.py      # Gemini API 연동
├── ui_components.py        # UI 컴포넌트 정의
├── utils.py                # 유틸리티 함수들
├── setup.py                # 설치 스크립트
├── test_project.py         # 테스트 스크립트
├── requirements.txt        # Python 의존성
├── .env.example            # 환경 변수 템플릿
├── README.md               # 프로젝트 개요
├── LICENSE                 # 라이선스
├── project_plan.md         # 프로젝트 계획
├── uploads/                # 업로드된 파일 저장
├── results/                # 분석 결과 저장
├── assets/                 # 정적 자산
└── docs/                   # 문서
    ├── user_guide.md       # 사용자 가이드
    └── developer_guide.md  # 개발자 가이드
```

## 개발 환경 설정

### 필수 요구사항
- Python 3.9+
- pip 최신 버전
- Google Gemini API 키

### 개발 환경 구성

1. **저장소 클론**
```bash
git clone <repository-url>
cd fletimageanalysis
```

2. **가상 환경 생성**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **개발 의존성 설치**
```bash
pip install -r requirements.txt
pip install black flake8 pytest  # 개발 도구
```

4. **환경 설정**
```bash
cp .env.example .env
# .env 파일에서 GEMINI_API_KEY 설정
```

### 코드 스타일

프로젝트는 다음 코딩 스타일을 따릅니다:

- **포맷터**: Black
- **린터**: Flake8
- **라인 길이**: 88자
- **문서화**: Google 스타일 docstring

```bash
# 코드 포맷팅
black .

# 코드 검사
flake8 .

# 테스트 실행
python test_project.py
```

## 모듈 구조

### 1. config.py - 설정 관리

```python
class Config:
    """애플리케이션 설정 클래스"""
    
    # 기본 설정
    APP_TITLE = "PDF 도면 분석기"
    APP_VERSION = "1.0.0"
    
    # API 설정
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"
    
    # 파일 설정
    MAX_FILE_SIZE_MB = 50
    ALLOWED_EXTENSIONS = ["pdf"]
```

**주요 기능:**
- 환경 변수 로드
- 설정 유효성 검사
- 경로 관리

### 2. pdf_processor.py - PDF 처리

```python
class PDFProcessor:
    """PDF 파일 처리 클래스"""
    
    def validate_pdf_file(self, file_path: str) -> bool:
        """PDF 파일 유효성 검사"""
        
    def convert_pdf_page_to_image(self, file_path: str, page_number: int) -> Image:
        """PDF 페이지를 PIL Image로 변환"""
        
    def pdf_page_to_base64(self, file_path: str, page_number: int) -> str:
        """PDF 페이지를 base64 문자열로 변환"""
```

**주요 기능:**
- PDF 파일 검증
- 페이지별 이미지 변환
- Base64 인코딩
- 메타데이터 추출

### 3. gemini_analyzer.py - API 연동

```python
class GeminiAnalyzer:
    """Gemini API 이미지 분석 클래스"""
    
    def analyze_image_from_base64(self, base64_data: str, prompt: str) -> str:
        """Base64 이미지 데이터 분석"""
        
    def analyze_pdf_images(self, base64_images: list, prompt: str) -> dict:
        """여러 PDF 페이지 일괄 분석"""
```

**주요 기능:**
- API 클라이언트 관리
- 이미지 분석 요청
- 응답 처리
- 오류 처리

### 4. ui_components.py - UI 컴포넌트

```python
class UIComponents:
    """UI 컴포넌트 클래스"""
    
    @staticmethod
    def create_app_bar() -> ft.AppBar:
        """애플리케이션 상단 바 생성"""
        
    @staticmethod
    def create_file_upload_section() -> ft.Container:
        """파일 업로드 섹션 생성"""
```

**주요 기능:**
- 재사용 가능한 UI 컴포넌트
- Material Design 스타일
- 이벤트 핸들러 정의

### 5. utils.py - 유틸리티

```python
class FileUtils:
    """파일 관련 유틸리티"""
    
class AnalysisResultSaver:
    """분석 결과 저장"""
    
class DateTimeUtils:
    """날짜/시간 유틸리티"""
```

**주요 기능:**
- 파일 조작
- 결과 저장
- 텍스트 처리
- 검증 함수

## API 참조

### PDFProcessor

#### `validate_pdf_file(file_path: str) -> bool`
PDF 파일의 유효성을 검사합니다.

**매개변수:**
- `file_path`: PDF 파일 경로

**반환값:**
- `bool`: 유효한 PDF인지 여부

#### `get_pdf_info(file_path: str) -> dict`
PDF 파일의 메타데이터를 조회합니다.

**반환값:**
```python
{
    'page_count': int,
    'metadata': dict,
    'file_size': int,
    'filename': str
}
```

### GeminiAnalyzer

#### `analyze_image_from_base64(base64_data: str, prompt: str) -> str`
Base64 이미지를 분석합니다.

**매개변수:**
- `base64_data`: Base64로 인코딩된 이미지
- `prompt`: 분석 요청 텍스트

**반환값:**
- `str`: 분석 결과 텍스트

### AnalysisResultSaver

#### `save_analysis_results(pdf_filename, analysis_results, pdf_info, analysis_settings) -> str`
분석 결과를 텍스트 파일로 저장합니다.

**반환값:**
- `str`: 저장된 파일 경로

## 확장 가이드

### 새로운 분석 모드 추가

1. **UI 업데이트**
```python
# ui_components.py에서 새 라디오 버튼 추가
ft.Radio(value="new_mode", label="새로운 모드")
```

2. **분석 로직 추가**
```python
# main.py의 run_analysis()에서 프롬프트 설정
elif self.analysis_mode.value == "new_mode":
    prompt = "새로운 분석 모드의 프롬프트"
```

### 새로운 파일 형식 지원

1. **설정 업데이트**
```python
# config.py
ALLOWED_EXTENSIONS = ["pdf", "docx"]  # 새 형식 추가
```

2. **처리기 확장**
```python
# 새로운 처리 클래스 구현
class DOCXProcessor:
    def validate_docx_file(self, file_path: str) -> bool:
        # DOCX 검증 로직
        pass
```

### 새로운 AI 모델 지원

1. **설정 추가**
```python
# config.py
ALTERNATIVE_MODEL = "claude-3-5-sonnet"
```

2. **분석기 확장**
```python
class ClaudeAnalyzer:
    def analyze_image(self, image_data: str) -> str:
        # Claude API 연동 로직
        pass
```

### UI 컴포넌트 확장

1. **새 컴포넌트 추가**
```python
# ui_components.py
@staticmethod
def create_advanced_settings_section() -> ft.Container:
    """고급 설정 섹션"""
    return ft.Container(...)
```

2. **메인 UI에 통합**
```python
# main.py의 build_ui()에서 새 컴포넌트 추가
```

## 기여하기

### 기여 프로세스

1. **이슈 생성**
   - 새 기능이나 버그 리포트
   - 명확한 설명과 예시 제공

2. **브랜치 생성**
```bash
git checkout -b feature/new-feature
git checkout -b bugfix/fix-issue
```

3. **개발 및 테스트**
```bash
# 개발 후 테스트 실행
python test_project.py
black .
flake8 .
```

4. **커밋 및 푸시**
```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

5. **Pull Request 생성**
   - 명확한 제목과 설명
   - 변경사항 설명
   - 테스트 결과 포함

### 커밋 메시지 규칙

- `feat:` 새로운 기능
- `fix:` 버그 수정
- `docs:` 문서 업데이트
- `style:` 코드 스타일 변경
- `refactor:` 코드 리팩토링
- `test:` 테스트 추가/수정
- `chore:` 기타 작업

### 코드 리뷰 체크리스트

- [ ] 코드 스타일 준수 (Black, Flake8)
- [ ] 테스트 통과
- [ ] 문서화 완료
- [ ] 타입 힌트 추가
- [ ] 에러 처리 적절
- [ ] 성능 고려
- [ ] 보안 검토

## 디버깅

### 로깅 설정

```python
import logging

# 개발 시 상세 로깅
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 일반적인 디버깅 시나리오

1. **API 연결 문제**
```python
# gemini_analyzer.py에서 연결 테스트
if not analyzer.validate_api_connection():
    logger.error("API 연결 실패")
```

2. **파일 처리 오류**
```python
# pdf_processor.py에서 상세 오류 정보
try:
    doc = fitz.open(file_path)
except Exception as e:
    logger.error(f"PDF 열기 실패: {e}")
```

3. **UI 업데이트 문제**
```python
# main.py에서 스레드 안전 업데이트
def safe_ui_update():
    def update():
        # UI 업데이트 코드
        self.page.update()
    
    self.page.run_thread(update)
```

## 성능 최적화

### 메모리 관리

1. **대용량 PDF 처리**
```python
# 페이지별 순차 처리
for page_num in range(total_pages):
    # 메모리 해제
    del previous_image
    gc.collect()
```

2. **이미지 크기 최적화**
```python
# 적절한 줌 레벨 선택
zoom = min(2.0, target_width / pdf_width)
```

### API 호출 최적화

1. **요청 배치 처리**
```python
# 여러 페이지를 하나의 요청으로 처리
combined_prompt = f"다음 {len(images)}개 이미지를 분석..."
```

2. **캐싱 구현**
```python
# 분석 결과 캐시
@lru_cache(maxsize=100)
def cached_analysis(image_hash: str, prompt: str) -> str:
    return analyzer.analyze_image(image_data, prompt)
```

---

더 자세한 정보나 질문이 있으시면 GitHub Issues에서 문의해 주세요.
