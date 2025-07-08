# Flet 기반 PDF 입력 및 Gemini API 이미지 분석 UI 프로젝트 계획

## 1. 프로젝트 목표
Flet 프레임워크를 사용하여 사용자가 PDF 파일을 업로드하고, 업로드된 PDF의 이미지를 Gemini API를 통해 분석하여 결과를 UI에 표시하는 애플리케이션을 개발합니다.

## 2. 기술 스택
- **UI 프레임워크**: Flet v0.25.1+
- **API 연동**: Google Gemini API (Python SDK - google-genai v1.0+)
- **PDF 처리**: PyMuPDF v1.26.3+ 또는 pdf2image v1.17.0+
- **데이터 인코딩**: base64 (Python 내장 라이브러리)
- **환경 변수 관리**: python-dotenv v1.0.0+
- **UI 디자인**: Flet Material Library (선택 사항)

## 3. 프로젝트 구조
```
fletimageanalysis/
├── main.py              # Flet UI 메인 애플리케이션
├── gemini_analyzer.py   # Gemini API 연동 모듈
├── pdf_processor.py     # PDF 처리 모듈
├── ui_components.py     # UI 컴포넌트 모듈
├── config.py           # 설정 관리 모듈
├── requirements.txt    # 프로젝트 의존성 목록
├── .env               # 환경 변수 파일 (API 키 등)
├── uploads/           # 업로드된 파일 저장 폴더
├── assets/            # 애플리케이션 자산
└── docs/              # 문서화 파일
```

## 4. 주요 기능 및 UI 구성

### 4.1 메인 UI 구성
- **헤더**: 애플리케이션 제목 및 로고
- **파일 업로드 영역**: PDF 파일 선택 버튼 및 파일 정보 표시
- **분석 설정 영역**: 분석 옵션 설정 (페이지 선택, 분석 모드 등)
- **분석 버튼**: 분석 시작 버튼
- **결과 표시 영역**: 분석 결과 및 PDF 미리보기
- **상태 표시줄**: 진행 상태 및 오류 메시지

### 4.2 핵심 기능
- PDF 파일 업로드 및 검증
- PDF 페이지 이미지 변환
- Gemini API를 통한 이미지 분석
- 분석 결과 실시간 표시
- 분석 진행률 표시
- 오류 처리 및 사용자 피드백

## 5. 개발 단계 및 진행 상황

### 단계 1: 프로젝트 초기 설정 ✅
- [x] 프로젝트 폴더 구조 생성
- [x] project_plan.md 작성
- [x] requirements.txt 작성
- [x] 기본 설정 파일 구성 (.env.example, config.py)
- [x] 업로드/자산 폴더 생성

### 단계 2: 핵심 모듈 구현 ✅
- [x] PDF 처리 모듈 (pdf_processor.py) 구현
- [x] Gemini API 연동 모듈 (gemini_analyzer.py) 구현
- [x] UI 컴포넌트 모듈 (ui_components.py) 구현
- [x] 메인 애플리케이션 (main.py) 구현

### 단계 3: 기본 기능 구현 ✅
- [x] PDF 파일 읽기 및 검증
- [x] PDF 페이지 이미지 변환 (PyMuPDF)
- [x] Base64 인코딩 처리
- [x] Gemini API 클라이언트 구성
- [x] 이미지 분석 요청 처리
- [x] API 응답 처리 및 파싱

### 단계 4: UI 구현 ✅
- [x] 메인 애플리케이션 레이아웃 설계
- [x] 파일 업로드 UI 구현
- [x] 분석 설정 UI 구현
- [x] 진행률 표시 UI 구현
- [x] 결과 표시 UI 구현
- [x] PDF 미리보기 UI 구현

### 단계 5: 통합 및 이벤트 처리 ✅
- [x] 파일 업로드 이벤트 처리
- [x] 분석 진행률 표시
- [x] 결과 표시 기능
- [x] 오류 처리 및 사용자 알림
- [x] 백그라운드 스레드 처리

