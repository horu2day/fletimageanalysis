# To run this code you need to install the following dependencies:
# pip install google-genai

"""
간단한 Gemini 이미지 분석기
getcode.py의 프롬프트를 그대로 사용하여 PDF 이미지를 분석합니다.

Author: Claude Assistant  
Created: 2025-07-14
Version: 1.0.0
Based on: getcode.py (original user code)
"""

import base64
import os
import logging
from google import genai
from google.genai import types
from typing import Optional, Dict, Any
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleGeminiAnalyzer:
    """
    getcode.py 스타일의 간단한 Gemini 이미지 분석기
    구조화된 JSON 스키마 대신 자연어 텍스트 분석을 수행합니다.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        간단한 Gemini 분석기 초기화
        
        Args:
            api_key: Gemini API 키 (None인 경우 환경변수에서 로드)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = "gemini-2.5-flash"  # getcode.py와 동일한 모델
        
        # getcode.py와 동일한 프롬프트 사용
        self.default_prompt = "pdf 이미지 분석하여 도면인지 어떤 정보들이 있는지 알려줘."
        
        if not self.api_key:
            raise ValueError("Gemini API 키가 설정되지 않았습니다. GEMINI_API_KEY 환경변수를 설정하거나 api_key 매개변수를 제공하세요.")
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Simple Gemini 클라이언트 초기화 완료 (모델: {self.model})")
        except Exception as e:
            logger.error(f"Gemini 클라이언트 초기화 실패: {e}")
            raise
    
    def analyze_pdf_image(
        self, 
        base64_data: str, 
        custom_prompt: Optional[str] = None,
        mime_type: str = "application/pdf"
    ) -> Optional[Dict[str, Any]]:
        """
        Base64로 인코딩된 PDF 데이터를 분석합니다.
        getcode.py와 동일한 방식으로 동작합니다.
        
        Args:
            base64_data: Base64로 인코딩된 PDF 데이터
            custom_prompt: 사용자 정의 프롬프트 (None인 경우 기본 프롬프트 사용)
            mime_type: 파일 MIME 타입
            
        Returns:
            분석 결과 딕셔너리 또는 None (실패 시)
            {
                'analysis_result': str,  # 분석 결과 텍스트
                'success': bool,         # 성공 여부
                'timestamp': str,        # 분석 시각
                'prompt_used': str,      # 사용된 프롬프트
                'model': str,           # 사용된 모델
                'error_message': str    # 오류 메시지 (실패 시)
            }
        """
        try:
            prompt = custom_prompt or self.default_prompt
            logger.info(f"이미지 분석 시작 - 프롬프트: {prompt[:50]}...")
            
            # getcode.py와 동일한 구조로 컨텐츠 생성
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            mime_type=mime_type,
                            data=base64.b64decode(base64_data),
                        ),
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            # getcode.py와 동일한 설정 사용
            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                top_p=0.05,
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                response_mime_type="text/plain",  # JSON이 아닌 일반 텍스트
            )
            
            # 스트리밍이 아닌 일반 응답으로 수정 (CSV 저장을 위해)
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            
            if response and hasattr(response, 'text') and response.text:
                result = {
                    'analysis_result': response.text.strip(),
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'prompt_used': prompt,
                    'model': self.model,
                    'error_message': None
                }
                logger.info(f"분석 완료: {len(response.text)} 문자")
                return result
            else:
                logger.error("API 응답에서 텍스트를 찾을 수 없습니다.")
                return {
                    'analysis_result': None,
                    'success': False,
                    'timestamp': datetime.now().isoformat(),
                    'prompt_used': prompt,
                    'model': self.model,
                    'error_message': "API 응답에서 텍스트를 찾을 수 없습니다."
                }
        
        except Exception as e:
            error_msg = f"이미지 분석 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            return {
                'analysis_result': None,
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'prompt_used': custom_prompt or self.default_prompt,
                'model': self.model,
                'error_message': error_msg
            }
    
    def analyze_image_from_bytes(
        self, 
        image_bytes: bytes, 
        custom_prompt: Optional[str] = None,
        mime_type: str = "image/png"
    ) -> Optional[Dict[str, Any]]:
        """
        바이트 형태의 이미지를 직접 분석합니다.
        
        Args:
            image_bytes: 이미지 바이트 데이터
            custom_prompt: 사용자 정의 프롬프트
            mime_type: 이미지 MIME 타입
            
        Returns:
            분석 결과 딕셔너리
        """
        try:
            # 바이트를 base64로 인코딩
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            return self.analyze_pdf_image(base64_data, custom_prompt, mime_type)
        except Exception as e:
            error_msg = f"이미지 바이트 분석 중 오류: {str(e)}"
            logger.error(error_msg)
            return {
                'analysis_result': None,
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'prompt_used': custom_prompt or self.default_prompt,
                'model': self.model,
                'error_message': error_msg
            }
    
    def validate_api_connection(self) -> bool:
        """API 연결 상태를 확인합니다."""
        try:
            test_content = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="안녕하세요")]
                )
            ]
            
            config = types.GenerateContentConfig(
                temperature=0,
                response_mime_type="text/plain"
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=test_content,
                config=config
            )
            
            if response and hasattr(response, 'text'):
                logger.info("Simple Gemini API 연결 테스트 성공")
                return True
            else:
                logger.error("Simple Gemini API 연결 테스트 실패")
                return False
        except Exception as e:
            logger.error(f"Simple Gemini API 연결 테스트 중 오류: {e}")
            return False


# 사용 예시
if __name__ == "__main__":
    # 테스트 코드
    analyzer = SimpleGeminiAnalyzer()
    
    # API 연결 테스트
    if analyzer.validate_api_connection():
        print("✅ API 연결 성공")
        
        # 샘플 이미지 분석 (실제 사용 시에는 PDF 파일에서 추출한 이미지 사용)
        sample_text = "테스트용 간단한 텍스트 분석"
        
        # 실제 사용 예시:
        # with open("sample.pdf", "rb") as f:
        #     pdf_bytes = f.read()
        #     base64_data = base64.b64encode(pdf_bytes).decode('utf-8')
        #     result = analyzer.analyze_pdf_image(base64_data)
        #     print("분석 결과:", result)
    else:
        print("❌ API 연결 실패")
