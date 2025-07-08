# PDF 도면 분석기

Flet 기반의 PDF 업로드 및 Gemini API 이미지 분석 애플리케이션입니다. PDF 파일의 도면, 문서, 이미지를 Google Gemini AI를 통해 분석하여 상세한 정보를 제공합니다.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flet](https://img.shields.io/badge/Flet-0.25.1+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 주요 기능

- 📄 **PDF 파일 업로드**: 간편한 드래그 앤 드롭 인터페이스
- 🔍 **AI 이미지 분석**: Google Gemini API를 통한 고급 이미지 분석
- 📊 **실시간 진행률**: 분석 과정을 실시간으로 확인
- 🎨 **현대적인 UI**: Material Design 기반의 직관적인 인터페이스
- ⚙️ **다양한 분석 모드**: 기본, 상세, 사용자 정의 분석
- 💾 **결과 저장**: 분석 결과를 텍스트 파일로 저장
- 👁️ **PDF 미리보기**: 업로드된 PDF의 미리보기 제공

## 🚀 빠른 시작

### 1. 요구 사항

- Python 3.9 이상
- Google Gemini API 키

### 2. 설치

```bash
# 저장소 클론
git clone https://github.com/your-username/pdf-analyzer.git
cd pdf-analyzer

# 가상 환경 생성 (권장)
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정

1. `.env.example` 파일을 `.env`로 복사:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

2. `.env` 파일을 편집하여 Gemini API 키 설정:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. 실행

```bash
python main.py
```

## 🛠️ 설정

### 환경 변수

`.env` 파일에서 다음 설정을 조정할 수 있습니다:

```env
# 필수: Gemini API 키
GEMINI_API_KEY=your_gemini_api_key

# 애플리케이션 설정
APP_TITLE=PDF 도면 분석기
APP_VERSION=1.0.0
DEBUG=False

# 파일 업로드 설정
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf
UPLOAD_FOLDER=uploads

# Gemini API 설정
GEMINI_MODEL=gemini-2.5-flash-preview-04-17
DEFAULT_PROMPT=pdf 이미지 분석하여 도면인지 어떤 정보들이 있는지 알려줘.
```

### Gemini API 키 획득

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 API 키를 `.env` 파일에 추가

## 📖 사용법

### 기본 사용법

1. **PDF 파일 선택**: "PDF 파일 선택" 버튼을 클릭하여 분석할 PDF 파일을 선택합니다.

2. **분석 설정**: 
   - **페이지 선택**: 첫 번째 페이지만 또는 모든 페이지 분석 선택
   - **분석 모드**: 기본, 상세, 사용자 정의 중 선택

3. **분석 시작**: "분석 시작" 버튼을 클릭하여 AI 분석을 시작합니다.

4. **결과 확인**: 분석 완료 후 결과를 확인하고 필요시 저장합니다.

### 분석 모드

- **기본 분석**: 문서 유형 및 기본 정보 분석
- **상세 분석**: 도면, 도표, 텍스트 등 상세 정보 분석  
- **사용자 정의**: 원하는 분석 내용을 직접 입력

## 🏗️ 프로젝트 구조

```
fletimageanalysis/
├── main.py              # 메인 애플리케이션
├── config.py            # 설정 관리
├── pdf_processor.py     # PDF 처리 모듈
├── gemini_analyzer.py   # Gemini API 연동
├── ui_components.py     # UI 컴포넌트
├── requirements.txt     # 의존성 목록
├── .env.example         # 환경 변수 템플릿
├── uploads/            # 업로드 폴더
├── assets/             # 자산 폴더
└── docs/               # 문서 폴더
```

## 🔧 개발

### 개발 환경 설정

```bash
# 개발용 의존성 설치
pip install black flake8 pytest

# 코드 포맷팅
black .

# 코드 검사
flake8 .

# 테스트 실행
pytest
```

### 모듈 설명

#### `pdf_processor.py`
- PDF 파일 검증 및 정보 추출
- PDF 페이지를 이미지로 변환
- Base64 인코딩 처리

#### `gemini_analyzer.py`
- Gemini API 클라이언트 관리
- 이미지 분석 요청 및 응답 처리
- 스트리밍 분석 지원

#### `ui_components.py`
- Flet UI 컴포넌트 정의
- 재사용 가능한 UI 요소들
- Material Design 스타일 적용

#### `main.py`
- 메인 애플리케이션 로직
- 이벤트 처리 및 UI 통합
- 백그라운드 작업 관리

## 🐛 문제 해결

### 일반적인 문제들

**1. API 키 오류**
```
오류: Gemini API 키가 설정되지 않았습니다.
해결: .env 파일에 올바른 GEMINI_API_KEY를 설정하세요.
```

**2. PDF 파일 오류**
```
오류: 유효하지 않은 PDF 파일입니다.
해결: 손상되지 않은 PDF 파일을 사용하거나 다른 PDF로 시도하세요.
```

**3. 의존성 설치 오류**
```bash
# PyMuPDF 설치 문제가 있을 경우
pip install --upgrade pip
pip install PyMuPDF --no-cache-dir
```

**4. 메모리 부족 오류**
```
해결: 큰 PDF 파일의 경우 첫 번째 페이지만 분석하거나 
      zoom 값을 낮춰서 이미지 크기를 줄이세요.
```

### 로그 확인

애플리케이션 실행 시 콘솔에서 상세한 로그를 확인할 수 있습니다:

```bash
python main.py 2>&1 | tee app.log
```

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성합니다

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- [Flet](https://flet.dev/) - 뛰어난 Python UI 프레임워크
- [Google Gemini](https://ai.google.dev/) - 강력한 AI 분석 API
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF 처리 라이브러리

## 📞 지원

문제가 있거나 질문이 있으시면 [Issues](https://github.com/your-username/pdf-analyzer/issues) 페이지에서 이슈를 생성해 주세요.

---

**🔗 관련 링크**
- [Flet 문서](https://flet.dev/docs/)
- [Gemini API 문서](https://ai.google.dev/gemini-api/docs)
- [PyMuPDF 문서](https://pymupdf.readthedocs.io/)