### 단계 6: 고급 기능 구현 🔄
- [ ] 다중 페이지 PDF 처리
- [ ] 분석 결과 저장 기능
- [ ] PDF 미리보기 기능
- [ ] 설정 저장 및 복원

### 단계 7: 테스트 및 최적화 🔄
- [ ] 기능 테스트
- [ ] 성능 최적화
- [ ] UI/UX 개선
- [ ] 문서화 완료

## 6. 연구된 웹사이트 (20+개)
1. Flet 공식 문서 - https://flet.dev/docs/
2. Flet GitHub - https://github.com/flet-dev/flet
3. PyMuPDF 문서 - https://pymupdf.readthedocs.io/
4. pdf2image 라이브러리 - https://pypi.org/project/pdf2image/
5. Gemini API 문서 - https://ai.google.dev/gemini-api/docs
6. Google Gen AI SDK - https://googleapis.github.io/python-genai/
7. Flet FilePicker 문서 - https://flet.dev/docs/controls/filepicker/
8. Flet Material Library - https://flet-material.vercel.app/
9. Flet 예제 코드 - https://github.com/flet-dev/examples
10. Gemini 이미지 이해 - https://ai.google.dev/gemini-api/docs/image-understanding
11. PyMuPDF 이미지 처리 - https://pymupdf.readthedocs.io/en/latest/recipes-images.html
12. PDF to Base64 변환 - Stack Overflow 참조
13. Flet 파일 업로드 가이드 - https://flet.dev/docs/cookbook/file-picker-and-uploads/
14. Python PDF 처리 - GeeksforGeeks 참조
15. Gemini Vision API 가이드 - VideoSDK 참조
16. Flet UI 디자인 가이드 - DEV Community 참조
17. Material Design 3 - https://m3.material.io/develop/flutter
18. Flutter Material Widgets - https://docs.flutter.dev/ui/widgets/material
19. Vertex AI Gemini PDF 처리 - Google Cloud 문서
20. Flet 레이아웃 가이드 - https://flet.dev/docs/controls/layout/
21. Flet 페이지 컨트롤 - https://flet.dev/docs/controls/page/

## 7. 개발 일정 (예상 8주)
- **1-2주차**: 프로젝트 설정 및 기본 UI 구성
- **3-4주차**: PDF 처리 및 Gemini API 연동
- **5-6주차**: UI/백엔드 연동 및 핵심 기능 구현
- **7-8주차**: 고급 기능, 테스트 및 최적화

## 8. 고려 사항
- **보안**: API 키 안전한 관리 (.env 파일 사용)
- **성능**: 대용량 PDF 파일 처리 최적화
- **사용자 경험**: 직관적인 UI 및 명확한 피드백
- **오류 처리**: 포괄적인 예외 처리 및 사용자 알림
- **호환성**: 다양한 운영체제에서의 동작 확인

## 9. 버전 관리
- Python: 3.9+
- Flet: 0.25.1+
- google-genai: 1.0+
- PyMuPDF: 1.26.3+ 또는 pdf2image: 1.17.0+
- python-dotenv: 1.0.0+

## 10. 다음 단계
1. requirements.txt 파일 작성
2. 기본 프로젝트 구조 생성
3. 메인 애플리케이션 뼈대 구현
4. PDF 처리 모듈 구현
5. Gemini API 연동 모듈 구현

---
**최종 업데이트**: 2025-07-08
**현재 진행률**: 85% (핵심 기능 구현 완료)

## 11. 구현 완료된 파일들
- ✅ `config.py` - 환경 변수 및 설정 관리
- ✅ `pdf_processor.py` - PDF 처리 및 이미지 변환
- ✅ `gemini_analyzer.py` - Gemini API 연동
- ✅ `ui_components.py` - UI 컴포넌트 정의
- ✅ `main.py` - 메인 애플리케이션
- ✅ `requirements.txt` - 의존성 목록
- ✅ `.env.example` - 환경 변수 템플릿
