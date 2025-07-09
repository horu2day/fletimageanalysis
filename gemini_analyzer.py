"""
Gemini API 연동 모듈 (좌표 추출 기능 추가)
Google Gemini API를 사용하여 이미지와 텍스트 좌표를 함께 분석합니다.
"""

import base64
import logging
import json
from google import genai
from google.genai import types
from typing import Optional, Dict, Any, List

from config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 새로운 스키마 정의 ---

# 좌표를 포함하는 값을 위한 재사용 가능한 스키마
ValueWithCoords = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "value": types.Schema(type=types.Type.STRING, description="추출된 텍스트 값"),
        "x": types.Schema(type=types.Type.NUMBER, description="텍스트의 시작 x 좌표"),
        "y": types.Schema(type=types.Type.NUMBER, description="텍스트의 시작 y 좌표"),
    },
    required=["value", "x", "y"]
)

# 모든 필드가 ValueWithCoords를 사용하도록 스키마 업데이트
SCHEMA_EXPRESSWAY = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "사업명": ValueWithCoords,
        "시설_공구": ValueWithCoords,
        "노선이정": ValueWithCoords,
        "설계사": ValueWithCoords,
        "시공사": ValueWithCoords,
        "건설분야": ValueWithCoords,
        "건설단계": ValueWithCoords,
        "계정번호": ValueWithCoords,
        "계정날짜": ValueWithCoords,
        "개정내용": ValueWithCoords,
        "작성자": ValueWithCoords,
        "검토자": ValueWithCoords,
        "확인자": ValueWithCoords,
        "설계공구_Station": ValueWithCoords,
        "시공공구_Station": ValueWithCoords,
        "도면번호": ValueWithCoords,
        "도면축척": ValueWithCoords,
        "도면명": ValueWithCoords,
        "편철번호": ValueWithCoords,
        "적용표준버전": ValueWithCoords,
        "Note": ValueWithCoords,
        "Title": ValueWithCoords,
        "기타정보": ValueWithCoords,
    },
)

SCHEMA_TRANSPORTATION = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "사업명": ValueWithCoords,
        "시설_공구": ValueWithCoords,
        "건설분야": ValueWithCoords,
        "건설단계": ValueWithCoords,
        "계정차수": ValueWithCoords,
        "계정일자": ValueWithCoords,
        "개정내용": ValueWithCoords,
        "과업책임자": ValueWithCoords,
        "분야별책임자": ValueWithCoords,
        "설계자": ValueWithCoords,
        "위치정보": ValueWithCoords,
        "축척": ValueWithCoords,
        "도면번호": ValueWithCoords,
        "도면명": ValueWithCoords,
        "편철번호": ValueWithCoords,
        "적용표준": ValueWithCoords,
        "Note": ValueWithCoords,
        "Title": ValueWithCoords,
        "기타정보": ValueWithCoords,
    },
)


class GeminiAnalyzer:
    """Gemini API 이미지 및 텍스트 분석 클래스"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = model or Config.GEMINI_MODEL
        self.default_prompt = Config.DEFAULT_PROMPT

        if not self.api_key:
            raise ValueError("Gemini API 키가 설정되지 않았습니다.")

        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini 클라이언트 초기화 완료 (모델: {self.model})")
        except Exception as e:
            logger.error(f"Gemini 클라이언트 초기화 실패: {e}")
            raise

    def _get_schema(self, organization_type: str) -> types.Schema:
        """조직 유형에 따른 스키마를 반환합니다."""
        return SCHEMA_EXPRESSWAY if organization_type == "expressway" else SCHEMA_TRANSPORTATION

    def analyze_pdf_page(
        self,
        base64_data: str,
        text_blocks: List[Dict[str, Any]],
        prompt: Optional[str] = None,
        mime_type: str = "image/png",
        organization_type: str = "transportation"
    ) -> Optional[str]:
        """
        Base64 이미지와 추출된 텍스트 좌표를 함께 분석합니다.

        Args:
            base64_data: Base64로 인코딩된 이미지 데이터.
            text_blocks: PDF에서 추출된 텍스트와 좌표 정보 리스트.
            prompt: 분석 요청 텍스트 (None인 경우 기본값 사용).
            mime_type: 이미지 MIME 타입.
            organization_type: 조직 유형 ("transportation" 또는 "expressway").

        Returns:
            분석 결과 JSON 문자열 또는 None (실패 시).
        """
        try:
            # 텍스트 블록 정보를 JSON 문자열로 변환하여 프롬프트에 추가
            text_context = "\n".join([
                f"- text: '{block['text']}', bbox: ({block['bbox'][0]:.0f}, {block['bbox'][1]:.0f})"
                for block in text_blocks
            ])
            
            analysis_prompt = (
                (prompt or self.default_prompt) +
                "\n\n--- 추출된 텍스트와 좌표 정보 ---\n" +
                text_context +
                "\n\n--- 지시사항 ---\n"
                "위 텍스트와 좌표 정보를 바탕으로, 이미지의 내용을 분석하여 JSON 스키마를 채워주세요."
                "각 필드에 해당하는 텍스트를 찾고, 해당 텍스트의 'value'와 시작 'x', 'y' 좌표를 JSON에 기입하세요."
            )

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            mime_type=mime_type,
                            data=base64.b64decode(base64_data),
                        ),
                        types.Part.from_text(text=analysis_prompt),
                    ],
                )
            ]

            selected_schema = self._get_schema(organization_type);

            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                top_p=0.05,
                response_mime_type="application/json",
                response_schema=selected_schema
            )

            logger.info("Gemini API 분석 요청 시작 (텍스트 좌표 포함)...")

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            if response and hasattr(response, 'text'):
                result = response.text
                # JSON 응답을 파싱하여 다시 직렬화 (일관된 포맷팅)
                parsed_json = json.loads(result)
                pretty_result = json.dumps(parsed_json, ensure_ascii=False, indent=2)
                logger.info(f"분석 완료: {len(pretty_result)} 문자")
                return pretty_result
            else:
                logger.error("API 응답에서 텍스트를 찾을 수 없습니다.")
                return None

        except Exception as e:
            logger.error(f"이미지 및 텍스트 분석 중 오류 발생: {e}")
            return None

    # --- 기존 다른 메서드들은 필요에 따라 수정 또는 유지 ---
    # analyze_image_stream_from_base64, analyze_pdf_images 등은
    # 새로운 analyze_pdf_page 메서드와 호환되도록 수정 필요.
    # 지금은 핵심 기능에 집중.

    def validate_api_connection(self) -> bool:
        """API 연결 상태를 확인합니다."""
        try:
            test_response = self.client.models.generate_content("안녕하세요")
            if test_response and hasattr(test_response, 'text'):
                logger.info("Gemini API 연결 테스트 성공")
                return True
            else:
                logger.error("Gemini API 연결 테스트 실패")
                return False
        except Exception as e:
            logger.error(f"Gemini API 연결 테스트 중 오류: {e}")
            return False