"""
고급 기능 모듈
PDF 미리보기, 고급 설정, 확장 기능들을 제공합니다.
"""

import base64
import io
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from PIL import Image, ImageDraw, ImageFont
import flet as ft

logger = logging.getLogger(__name__)

class PDFPreviewGenerator:
    """PDF 미리보기 생성 클래스"""
    
    def __init__(self, pdf_processor):
        self.pdf_processor = pdf_processor
        self.preview_cache = {}
    
    def generate_preview(
        self, 
        file_path: str, 
        page_number: int = 0,
        max_size: tuple = (300, 400)
    ) -> Optional[str]:
        """PDF 페이지 미리보기 이미지 생성 (base64 반환)"""
        try:
            cache_key = f"{file_path}_{page_number}_{max_size}"
            
            # 캐시 확인
            if cache_key in self.preview_cache:
                return self.preview_cache[cache_key]
            
            # PDF 페이지를 이미지로 변환
            image = self.pdf_processor.convert_pdf_page_to_image(
                file_path, page_number, zoom=1.0
            )
            
            if not image:
                return None
            
            # 미리보기 크기로 조정
            preview_image = self._resize_for_preview(image, max_size)
            
            # base64로 인코딩
            buffer = io.BytesIO()
            preview_image.save(buffer, format='PNG')
            base64_data = base64.b64encode(buffer.getvalue()).decode()
            
            # 캐시에 저장
            self.preview_cache[cache_key] = base64_data
            
            logger.info(f"PDF 미리보기 생성 완료: 페이지 {page_number + 1}")
            return base64_data
            
        except Exception as e:
            logger.error(f"미리보기 생성 실패: {e}")
            return None
    
    def _resize_for_preview(self, image: Image.Image, max_size: tuple) -> Image.Image:
        """이미지를 미리보기 크기로 조정"""
        # 비율 유지하면서 크기 조정
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 캔버스 생성 (회색 배경)
        canvas = Image.new('RGB', max_size, color='#f0f0f0')
        
        # 이미지를 중앙에 배치
        x = (max_size[0] - image.width) // 2
        y = (max_size[1] - image.height) // 2
        canvas.paste(image, (x, y))
        
        return canvas
    
    def clear_cache(self):
        """캐시 정리"""
        self.preview_cache.clear()
        logger.info("미리보기 캐시 정리 완료")

