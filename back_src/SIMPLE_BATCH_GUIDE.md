# 간단한 PDF 배치 분석기 사용법

## 🎯 개요
사용자 요구사항: **"복잡하게 하지 말고 기존 모듈 그대로 사용해서 여러 개 처리하고 CSV로 만들기"**

✅ **완전 구현 완료!** getcode.py와 똑같은 방식으로 여러 PDF를 처리하고 결과를 CSV로 저장하는 시스템이 준비되어 있습니다.

## 🚀 실행 방법

### 방법 1: 간단한 실행기 사용
```bash
python run_simple_batch.py
```

### 방법 2: 직접 실행
```bash
python simple_batch_analyzer_app.py
```

## 📱 UI 사용법

1. **📂 파일 선택**: "PDF 파일 선택" 버튼 클릭 또는 드래그&드롭
2. **✏️ 프롬프트 설정** (선택사항): 기본값은 getcode.py와 동일
   - 기본: "pdf 이미지 분석하여 도면인지 어떤 정보들이 있는지 알려줘"
3. **▶️ 분석 시작**: "배치 분석 시작" 버튼 클릭
4. **📊 진행률 확인**: 실시간 진행률 및 처리 상태 표시
5. **💾 결과 확인**: 자동으로 CSV 파일 저장 및 요약 통계 표시

## 📄 CSV 출력 형식

생성되는 CSV 파일에는 다음 컬럼들이 포함됩니다:

| 컬럼명 | 설명 |
|--------|------|
| file_name | 파일 이름 |
| file_size_mb | 파일 크기 (MB) |
| processing_time_seconds | 처리 시간 (초) |
| success | 성공 여부 (True/False) |
| analysis_result | getcode.py 스타일 분석 결과 |
| analysis_timestamp | 분석 완료 시간 |
| prompt_used | 사용된 프롬프트 |
| model_used | 사용된 AI 모델 |
| error_message | 오류 메시지 (실패시) |
| processed_at | 처리 완료 시간 |

## 🔧 환경 설정

### 1. API 키 설정
`.env` 파일에 Gemini API 키 설정:
```
GEMINI_API_KEY=your_api_key_here
```

### 2. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

주요 패키지:
- `flet>=0.25.1` - UI 프레임워크
- `google-genai>=1.0` - Gemini API
- `PyMuPDF>=1.26.3` - PDF 처리
- `pandas>=1.5.0` - CSV 출력
- `python-dotenv>=1.0.0` - 환경변수

## ⚡ 핵심 특징

- ✨ **단순성**: getcode.py와 동일한 방식, 복잡한 기능 제거
- 🔄 **배치 처리**: 한 번에 여러 PDF 파일 처리
- 📊 **CSV 출력**: JSON 분석 결과를 자동으로 CSV 변환
- ⚡ **성능**: 비동기 처리로 빠른 배치 분석
- 📱 **사용성**: 직관적이고 간단한 UI

## 🗂️ 파일 저장 위치

- CSV 결과: `D:/MYCLAUDE_PROJECT/fletimageanalysis/results/`
- 파일명 형식: `batch_analysis_results_YYYY-MM-DD_HH-MM-SS.csv`

## 🎯 예상 사용 시나리오

1. **여러 도면 PDF 분석**: 한 번에 10-50개 도면 파일 분석
2. **일괄 메타데이터 추출**: 도면 정보, 제목, 축척 등 추출
3. **분석 결과 관리**: CSV로 저장하여 Excel에서 관리
4. **품질 보증**: 성공률 및 처리 시간 통계로 분석 품질 확인

## 🔍 문제 해결

### Q: 분석이 실패하는 경우
A: 
- Gemini API 키가 올바르게 설정되었는지 확인
- PDF 파일이 손상되지 않았는지 확인
- 인터넷 연결 상태 확인

### Q: UI가 실행되지 않는 경우
A:
- Python 3.9+ 버전 확인
- Flet 패키지 설치 확인: `pip install flet`
- 작업 디렉토리가 올바른지 확인

### Q: CSV 파일을 찾을 수 없는 경우
A:
- `results/` 폴더가 자동 생성됩니다
- 완료 메시지에서 정확한 파일 경로 확인
- 파일 권한 문제 확인

## 📞 지원

이 시스템은 사용자 요구사항에 맞춰 **단순하고 직관적**으로 설계되었습니다.
getcode.py의 장점을 그대로 유지하면서 배치 처리 기능만 추가했습니다.
