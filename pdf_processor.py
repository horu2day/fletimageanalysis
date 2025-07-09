"""
PDF 처리 모듈
PDF 파일을 이미지로 변환하고 base64로 인코딩하는 기능을 제공합니다.
"""

import base64
import io
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Optional, Tuple, Dict, Any
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF 파일 처리 클래스"""
    
    def __init__(self):
        self.supported_formats = ['pdf']
        
    def validate_pdf_file(self, file_path: str) -> bool:
        """PDF 파일 유효성 검사"""
        try:
            path = Path(file_path)
            
            # 파일 존재 여부 확인
            if not path.exists():
                logger.error(f"파일이 존재하지 않습니다: {file_path}")
                return False
                
            # 파일 확장자 확인
            if path.suffix.lower() != '.pdf':
                logger.error(f"지원하지 않는 파일 형식입니다: {path.suffix}")
                return False
                
            # PDF 파일 열기 테스트
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                logger.error("PDF 파일에 페이지가 없습니다.")
                return False
                
            logger.info(f"PDF 검증 완료: {page_count}페이지")
            return True
            
        except Exception as e:
            logger.error(f"PDF 파일 검증 중 오류 발생: {e}")
            return False
    
    def get_pdf_info(self, file_path: str) -> Optional[dict]:
        """PDF 파일 정보 조회"""
        try:
            doc = fitz.open(file_path)
            info = {
                'page_count': len(doc),
                'metadata': doc.metadata,
                'file_size': Path(file_path).stat().st_size,
                'filename': Path(file_path).name
            }
            doc.close()
            return info
            
        except Exception as e:
            logger.error(f"PDF 정보 조회 중 오류 발생: {e}")
            return None
    
    def convert_pdf_page_to_image(
        self, 
        file_path: str, 
        page_number: int = 0,
        zoom: float = 2.0,
        image_format: str = "PNG"
    ) -> Optional[Image.Image]:
        """PDF 페이지를 PIL Image로 변환"""
        try:
            doc = fitz.open(file_path)
            
            if page_number >= len(doc):
                logger.error(f"페이지 번호가 범위를 벗어남: {page_number}")
                doc.close()
                return None
                
            # 페이지 로드
            page = doc.load_page(page_number)
            
            # 이미지 변환을 위한 매트릭스 설정 (확대/축소)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # PIL Image로 변환
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            doc.close()
            logger.info(f"페이지 {page_number + 1} 이미지 변환 완료: {img.size}")
            return img
            
        except Exception as e:
            logger.error(f"PDF 페이지 이미지 변환 중 오류 발생: {e}")
            return None
    
    def convert_pdf_to_images(
        self, 
        file_path: str,
        max_pages: Optional[int] = None,
        zoom: float = 2.0
    ) -> List[Image.Image]:
        """PDF의 모든 페이지를 이미지로 변환"""
        images = []
        
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # 최대 페이지 수 제한
            if max_pages:
                total_pages = min(total_pages, max_pages)
            
            for page_num in range(total_pages):
                img = self.convert_pdf_page_to_image(file_path, page_num, zoom)
                if img:
                    images.append(img)
                    
            doc.close()
            logger.info(f"총 {len(images)}개 페이지 이미지 변환 완료")
            
        except Exception as e:
            logger.error(f"PDF 전체 페이지 변환 중 오류 발생: {e}")
            
        return images
    
    def image_to_base64(
        self, 
        image: Image.Image, 
        format: str = "PNG",
        quality: int = 95
    ) -> Optional[str]:
        """PIL Image를 base64 문자열로 변환"""
        try:
            buffer = io.BytesIO()
            
            # JPEG 형식인 경우 품질 설정
            if format.upper() == "JPEG":
                image.save(buffer, format=format, quality=quality)
            else:
                image.save(buffer, format=format)
                
            buffer.seek(0)
            base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            logger.info(f"이미지를 base64로 변환 완료 (크기: {len(base64_string)} 문자)")
            return base64_string
            
        except Exception as e:
            logger.error(f"이미지 base64 변환 중 오류 발생: {e}")
            return None
    
    def pdf_page_to_base64(
        self, 
        file_path: str, 
        page_number: int = 0,
        zoom: float = 2.0,
        format: str = "PNG"
    ) -> Optional[str]:
        """PDF 페이지를 직접 base64로 변환"""
        img = self.convert_pdf_page_to_image(file_path, page_number, zoom)
        if img:
            return self.image_to_base64(img, format)
        return None
    
    def pdf_page_to_image_bytes(
        self, 
        file_path: str, 
        page_number: int = 0,
        zoom: float = 2.0,
        format: str = "PNG"
    ) -> Optional[bytes]:
        """PDF 페이지를 이미지 바이트로 변환 (Flet 이미지 표시용)"""
        try:
            img = self.convert_pdf_page_to_image(file_path, page_number, zoom)
            if img:
                buffer = io.BytesIO()
                img.save(buffer, format=format)
                buffer.seek(0)
                image_bytes = buffer.getvalue()
                
                logger.info(f"페이지 {page_number + 1} 이미지 바이트 변환 완료 (크기: {len(image_bytes)} 바이트)")
                return image_bytes
            return None
            
        except Exception as e:
            logger.error(f"PDF 페이지 이미지 바이트 변환 중 오류 발생: {e}")
            return None
    
    def get_optimal_zoom_for_size(self, target_size: Tuple[int, int]) -> float:
        """목표 크기에 맞는 최적 줌 비율 계산"""
        # 기본 PDF 페이지 크기 (A4: 595x842 points)
        default_width, default_height = 595, 842
        target_width, target_height = target_size
        
        # 비율 계산
        width_ratio = target_width / default_width
        height_ratio = target_height / default_height
        
        # 작은 비율을 선택하여 전체 페이지가 들어가도록 함
        zoom = min(width_ratio, height_ratio)
        
        logger.info(f"최적 줌 비율 계산: {zoom:.2f}")
        return zoom

    def extract_text_with_coordinates(self, file_path: str, page_number: int = 0) -> List[Dict[str, Any]]:
        """PDF 페이지에서 텍스트와 좌표를 추출합니다."""
        text_blocks = []
        try:
            doc = fitz.open(file_path)
            if page_number >= len(doc):
                logger.error(f"페이지 번호가 범위를 벗어남: {page_number}")
                doc.close()
                return []

            page = doc.load_page(page_number)
            # 'dict' 옵션은 블록, 라인, 스팬에 대한 상세 정보를 제공합니다.
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:  # 블록 반복
                if b['type'] == 0:  # 텍스트 블록
                    for l in b["lines"]:  # 라인 반복
                        for s in l["spans"]:  # 스팬(텍스트 조각) 반복
                            text_blocks.append({
                                "text": s["text"],
                                "bbox": s["bbox"], # (x0, y0, x1, y1)
                                "font": s["font"],
                                "size": s["size"]
                            })
            
            doc.close()
            logger.info(f"페이지 {page_number + 1}에서 {len(text_blocks)}개의 텍스트 블록 추출 완료")
            return text_blocks

        except Exception as e:
            logger.error(f"PDF 텍스트 및 좌표 추출 중 오류 발생: {e}")
            return []

# 사용 예시
if __name__ == "__main__":
    processor = PDFProcessor()
    
    # 테스트용 코드 (실제 PDF 파일 경로로 변경 필요)
    test_pdf = "test.pdf"
    
    if processor.validate_pdf_file(test_pdf):
        info = processor.get_pdf_info(test_pdf)
        print(f"PDF 정보: {info}")
        
        # 첫 번째 페이지를 base64로 변환
        base64_data = processor.pdf_page_to_base64(test_pdf, 0)
        if base64_data:
            print(f"Base64 변환 성공: {len(base64_data)} 문자")
    else:
        print("PDF 파일 검증 실패")
