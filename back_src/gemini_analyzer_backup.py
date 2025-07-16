"""
Gemini API 연동 모듈
Google Gemini API를 사용하여 이미지 분석을 수행합니다.
"""

import base64
import logging
from google import genai
from google.genai import types
from typing import Optional, Dict, Any
from config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Gemini API 이미지 분석 클래스"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        GeminiAnalyzer 초기화
        
        Args:
            api_key: Gemini API 키 (None인 경우 환경변수에서 가져옴)
            model: 사용할 모델명 (기본값: 설정에서 가져옴)
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = model or Config.GEMINI_MODEL
        self.default_prompt = Config.DEFAULT_PROMPT
        
        if not self.api_key:
            raise ValueError("Gemini API 키가 설정되지 않았습니다.")
            
        # Gemini 클라이언트 초기화
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini 클라이언트 초기화 완료 (모델: {self.model})")
        except Exception as e:
            logger.error(f"Gemini 클라이언트 초기화 실패: {e}")
            raise
    
    def analyze_image_from_base64(
        self, 
        base64_data: str, 
        prompt: Optional[str] = None,
        mime_type: str = "image/png",
        organization_type: str = "transportation"
    ) -> Optional[str]:
        """
        Base64 이미지 데이터를 분석합니다.
        
        Args:
            base64_data: Base64로 인코딩된 이미지 데이터
            prompt: 분석 요청 텍스트 (None인 경우 기본값 사용)
            mime_type: 이미지 MIME 타입
            organization_type: 조직 유형 ("transportation" 또는 "expressway")
            
        Returns:
            분석 결과 텍스트 또는 None (실패 시)
        """
        try:
            analysis_prompt = prompt or self.default_prompt
            
            # 컨텐츠 구성
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
            schema_expressway=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["사업명", "시설/공구", "건설분야", "건설단계"],
                    properties = {
                        "사업명": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "노선이정": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "설계사": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "시공사": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "건설분야": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "건설단계": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "계정번호": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "(계정)날짜": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "(개정)내용": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "작성자": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "검토자": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "확인자": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "설계공구": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "시공공구": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "도면번호": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "도면축척": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "도면명": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "편철번호": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "적용표준버전": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "Note": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "Title": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "기타정보": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                    },
                )
            schema_transportation=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["사업명", "시설/공구", "건설분야", "건설단계"],
                    properties = {
                        "사업명": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "시설/공구": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "건설분야": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "건설단계": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "계정차수": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "계정일자": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "개정내용": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "과업책임자": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "분야별책임자": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "설계자": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "위치정보": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "축척": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "도면번호": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "도면명": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "편철번호": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "적용표준": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "Note": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "Title": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "기타정보": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                    },
                )
            # 조직 유형에 따른 스키마 선택
            if organization_type == "expressway":
                selected_schema = schema_expressway
            else:  # transportation (기본값)
                selected_schema = schema_transportation
            
            # 생성 설정
            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                top_p=0.05,
                thinking_config = types.ThinkingConfig(
                    thinking_budget=0,
                ),
                response_mime_type="application/json",
                response_schema= selected_schema
            )
            
            logger.info("Gemini API 분석 요청 시작...")
            
            # API 호출
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            
            if response and hasattr(response, 'text'):
                result = response.text
                logger.info(f"분석 완료: {len(result)} 문자")
                return result
            else:
                logger.error("API 응답에서 텍스트를 찾을 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"이미지 분석 중 오류 발생: {e}")
            return None
    
    def analyze_image_stream_from_base64(
        self, 
        base64_data: str, 
        prompt: Optional[str] = None,
        mime_type: str = "image/png",
        organization_type: str = "transportation"
    ):
        """
        Base64 이미지 데이터를 스트리밍으로 분석합니다.
        
        Args:
            base64_data: Base64로 인코딩된 이미지 데이터
            prompt: 분석 요청 텍스트
            mime_type: 이미지 MIME 타입
            organization_type: 조직 유형 ("transportation" 또는 "expressway")
            
        Yields:
            분석 결과 텍스트 청크
        """
        try:
            analysis_prompt = prompt or self.default_prompt
            
            # 컨텐츠 구성
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
            
            # 조직 유형에 따른 스키마 선택
            if organization_type == "expressway":
                selected_schema = schema_expressway
            else:  # transportation (기본값)
                selected_schema = schema_transportation
            
            # 생성 설정
            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                top_p=0.05,
                thinking_config = types.ThinkingConfig(
                    thinking_budget=0,
                ),
                response_mime_type="application/json",
                response_schema=selected_schema,
            )
            
            logger.info("Gemini API 스트리밍 분석 요청 시작...")
            
            # 스트리밍 API 호출
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"스트리밍 이미지 분석 중 오류 발생: {e}")
            yield f"오류: {str(e)}"
    
    def analyze_pdf_images(
        self, 
        base64_images: list, 
        prompt: Optional[str] = None,
        mime_type: str = "image/png",
        organization_type: str = "transportation"
    ) -> Dict[int, str]:
        """
        여러 PDF 페이지 이미지를 일괄 분석합니다.
        
        Args:
            base64_images: Base64 이미지 데이터 리스트
            prompt: 분석 요청 텍스트
            mime_type: 이미지 MIME 타입
            organization_type: 조직 유형 ("transportation" 또는 "expressway")
            
        Returns:
            페이지 번호별 분석 결과 딕셔너리
        """
        results = {}
        
        for i, base64_data in enumerate(base64_images):
            logger.info(f"페이지 {i + 1}/{len(base64_images)} 분석 중...")
            
            result = self.analyze_image_from_base64(
                base64_data=base64_data,
                prompt=prompt,
                mime_type=mime_type,
                organization_type=organization_type
            )
            
            if result:
                results[i] = result
            else:
                results[i] = f"페이지 {i + 1} 분석 실패"
                
        logger.info(f"총 {len(results)}개 페이지 분석 완료")
        return results
    
    def validate_api_connection(self) -> bool:
        """API 연결 상태를 확인합니다."""
        try:
            # 간단한 텍스트 생성으로 연결 테스트
            test_response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="안녕하세요. 연결 테스트입니다.")]
                )],
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=10,
                )
            )
            
            if test_response and hasattr(test_response, 'text'):
                logger.info("Gemini API 연결 테스트 성공")
                return True
            else:
                logger.error("Gemini API 연결 테스트 실패")
                return False
                
        except Exception as e:
            logger.error(f"Gemini API 연결 테스트 중 오류: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """현재 사용 중인 모델 정보를 반환합니다."""
        return {
            "model": self.model,
            "api_key_length": len(self.api_key) if self.api_key else 0,
            "default_prompt": self.default_prompt
        }

# 사용 예시 및 테스트
if __name__ == "__main__":
    try:
        # 분석기 초기화
        analyzer = GeminiAnalyzer()
        
        # 연결 테스트
        if analyzer.validate_api_connection():
            print("Gemini API 연결 성공!")
            print(f"모델 정보: {analyzer.get_model_info()}")
        else:
            print("Gemini API 연결 실패!")
            
    except Exception as e:
        print(f"초기화 실패: {e}")
        print("API 키가 올바르게 설정되었는지 확인하세요.")