class AdvancedSettings:
    """고급 설정 관리 클래스"""
    
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = Path(settings_file)
        self.default_settings = {
            "ui": {
                "theme_mode": "light",
                "window_width": 1200,
                "window_height": 800,
                "auto_save_results": False,
                "show_preview": True
            },
            "processing": {
                "default_zoom": 2.0,
                "image_format": "PNG",
                "jpeg_quality": 95,
                "max_pages_batch": 5
            },
            "analysis": {
                "default_mode": "basic",
                "save_format": "both",  # text, json, both
                "auto_analyze": False,
                "custom_prompts": []
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                # 기본 설정과 병합
                settings = self.default_settings.copy()
                self._deep_merge(settings, loaded_settings)
                return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            logger.error(f"설정 로드 실패: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """설정 파일 저장"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info("설정 저장 완료")
            return True
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            return False
    
    def get(self, section: str, key: str, default=None):
        """설정 값 조회"""
        return self.settings.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value):
        """설정 값 변경"""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
    
    def _deep_merge(self, base: dict, update: dict):
        """딕셔너리 깊은 병합"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

class ErrorHandler:
    """고급 오류 처리 클래스"""
    
    def __init__(self):
        self.error_log = []
        self.error_callbacks = []
    
    def handle_error(
        self, 
        error: Exception, 
        context: str = "",
        user_message: str = None
    ) -> Dict[str, Any]:
        """오류 처리 및 정보 수집"""
        error_info = {
            "timestamp": self._get_timestamp(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "user_message": user_message or self._get_user_friendly_message(error)
        }
        
        # 오류 로그에 추가
        self.error_log.append(error_info)
        
        # 로거에 기록
        logger.error(f"[{context}] {error_info['error_type']}: {error_info['error_message']}")
        
        # 콜백 실행
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                logger.error(f"오류 콜백 실행 실패: {e}")
        
        return error_info
    
    def add_error_callback(self, callback):
        """오류 발생 시 실행할 콜백 추가"""
        self.error_callbacks.append(callback)
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """최근 오류 목록 반환"""
        return self.error_log[-count:]
    
    def clear_error_log(self):
        """오류 로그 정리"""
        self.error_log.clear()
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_user_friendly_message(self, error: Exception) -> str:
        """사용자 친화적 오류 메시지 생성"""
        error_type = type(error).__name__
        
        friendly_messages = {
            "FileNotFoundError": "파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.",
            "PermissionError": "파일에 접근할 권한이 없습니다. 관리자 권한으로 실행해보세요.",
            "ConnectionError": "네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인해주세요.",
            "TimeoutError": "요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.",
            "ValueError": "입력 값이 올바르지 않습니다. 설정을 확인해주세요.",
            "KeyError": "필요한 설정 값이 없습니다. 설정을 다시 확인해주세요.",
            "ImportError": "필요한 라이브러리가 설치되지 않았습니다. 의존성을 확인해주세요."
        }
        
        return friendly_messages.get(error_type, "예상치 못한 오류가 발생했습니다.")

class AnalysisHistory:
    """분석 히스토리 관리 클래스"""
    
    def __init__(self, history_file: str = "analysis_history.json"):
        self.history_file = Path(history_file)
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict[str, Any]]:
        """히스토리 파일 로드"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            logger.error(f"히스토리 로드 실패: {e}")
            return []
    
    def save_history(self):
        """히스토리 파일 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            logger.info("히스토리 저장 완료")
        except Exception as e:
            logger.error(f"히스토리 저장 실패: {e}")
    
    def add_analysis(
        self, 
        pdf_filename: str,
        analysis_mode: str,
        pages_analyzed: int,
        analysis_time: float,
        success: bool = True
    ):
        """분석 기록 추가"""
        record = {
            "timestamp": self._get_timestamp(),
            "pdf_filename": pdf_filename,
            "analysis_mode": analysis_mode,
            "pages_analyzed": pages_analyzed,
            "analysis_time": analysis_time,
            "success": success
        }
        
        self.history.append(record)
        
        # 최대 100개 기록 유지
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self.save_history()
    
    def get_recent_analyses(self, count: int = 10) -> List[Dict[str, Any]]:
        """최근 분석 기록 반환"""
        return self.history[-count:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """분석 통계 반환"""
        if not self.history:
            return {
                "total_analyses": 0,
                "successful_analyses": 0,
                "total_pages": 0,
                "average_time": 0,
                "most_used_mode": None
            }
        
        successful = [h for h in self.history if h["success"]]
        
        mode_counts = {}
        for h in self.history:
            mode = h["analysis_mode"]
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        return {
            "total_analyses": len(self.history),
            "successful_analyses": len(successful),
            "total_pages": sum(h["pages_analyzed"] for h in self.history),
            "average_time": sum(h["analysis_time"] for h in successful) / len(successful) if successful else 0,
            "most_used_mode": max(mode_counts.items(), key=lambda x: x[1])[0] if mode_counts else None
        }
    
    def clear_history(self):
        """히스토리 정리"""
        self.history.clear()
        self.save_history()
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()

class CustomPromptManager:
    """사용자 정의 프롬프트 관리 클래스"""
    
    def __init__(self, prompts_file: str = "custom_prompts.json"):
        self.prompts_file = Path(prompts_file)
        self.prompts = self.load_prompts()
    
    def load_prompts(self) -> List[Dict[str, str]]:
        """프롬프트 파일 로드"""
        try:
            if self.prompts_file.exists():
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_prompts()
        except Exception as e:
            logger.error(f"프롬프트 로드 실패: {e}")
            return self._get_default_prompts()
    
    def save_prompts(self):
        """프롬프트 파일 저장"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=2, ensure_ascii=False)
            logger.info("프롬프트 저장 완료")
        except Exception as e:
            logger.error(f"프롬프트 저장 실패: {e}")
    
    def add_prompt(self, name: str, content: str, description: str = ""):
        """새 프롬프트 추가"""
        prompt = {
            "name": name,
            "content": content,
            "description": description,
            "created_at": self._get_timestamp()
        }
        self.prompts.append(prompt)
        self.save_prompts()
    
    def get_prompt(self, name: str) -> Optional[str]:
        """프롬프트 내용 조회"""
        for prompt in self.prompts:
            if prompt["name"] == name:
                return prompt["content"]
        return None
    
    def get_prompt_list(self) -> List[str]:
        """프롬프트 이름 목록 반환"""
        return [prompt["name"] for prompt in self.prompts]
    
    def delete_prompt(self, name: str) -> bool:
        """프롬프트 삭제"""
        for i, prompt in enumerate(self.prompts):
            if prompt["name"] == name:
                del self.prompts[i]
                self.save_prompts()
                return True
        return False
    
    def _get_default_prompts(self) -> List[Dict[str, str]]:
        """기본 프롬프트 목록 반환"""
        return [
            {
                "name": "기본 도면 분석",
                "content": "이 도면을 분석하여 문서 유형, 주요 내용, 치수 정보를 알려주세요.",
                "description": "일반적인 도면 분석용",
                "created_at": self._get_timestamp()
            },
            {
                "name": "건축 도면 분석",
                "content": "이 건축 도면을 분석하여 건물 유형, 평면 구조, 주요 치수, 방의 용도를 상세히 설명해주세요.",
                "description": "건축 도면 전용",
                "created_at": self._get_timestamp()
            },
            {
                "name": "기계 도면 분석",
                "content": "이 기계 도면을 분석하여 부품명, 치수, 공차, 재료, 가공 방법을 파악해주세요.",
                "description": "기계 설계 도면 전용",
                "created_at": self._get_timestamp()
            }
        ]
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()

# 사용 예시
if __name__ == "__main__":
    # 고급 기능 테스트
    print("고급 기능 모듈 테스트")
    
    # 설정 관리 테스트
    settings = AdvancedSettings()
    print(f"현재 테마: {settings.get('ui', 'theme_mode')}")
    
    # 오류 처리 테스트
    error_handler = ErrorHandler()
    try:
        raise ValueError("테스트 오류")
    except Exception as e:
        error_info = error_handler.handle_error(e, "테스트 컨텍스트")
        print(f"오류 처리: {error_info['user_message']}")
    
    # 프롬프트 관리 테스트
    prompt_manager = CustomPromptManager()
    prompts = prompt_manager.get_prompt_list()
    print(f"사용 가능한 프롬프트: {prompts}")
