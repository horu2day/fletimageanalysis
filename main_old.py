"""
PDF 도면 분석기 - 메인 애플리케이션 (업데이트됨)
Flet 기반의 PDF 업로드 및 Gemini API 이미지 분석 애플리케이션
"""

import flet as ft
import logging
import threading
from typing import Optional
import time

# 프로젝트 모듈 임포트
from config import Config
from pdf_processor import PDFProcessor
from gemini_analyzer import GeminiAnalyzer
from ui_components import UIComponents
from utils import AnalysisResultSaver, DateTimeUtils

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFAnalyzerApp:
    """PDF 분석기 메인 애플리케이션 클래스"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.pdf_processor = PDFProcessor()
        self.gemini_analyzer = None
        self.current_pdf_path = None
        self.current_pdf_info = None
        self.analysis_results = {}
        self.result_saver = AnalysisResultSaver("results")
        self.analysis_start_time = None
        
        # UI 컴포넌트 참조
        self.file_picker = None
        self.selected_file_text = None
        self.upload_button = None
        self.progress_bar = None
        self.progress_ring = None
        self.status_text = None
        self.results_text = None
        self.results_container = None
        self.save_button = None
        self.organization_selector = None  # 새로 추가
        self.page_selector = None
        self.analysis_mode = None
        self.custom_prompt = None
        self.pdf_preview_container = None
        self.page_nav_text = None
        self.prev_button = None
        self.next_button = None
        
        # 초기화
        self.setup_page()
        self.init_gemini_analyzer()
        
    def setup_page(self):
        """페이지 기본 설정"""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = ft.Colors.GREY_100
        
        # 윈도우 크기 설정
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 1000
        self.page.window_min_height = 700
        
        logger.info("페이지 설정 완료")
    
    def init_gemini_analyzer(self):
        """Gemini 분석기 초기화"""
        try:
            config_errors = Config.validate_config()
            if config_errors:
                self.show_error_dialog(
                    "설정 오류", 
                    "\\n".join(config_errors) + "\\n\\n.env 파일을 확인하세요."
                )
                return
                
            self.gemini_analyzer = GeminiAnalyzer()
            logger.info("Gemini 분석기 초기화 완료")
            
        except Exception as e:
            logger.error(f"Gemini 분석기 초기화 실패: {e}")
            self.show_error_dialog(
                "초기화 오류",
                f"Gemini API 초기화에 실패했습니다:\\n{str(e)}"
            )
    
    def build_ui(self):
        """UI 구성"""
        
        # 앱바
        app_bar = UIComponents.create_app_bar()
        self.page.appbar = app_bar
        
        # 파일 업로드 섹션
        upload_section = self.create_file_upload_section()
        
        # 분석 설정 섹션
        settings_section = self.create_analysis_settings_section()
        
        # 진행률 섹션
        progress_section = self.create_progress_section()
        
        # 결과 및 미리보기 섹션
        content_row = ft.Row([
            ft.Column([
                self.create_results_section(),
            ], expand=2),
            ft.Column([
                self.create_pdf_preview_section(),
            ], expand=1),
        ])
        
        # 메인 레이아웃
        main_content = ft.Column([
            upload_section,
            settings_section,
            progress_section,
            content_row,
        ], scroll=ft.ScrollMode.AUTO)
        
        # 페이지에 추가
        self.page.add(main_content)
        logger.info("UI 구성 완료")
    
    def create_file_upload_section(self) -> ft.Container:
        """파일 업로드 섹션 생성"""
        
        # 파일 선택기
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)
        
        # 선택된 파일 정보
        self.selected_file_text = ft.Text(
            "선택된 파일이 없습니다",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        # 파일 선택 버튼
        select_button = ft.ElevatedButton(
            text="PDF 파일 선택",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.on_select_file_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_100,
                color=ft.Colors.BLUE_800,
            )
        )
        
        # 분석 시작 버튼
        self.upload_button = ft.ElevatedButton(
            text="분석 시작",
            icon=ft.Icons.ANALYTICS,
            on_click=self.on_analysis_start_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📄 PDF 파일 업로드",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800
                ),
                ft.Divider(),
                ft.Row([
                    select_button,
                    self.upload_button,
                ], alignment=ft.MainAxisAlignment.START),
                self.selected_file_text,
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    def create_analysis_settings_section(self) -> ft.Container:
        """분석 설정 섹션 생성"""
        
        # UI 컴포넌트와 참조를 가져오기
        container, organization_selector, page_selector, analysis_mode, custom_prompt = \
            UIComponents.create_analysis_settings_section_with_refs()
        
        # 인스턴스 변수에 참조 저장
        self.organization_selector = organization_selector
        self.page_selector = page_selector
        self.analysis_mode = analysis_mode
        self.custom_prompt = custom_prompt
        
        # 이벤트 핸들러 설정
        self.analysis_mode.on_change = self.on_analysis_mode_change
        self.organization_selector.on_change = self.on_organization_change
        
        return container
    
    def create_progress_section(self) -> ft.Container:
        """진행률 섹션 생성"""
        
        # 진행률 바
        self.progress_bar = ft.ProgressBar(
            width=400,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.GREY_300,
            visible=False,
        )
        
        # 상태 텍스트
        self.status_text = ft.Text(
            "대기 중...",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        # 진행률 링
        self.progress_ring = ft.ProgressRing(
            width=50,
            height=50,
            stroke_width=4,
            visible=False,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📊 분석 진행 상황",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PURPLE_800
                ),
                ft.Divider(),
                ft.Row([
                    self.progress_ring,
                    ft.Column([
                        self.status_text,
                        self.progress_bar,
                    ], expand=1),
                ], alignment=ft.MainAxisAlignment.START),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    def create_results_section(self) -> ft.Container:
        """결과 섹션 생성"""
        
        # 결과 텍스트
        self.results_text = ft.Text(
            "분석 결과가 여기에 표시됩니다.",
            size=14,
            selectable=True,
        )
        
        # 결과 컨테이너
        self.results_container = ft.Container(
            content=ft.Column([
                self.results_text,
            ], scroll=ft.ScrollMode.AUTO),
            padding=15,
            height=350,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # 저장 버튼들
        save_text_button = ft.ElevatedButton(
            text="텍스트 저장",
            icon=ft.Icons.SAVE,
            disabled=True,
            on_click=self.on_save_text_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.TEAL_100,
                color=ft.Colors.TEAL_800,
            )
        )
        
        save_json_button = ft.ElevatedButton(
            text="JSON 저장",
            icon=ft.Icons.SAVE_ALT,
            disabled=True,
            on_click=self.on_save_json_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.INDIGO_100,
                color=ft.Colors.INDIGO_800,
            )
        )
        
        # 저장 버튼들을 인스턴스 변수로 저장
        self.save_text_button = save_text_button
        self.save_json_button = save_json_button
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📋 분석 결과",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_800
                    ),
                    ft.Row([
                        save_text_button,
                        save_json_button,
                    ]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                self.results_container,
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    def create_pdf_preview_section(self) -> ft.Container:
        """PDF 미리보기 섹션 생성"""
        
        # 미리보기 컨테이너
        self.pdf_preview_container = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.PICTURE_AS_PDF,
                    size=100,
                    color=ft.Colors.GREY_400
                ),
                ft.Text(
                    "PDF 미리보기",
                    size=14,
                    color=ft.Colors.GREY_600
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=300,
            height=400,
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
            alignment=ft.alignment.center,
        )
        
        # 페이지 네비게이션
        self.prev_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            disabled=True,
        )
        
        self.page_nav_text = ft.Text("1 / 1", size=14)
        
        self.next_button = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            disabled=True,
        )
        
        page_nav = ft.Row([
            self.prev_button,
            self.page_nav_text,
            self.next_button,
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "👁️ PDF 미리보기",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.INDIGO_800
                ),
                ft.Divider(),
                self.pdf_preview_container,
                page_nav,
            ], alignment=ft.MainAxisAlignment.START),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    # 이벤트 핸들러들
    
    def on_select_file_click(self, e):
        """파일 선택 버튼 클릭 핸들러"""
        self.file_picker.pick_files(
            allowed_extensions=["pdf"],
            allow_multiple=False
        )
    
    def on_file_selected(self, e: ft.FilePickerResultEvent):
        """파일 선택 결과 핸들러"""
        if e.files:
            file = e.files[0]
            self.current_pdf_path = file.path
            
            # 파일 검증
            if self.pdf_processor.validate_pdf_file(self.current_pdf_path):
                # PDF 정보 조회
                self.current_pdf_info = self.pdf_processor.get_pdf_info(self.current_pdf_path)
                
                # 파일 크기 정보 추가
                file_size_mb = self.current_pdf_info['file_size'] / (1024 * 1024)
                file_info = f"📄 {file.name} ({self.current_pdf_info['page_count']}페이지, {file_size_mb:.1f}MB)"
                self.selected_file_text.value = file_info
                self.selected_file_text.color = ft.Colors.GREEN_600
                self.upload_button.disabled = False
                
                # 페이지 네비게이션 업데이트
                self.page_nav_text.value = f"1 / {self.current_pdf_info['page_count']}"
                
                logger.info(f"PDF 파일 선택됨: {file.name}")
            else:
                self.selected_file_text.value = "❌ 유효하지 않은 PDF 파일입니다"
                self.selected_file_text.color = ft.Colors.RED_600
                self.upload_button.disabled = True
                self.current_pdf_path = None
                self.current_pdf_info = None
        else:
            self.selected_file_text.value = "선택된 파일이 없습니다"
            self.selected_file_text.color = ft.Colors.GREY_600
            self.upload_button.disabled = True
            self.current_pdf_path = None
            self.current_pdf_info = None
            
        self.page.update()
    
    def on_analysis_mode_change(self, e):
        """분석 모드 변경 핸들러"""
        if e.control.value == "custom":
            self.custom_prompt.visible = True
        else:
            self.custom_prompt.visible = False
        self.page.update()
    
    def on_organization_change(self, e):
        """조직 선택 변경 핸들러"""
        selected_org = e.control.value
        logger.info(f"조직 선택 변경: {selected_org}")
        # 필요한 경우 추가 작업 수행
        self.page.update()
    
    def on_analysis_start_click(self, e):
        """분석 시작 버튼 클릭 핸들러"""
        if not self.current_pdf_path or not self.gemini_analyzer:
            return
            
        # 분석을 별도 스레드에서 실행
        threading.Thread(target=self.run_analysis, daemon=True).start()
    
    def on_save_text_click(self, e):
        """텍스트 저장 버튼 클릭 핸들러"""
        self._save_results("text")
    
    def on_save_json_click(self, e):
        """JSON 저장 버튼 클릭 핸들러"""
        self._save_results("json")
    
    def _save_results(self, format_type: str):
        """결과 저장 공통 함수"""
        if not self.analysis_results or not self.current_pdf_info:
            self.show_error_dialog("저장 오류", "저장할 분석 결과가 없습니다.")
            return
            
        try:
            # 분석 설정 정보 수집
            analysis_settings = {
                "페이지_선택": self.page_selector.value,
                "분석_모드": self.analysis_mode.value,
                "사용자_정의_프롬프트": self.custom_prompt.value if self.analysis_mode.value == "custom" else None,
                "분석_시간": DateTimeUtils.get_timestamp()
            }
            
            if format_type == "text":
                # 텍스트 파일로 저장
                saved_path = self.result_saver.save_analysis_results(
                    pdf_filename=self.current_pdf_info['filename'],
                    analysis_results=self.analysis_results,
                    pdf_info=self.current_pdf_info,
                    analysis_settings=analysis_settings
                )
                
                if saved_path:
                    self.show_info_dialog(
                        "저장 완료", 
                        f"분석 결과가 텍스트 파일로 저장되었습니다:\\n\\n{saved_path}"
                    )
                else:
                    self.show_error_dialog("저장 실패", "텍스트 파일 저장 중 오류가 발생했습니다.")
                    
            elif format_type == "json":
                # JSON 파일로 저장
                saved_path = self.result_saver.save_analysis_json(
                    pdf_filename=self.current_pdf_info['filename'],
                    analysis_results=self.analysis_results,
                    pdf_info=self.current_pdf_info,
                    analysis_settings=analysis_settings
                )
                
                if saved_path:
                    self.show_info_dialog(
                        "저장 완료", 
                        f"분석 결과가 JSON 파일로 저장되었습니다:\\n\\n{saved_path}"
                    )
                else:
                    self.show_error_dialog("저장 실패", "JSON 파일 저장 중 오류가 발생했습니다.")
                
        except Exception as e:
            logger.error(f"결과 저장 중 오류: {e}")
            self.show_error_dialog("저장 오류", f"결과 저장 중 오류가 발생했습니다:\\n{str(e)}")
    
    def run_analysis(self):
        """분석 실행 (백그라운드 스레드)"""
        try:
            # 분석 시작 시간 기록
            self.analysis_start_time = time.time()
            
            # UI 상태 업데이트
            self.update_progress_ui(True, "PDF 이미지 변환 중...")
            
            # 조직 유형 결정
            organization_type = "transportation"  # 기본값
            if self.organization_selector and self.organization_selector.value:
                if self.organization_selector.value == "한국도로공사":
                    organization_type = "expressway"
                else:
                    organization_type = "transportation"
            
            logger.info(f"선택된 조직 유형: {organization_type}")
            
            # 분석할 페이지 결정
            if self.page_selector.value == "첫 번째 페이지":
                pages_to_analyze = [0]
            else:  # 모든 페이지
                pages_to_analyze = list(range(self.current_pdf_info['page_count']))
            
            # 분석 프롬프트 결정
            if self.analysis_mode.value == "custom":
                prompt = self.custom_prompt.value or Config.DEFAULT_PROMPT
            elif self.analysis_mode.value == "detailed":
                prompt = "이 PDF 이미지를 자세히 분석하여 다음 정보를 제공해주세요: 1) 문서 유형, 2) 주요 내용, 3) 도면/도표 정보, 4) 텍스트 내용, 5) 기타 특징"
            else:  # basic
                prompt = Config.DEFAULT_PROMPT
            
            # 페이지별 분석 수행
            total_pages = len(pages_to_analyze)
            self.analysis_results = {}
            
            for i, page_num in enumerate(pages_to_analyze):
                # 진행률 업데이트
                progress = (i + 1) / total_pages
                self.update_progress_ui(
                    True, 
                    f"페이지 {page_num + 1} 분석 중... ({i + 1}/{total_pages})",
                    progress
                )
                
                # PDF 페이지를 base64로 변환
                base64_data = self.pdf_processor.pdf_page_to_base64(
                    self.current_pdf_path, 
                    page_num
                )
                
                if base64_data:
                    # Gemini API로 분석 (조직 유형 전달)
                    result = self.gemini_analyzer.analyze_image_from_base64(
                        base64_data=base64_data,
                        prompt=prompt,
                        organization_type=organization_type
                    )
                    
                    if result:
                        self.analysis_results[page_num] = result
                    else:
                        self.analysis_results[page_num] = f"페이지 {page_num + 1} 분석 실패"
                else:
                    self.analysis_results[page_num] = f"페이지 {page_num + 1} 이미지 변환 실패"
            
            # 결과 표시
            self.display_analysis_results()
            
            # 완료 상태로 업데이트
            if self.analysis_start_time:
                duration = time.time() - self.analysis_start_time
                duration_str = DateTimeUtils.format_duration(duration)
                self.update_progress_ui(False, f"분석 완료! (소요시간: {duration_str})", 1.0)
            else:
                self.update_progress_ui(False, "분석 완료!", 1.0)
            
        except Exception as e:
            logger.error(f"분석 중 오류 발생: {e}")
            self.update_progress_ui(False, f"분석 오류: {str(e)}")
            self.show_error_dialog("분석 오류", f"분석 중 오류가 발생했습니다:\\n{str(e)}")
    
    def update_progress_ui(
        self, 
        is_running: bool, 
        status: str, 
        progress: Optional[float] = None
    ):
        """진행률 UI 업데이트"""
        def update():
            self.progress_ring.visible = is_running
            self.status_text.value = status
            
            if progress is not None:
                self.progress_bar.value = progress
                self.progress_bar.visible = True
            else:
                self.progress_bar.visible = is_running
                
            self.page.update()
        
        # 메인 스레드에서 UI 업데이트
        self.page.run_thread(update)
    
    def display_analysis_results(self):
        """분석 결과 표시"""
        def update_results():
            if self.analysis_results:
                # 결과 텍스트 구성 (요약 정보 포함)
                result_text = "📊 분석 요약\\n"
                result_text += f"- 분석된 페이지: {len(self.analysis_results)}개\\n"
                result_text += f"- 분석 완료 시간: {DateTimeUtils.get_timestamp()}\\n\\n"
                
                for page_num, result in self.analysis_results.items():
                    result_text += f"\\n📋 페이지 {page_num + 1} 분석 결과\\n"
                    result_text += "=" * 50 + "\\n"
                    result_text += result
                    result_text += "\\n\\n"
                
                self.results_text.value = result_text.strip()
                
                # 저장 버튼 활성화
                self.save_text_button.disabled = False
                self.save_json_button.disabled = False
            else:
                self.results_text.value = "분석 결과가 없습니다."
                self.save_text_button.disabled = True
                self.save_json_button.disabled = True
                
            self.page.update()
        
        # 메인 스레드에서 UI 업데이트
        self.page.run_thread(update_results)
    
    def show_error_dialog(self, title: str, message: str):
        """오류 다이얼로그 표시"""
        dialog = UIComponents.create_error_dialog(title, message)
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            
        dialog.actions[0].on_click = close_dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_info_dialog(self, title: str, message: str):
        """정보 다이얼로그 표시"""
        dialog = UIComponents.create_info_dialog(title, message)
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            
        dialog.actions[0].on_click = close_dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

def main(page: ft.Page):
    """메인 함수"""
    try:
        # 애플리케이션 초기화
        app = PDFAnalyzerApp(page)
        
        # UI 구성
        app.build_ui()
        
        logger.info("애플리케이션 시작 완료")
        
    except Exception as e:
        logger.error(f"애플리케이션 시작 실패: {e}")
        # 간단한 오류 페이지 표시
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("애플리케이션 초기화 오류", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"오류 내용: {str(e)}", size=16),
                    ft.Text("설정을 확인하고 다시 시도하세요.", size=14),
                ], alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
            )
        )

if __name__ == "__main__":
    # 애플리케이션 실행
    ft.app(
        target=main,
        view=ft.AppView.FLET_APP,
        upload_dir="uploads",
    )
