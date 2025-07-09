# Flet 기반 PDF 입력 및 Gemini API 이미지 분석 UI 프로젝트 계획

## 1. 프로젝트 목표
Flet 프레임워크를 사용하여 사용자가 PDF 및 DXF 파일을 업로드하고, 다음과 같은 분석을 수행하는 애플리케이션을 개발합니다:
- **PDF 파일**: Gemini API를 통한 이미지 분석
- **DXF 파일**: ezdxf 라이브러리를 통한 도곽(Title Block) 정보 추출 및 Block Reference/Attribute Reference 분석

## 2. 기술 스택
- **UI 프레임워크**: Flet v0.25.1+
- **API 연동**: Google Gemini API (Python SDK - google-genai v1.0+)
- **PDF 처리**: PyMuPDF v1.26.3+ 또는 pdf2image v1.17.0+
- **DXF 처리**: ezdxf v1.4.2+ (CAD 도면 파일 처리)
- **데이터 인코딩**: base64 (Python 내장 라이브러리)
- **환경 변수 관리**: python-dotenv v1.0.0+
- **UI 디자인**: Flet Material Library (선택 사항)
- **좌표 계산**: numpy v1.24.0+ (Bounding Box 계산)

## 3. 프로젝트 구조
```
fletimageanalysis/
├── main.py              # Flet UI 메인 애플리케이션
├── gemini_analyzer.py   # Gemini API 연동 모듈
├── pdf_processor.py     # PDF 처리 모듈
├── dxf_processor.py     # DXF 처리 모듈 (NEW)
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
**PDF 분석 기능:**
- PDF 파일 업로드 및 검증
- PDF 페이지 이미지 변환
- Gemini API를 통한 이미지 분석

**DXF 분석 기능 (NEW):**
- DXF 파일 업로드 및 검증
- Block Reference 추출 및 분석
- Attribute Reference에서 도곽 정보 추출
- 도곽 위치, 배치, 크기 정보 추출
- Text Bounding Box 좌표 계산

**공통 기능:**
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

### 단계 6: 고급 기능 구현 ✅
- [x] PDF 미리보기 기능 (advanced_features.py)
- [x] 분석 결과 저장 기능 (텍스트/JSON)
- [x] 고급 설정 관리 (AdvancedSettings)
- [x] 오류 처리 및 로깅 시스템 (ErrorHandler)
- [x] 분석 히스토리 관리 (AnalysisHistory)
- [x] 사용자 정의 프롬프트 관리 (CustomPromptManager)

### 단계 7: 문서화 및 테스트 ✅
- [x] README.md 작성 (상세한 사용법 및 설치 가이드)
- [x] 사용자 가이드 (docs/user_guide.md)
- [x] 개발자 가이드 (docs/developer_guide.md)
- [x] 테스트 스크립트 (test_project.py)
- [x] 설치 스크립트 (setup.py)
- [x] 라이선스 파일 (LICENSE - MIT)

### 단계 8: 고급 기능 확장 ✅ (NEW)
- [x] 조직별 스키마 선택 기능 구현
- [x] 국토교통부/한국도로공사 전용 스키마 적용
- [x] UI 조직 선택 드롭다운 추가
- [x] Gemini API 스키마 매개변수 동적 전달
- [x] 조직별 분석 결과 차별화

### 단계 9: 최종 최적화 및 배포 준비 ✅
- [x] 코드 정리 및 최적화
- [x] 오류 처리 강화
- [x] 사용자 경험 개선
- [x] 최종 테스트 및 검증

### 단계 10: UI 레이아웃 개선 ✅
- [x] 좌우 분할 레이아웃으로 UI 재구성
- [x] ResponsiveRow를 활용한 반응형 디자인 적용
- [x] 좌측: 파일 업로드 + 분석 설정 + 진행률 + 분석 시작 버튼
- [x] 우측: 분석 결과 표시 영역 확장
- [x] PDF 뷰어를 별도 모달 창으로 분리
- [x] AlertDialog를 사용한 PDF 미리보기 기능 구현
- [x] 페이지 네비게이션 기능 추가 (이전/다음 페이지)
- [x] pdf_processor.py에 이미지 바이트 변환 메서드 추가
- [x] 기존 UI와 새 UI 백업 및 교체 완료

### 단계 11: DXF 파일 지원 추가 ✅ (COMPLETED)
- [x] DXF 파일 형식 지원 추가 (.dxf 확장자)
- [x] ezdxf 라이브러리 설치 및 설정 (requirements.txt 업데이트)
- [x] DXF 파일 업로드 및 검증 기능 (dxf_processor.py 완성)
- [x] Block Reference 추출 모듈 구현 (dxf_processor.py)
- [x] Attribute Reference 분석 모듈 구현 (dxf_processor.py)
- [x] 도곽 정보 추출 로직 구현 (dxf_processor.py)
- [x] Bounding Box 계산 기능 구현 (dxf_processor.py)
- [x] config.py DXF 지원 설정 추가
- [x] ui_components.py DXF 지원 텍스트 업데이트
- [x] main.py 기본 DXF 지원 구조 수정 (import, 클래스명)
- [x] DXF 지원 메서드들 설계 및 구현 (dxf_support_methods.py)
- [x] main.py에 DXF 지원 메서드들 완전 통합
- [x] 파일 선택 로직 DXF 지원으로 완전 업데이트
- [x] DXF 분석 결과 UI 통합
- [x] 파일 타입별 분석 방법 자동 선택
- [x] DocumentAnalyzerApp 클래스명 통일
- [x] 변수명 통일 (current_file_path, current_file_type)
- [x] 좌우 분할 레이아웃으로 UI 재구성
- [x] ResponsiveRow를 활용한 반응형 디자인 적용
- [x] 좌측: 파일 업로드 + 분석 설정 + 진행률 + 분석 시작 버튼
- [x] 우측: 분석 결과 표시 영역 확장
- [x] PDF 뷰어를 별도 모달 창으로 분리
- [x] AlertDialog를 사용한 PDF 미리보기 기능 구현
- [x] 페이지 네비게이션 기능 추가 (이전/다음 페이지)
- [x] pdf_processor.py에 이미지 바이트 변환 메서드 추가
- [x] 기존 UI와 새 UI 백업 및 교체 완료

## 6. 연구된 웹사이트 (70+개)

### 6.1 Flet 프레임워크 관련 (12개)
1. Flet 공식 문서 - https://flet.dev/docs/
2. Flet GitHub - https://github.com/flet-dev/flet
3. Flet 드롭다운 컴포넌트 - https://flet.dev/docs/controls/dropdown/
4. Flet 컨트롤 참조 - https://flet.dev/docs/controls/
5. Flet FilePicker 문서 - https://flet.dev/docs/controls/filepicker/
6. Flet 2024 개발 동향 - DEV Community
7. Flet 초보자 가이드 - DEV Community
8. Flet 예제 코드 - https://github.com/flet-dev/examples
9. Flet UI 컴포넌트 라이브러리 - Gumroad
10. Flet 개발 토론 - GitHub Discussions
11. Flet 소개 및 특징 - Analytics Vidhya
12. Talk Python 팟캐스트 Flet 업데이트 - TalkPython.fm

### 6.2 Gemini API 및 구조화된 출력 (10개)
13. Gemini API Structured Output - https://ai.google.dev/gemini-api/docs/structured-output
14. Firebase Vertex AI Structured Output - Firebase 문서
15. Google Gen AI SDK - https://googleapis.github.io/python-genai/
16. Gemini JSON 모드 - Google Cloud 커뮤니티 Medium
17. Vertex AI Structured Output - Google Cloud 문서
18. Gemini API 퀵스타트 - Google AI 개발자
19. Gemini API 참조 - Google AI 개발자
20. Google Developers Blog 제어된 생성 - Google 개발자 블로그
21. Controlled Generation 매거진 - tanaikech GitHub
22. Gemini API JSON 구조화 가이드 - Medium

### 6.3 PDF 처리 라이브러리 비교 (8개)
23. PyMuPDF 성능 비교 - PyMuPDF 문서
24. Python PDF 라이브러리 비교 2024 - Pythonify
25. PDF 에코시스템 2023/2024 - Medium
26. PyMuPDF vs pdf2image - GitHub 토론
27. PDF 텍스트 추출 도구 평가 - Unstract
28. Python PDF 라이브러리 성능 벤치마크 - GitHub
29. PDF 처리 방법 비교 - Medium
30. Python PDF 라이브러리 비교 - IronPDF

### 6.4 한국 건설/교통 표준 (8개)
31. 국토교통부 (MOLIT) 공식사이트 - https://www.molit.go.kr/
32. 한국 건설표준센터 - KCSC
33. 한국 건설 표준 용어집 - SPACE Magazine
34. 국제 건설 코드 한국 - ICC
35. 한국 건설 안전 규정 - CAPA
36. 건설 도면 표준 번호 체계 - Archtoolbox
37. 건설 문서 가이드 - Monograph
38. 미국 건설 도면 규격 - Acquisition.gov

### 6.5 DXF 파일 처리 및 ezdxf 라이브러리 (20개)
39. ezdxf 공식 문서 - https://ezdxf.readthedocs.io/en/stable/
40. ezdxf PyPI 패키지 - https://pypi.org/project/ezdxf/
41. ezdxf GitHub 리포지토리 - https://github.com/mozman/ezdxf
42. ezdxf 블록 튜토리얼 - Block Management Documentation
43. ezdxf 데이터 추출 튜토리얼 - Getting Data Tutorial
44. ezdxf DXF 엔티티 문서 - DXF Entities Documentation
45. Stack Overflow - ezdxf Block Reference 추출
46. Stack Overflow - DXF 텍스트 추출 방법
47. Stack Overflow - ezdxf Attribute Reference 처리
48. ezdxf Block Management Structures
49. ezdxf DXF Tags 문서
50. AutoCAD DXF Reference - Autodesk
51. FileFormat.com - ezdxf 라이브러리 가이드
52. ezdxf Usage for Beginners
53. ezdxf Quick-Info 문서
54. GitHub - ezdxf 포크 프로젝트들
55. PyDigger - ezdxf 패키지 정보
56. GDAL AutoCAD DXF 드라이버 문서
57. FME Support - AutoCAD DWG Block Attribute 추출
58. ezdxf MText 문서

### 6.6 CAD 도면 분석 및 AI 기반 처리 (12개)
59. 엔지니어링 도면 데이터 추출 - Infrrd.ai
60. werk24 PyPI - AI 기반 기술 도면 분석
61. ResearchGate - 도면 제목 블록 정보 추출 연구
62. ScienceDirect - 엔지니어링 도면에서 치수 요구사항 추출
63. Medium - TensorFlow, Keras-OCR, OpenCV를 이용한 기술 도면 정보 추출
64. GitHub - 엔지니어링 도면 추출기 (Bakkopi)
65. Werk24 - 기술 도면 특징 추출 API
66. Stack Overflow - PyPDF2 엔지니어링 도면 파싱
67. BusinesswareTech - 기술 도면 데이터 추출 AI 솔루션
68. Stack Overflow - OCR을 이용한 CAD 기술 도면 특정 데이터 추출
69. Autodesk Forums - 제목 블록/텍스트 속성 문제
70. AutoCAD DXF 공식 레퍼런스 문서
31. 국토교통부 (MOLIT) 공식사이트 - https://www.molit.go.kr/
32. 한국 건설표준센터 - KCSC
33. 한국 건설 표준 용어집 - SPACE Magazine
34. 국제 건설 코드 한국 - ICC
35. 한국 건설 안전 규정 - CAPA
36. 건설 도면 표준 번호 체계 - Archtoolbox
37. 건설 문서 가이드 - Monograph
38. 미국 건설 도면 규격 - Acquisition.gov

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
- ezdxf: 1.4.2+ (NEW - DXF 파일 처리)
- numpy: 1.24.0+ (NEW - 좌표 계산)
- python-dotenv: 1.0.0+

## 10. 다음 단계
1. requirements.txt 파일 작성
2. 기본 프로젝트 구조 생성
3. 메인 애플리케이션 뼈대 구현
4. PDF 처리 모듈 구현
5. Gemini API 연동 모듈 구현

---
**최종 업데이트**: 2025-07-09
**현재 진행률**: 100% (DXF 파일 지원 기능 통합 완료)

## 12. 최근 업데이트 (2025-07-09)

### 12.1 새로 구현된 기능
1. **조직별 스키마 선택 시스템**
   - 국토교통부: 일반 토목/건설 도면 표준 스키마
   - 한국도로공사: 고속도로 전용 도면 스키마
   - UI에서 드롭다운으로 선택 가능

2. **gemini_analyzer.py 확장**
   - `organization_type` 매개변수 추가
   - 동적 스키마 선택 로직 구현
   - `schema_transportation`, `schema_expressway` 분리

3. **UI 컴포넌트 개선**
   - `create_analysis_settings_section_with_refs()` 함수 추가
   - 조직별 설명 텍스트 포함
   - 직관적인 선택 인터페이스 제공

4. **main.py 통합**
   - 조직 선택 이벤트 핸들러 추가
   - 분석 시 선택된 조직 유형 전달
   - 결과에 조직 정보 포함

### 12.2 기술적 개선사항
- 30개 이상 웹사이트 심층 연구 완료
- Flet 최신 드롭다운 API 활용
- Gemini API Structured Output 최신 기능 적용
- 한국 건설 표준 및 도로공사 규격 조사

### 12.3 UI 레이아웃 개선 세부사항 (2025-07-09)
- 창 크기 조정: 1400x900 기본, 최소 1200x800
- ResponsiveRow 반응형 브레이크포인트: sm(12), md(5/7), lg(4/8)
- PDF 뷰어 모달: 650x750 크기, 이미지 600x700 컴테이너
- 50개 이상의 웹사이트 연구로 Flet 최신 기능 적용

### 12.4 DXF 파일 지원 구현 완료 (2025-07-09) ✅

**완성된 기능:**
1. **파일 형식 확장**: requirements.txt에 ezdxf v1.4.2+, numpy v1.24.0+ 추가
2. **DXF 처리 모듈**: dxf_processor.py 완전 구현
   - Block Reference 추출 및 분석
   - Attribute Reference에서 도곽 정보 추출
   - 도곽 식별 로직 (건설분야, 건설단계, 도면명, 축척, 도면번호)
   - Text Bounding Box 좌표 계산
   - 최외곽 Bounding Box 계산
3. **설정 업데이트**: config.py에 DXF 파일 지원 추가
4. **UI 업데이트**: ui_components.py에 PDF/DXF 지원 텍스트 추가
5. **메인 애플리케이션**: main.py 기본 구조 수정 및 DXF 지원 메서드 설계
6. **지원 메서드**: dxf_support_methods.py에 다음 기능 구현
   - DXF 파일 선택 처리
   - DXF 분석 실행 로직
   - DXF 결과 표시 UI

**기술적 세부사항:**
- ezdxf 라이브러리를 통한 DXF 파일 파싱
- Block Reference 순회 및 Attribute Reference 추출
- 도곽 식별을 위한 키워드 매칭 알고리즘
- numpy를 이용한 좌표 계산 및 Bounding Box 처리
- 데이터클래스를 통한 구조화된 데이터 처리
- 포괄적인 오류 처리 및 로깅 시스템

**다음 단계 (완료):**
1. ✅ main.py에 dxf_support_methods.py의 메서드들 통합 완료
2. ✅ 파일 선택 로직 DXF 지원으로 완전 업데이트 완료
3. ✅ DXF 분석 결과 UI 통합 및 테스트 완료
4. ✅ 전체 기능 통합 및 테스트 완료

### 12.6 DXF 지원 기능 통합 완료 (2025-07-09) ✅

**완성된 통합 작업:**
1. **파일 선택기 확장**: PDF와 DXF 파일 확장자 모두 지원
2. **파일 선택 로직 업데이트**: 
   - `on_file_selected` 메서드를 PDF/DXF 파일 타입 자동 감지로 완전 교체
   - `_handle_pdf_file_selection`과 `_handle_dxf_file_selection` 메서드 추가
   - `_reset_file_state` 메서드로 파일 상태 초기화
3. **분석 실행 로직 확장**:
   - `run_analysis` 메서드를 PDF/DXF 타입별 분석으로 완전 교체
   - `_run_pdf_analysis`와 `_run_dxf_analysis` 메서드 분리
   - `display_dxf_analysis_results` 메서드 추가
4. **UI 통합**:
   - 파일 타입별 미리보기 활성화/비활성화
   - DXF 분석 결과 전용 UI 표시
   - 파일 정보 표시 개선 (PDF/DXF 구분)
5. **변수명 통일**: 
   - `current_pdf_path` → `current_file_path`
   - `current_file_type` 변수로 PDF/DXF 구분
   - `DocumentAnalyzerApp` 클래스명 통일
6. **저장 기능 확장**: PDF와 DXF 분석 결과 모두 지원

**기술적 성과:**
- 단일 애플리케이션에서 PDF(Gemini API)와 DXF(ezdxf) 분석 완전 지원
- 파일 타입 자동 감지 및 적절한 분석 방법 선택
- 20개 이상의 웹사이트 연구를 통한 최신 기술 적용
- Flet 프레임워크의 FilePicker 최신 기능 활용
- 모듈화된 코드 구조로 유지보수성 향상

### 12.7 프로젝트 완료
- ✅ PDF/DXF 통합 문서 분석기 완전 구현
- ✅ 모든 핵심 기능 동작 확인
- ✅ 사용자 인터페이스 최종 완성
- ✅ 프로젝트 목표 100% 달성

## 11. 구현 완료된 파일들
- ✅ `config.py` - 환경 변수 및 설정 관리
- ✅ `pdf_processor.py` - PDF 처리 및 이미지 변환
- ✅ `gemini_analyzer.py` - Gemini API 연동 (조직별 스키마 지원)
- ✅ `ui_components.py` - UI 컴포넌트 정의 (조직 선택 기능 포함)
- ✅ `main.py` - 메인 애플리케이션 (조직별 분석 통합)
- ✅ `requirements.txt` - 의존성 목록
- ✅ `.env.example` - 환경 변수 템플릿
- ✅ `advanced_features.py` - 고급 기능 모듈
- ✅ `utils.py` - 유틸리티 함수들
- ✅ `test_project.py` - 테스트 스크립트
