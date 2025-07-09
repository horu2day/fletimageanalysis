"""
PDF/DXF 도면 분석기 - 메인 애플리케이션 (업데이트된 좌우 분할 레이아웃)
Flet 기반의 PDF/DXF 업로드 및 분석 애플리케이션
- PDF: Gemini API 이미지 분석
- DXF: ezdxf 라이브러리를 통한 도곽 정보 추출
새로운 UI: 좌측 설정/분석, 우측 결과, PDF 뷰어 모달
"""

import flet as ft
import logging
import threading
import base64
from typing import Optional
import time

# 프로젝트 모듈 임포트
from config import Config
from pdf_processor import PDFProcessor
from dxf_processor_fixed import FixedDXFProcessor as DXFProcessor  # NEW - 수정된 DXF 처리기
from gemini_analyzer import GeminiAnalyzer
from ui_components import UIComponents
from utils import AnalysisResultSaver, DateTimeUtils
from csv_exporter import TitleBlockCSVExporter  # NEW - CSV 저장 기능

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentAnalyzerApp:
    """PDF/DXF 분석기 메인 애플리케이션 클래스 - 새로운 좌우 분할 레이아웃"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.pdf_processor = PDFProcessor()
        self.dxf_processor = DXFProcessor()  # NEW - DXF 처리기
        self.csv_exporter = TitleBlockCSVExporter()  # NEW - CSV 저장기
        self.gemini_analyzer = None
        self.current_file_path = None  # PDF/DXF 파일 경로
        self.current_file_type = None  # 파일 타입 (pdf 또는 dxf)
        self.current_pdf_info = None  # PDF 전용
        self.current_title_block_info = None  # DXF 타이틀블럭 정보
        self.analysis_results = {}
        self.result_saver = AnalysisResultSaver("results")
        self.analysis_start_time = None
        self.current_page_index = 0
        
        # UI 컴포넌트 참조
        self.file_picker = None
        self.selected_file_text = None
        self.upload_button = None
        self.progress_bar = None
        self.progress_ring = None
        self.status_text = None
        self.results_text = None
        self.results_container = None
        self.save_text_button = None
        self.save_json_button = None
        self.save_csv_button = None  # NEW - CSV 저장 버튼
        self.title_block_table = None  # NEW - 타이틀블럭 속성 테이블
        self.organization_selector = None
        self.page_selector = None
        self.analysis_mode = None
        self.custom_prompt = None
        self.pdf_viewer_dialog = None
        self.pdf_preview_button = None
        
        # 초기화
        self.setup_page()
        self.init_gemini_analyzer()
        
    def setup_page(self):
        """페이지 기본 설정"""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = ft.Colors.GREY_100
        
        # 윈도우 크기 설정 - 버튼이 모두 보이게 세로 길게, 가로는 10% 줄임
        self.page.window.width = 980  # 1400 * 0.9 = 1260
        self.page.window.height = 980  # 1000 -> 1080으로 증가
        self.page.window.min_width = 1080  # 1200 * 0.9 = 1080
        self.page.window.min_height = 780
        
        logger.info("페이지 설정 완료 - 새로운 좌우 분할 레이아웃")
    
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
        """새로운 좌우 분할 UI 구성"""
        
        # 앱바
        app_bar = UIComponents.create_app_bar()
        self.page.appbar = app_bar
        
        # 좌측 컨트롤 패널 (4/12 columns)
        left_panel = self.create_left_control_panel()
        
        # 우측 결과 패널 (8/12 columns)  
        right_panel = self.create_right_results_panel()
        
        # ResponsiveRow를 사용한 좌우 분할 레이아웃
        main_layout = ft.ResponsiveRow([
            ft.Container(
                content=left_panel,
                col={"sm": 12, "md": 5, "lg": 4},
                padding=10,
            ),
            ft.Container(
                content=right_panel,
                col={"sm": 12, "md": 7, "lg": 8},
                padding=10,
            ),
        ])
        
        # 메인 컨테이너
        main_container = ft.Container(
            content=ft.Column([
                main_layout,
            ], expand=True, scroll=ft.ScrollMode.AUTO),
            expand=True,
            margin=10,
        )
        
        # 페이지에 추가
        self.page.add(main_container)
        
        # PDF 뷰어 다이얼로그 초기화
        self.init_pdf_viewer_dialog()
        
        logger.info("새로운 좌우 분할 UI 구성 완료")
    
    def create_left_control_panel(self) -> ft.Column:
        """좌측 컨트롤 패널 생성"""
        
        # 파일 업로드 섹션
        upload_section = self.create_file_upload_section()
        
        # 분석 설정 섹션
        settings_section = self.create_analysis_settings_section()
        
        # 진행률 섹션
        progress_section = self.create_progress_section()
        
        # 분석 시작 버튼 (크게)
        start_analysis_button = ft.Container(
            content=ft.ElevatedButton(
                text="🚀 분석 시작",
                icon=ft.Icons.ANALYTICS,
                on_click=self.on_analysis_start_click,
                disabled=True,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREEN_100,
                    color=ft.Colors.GREEN_800,
                ),
                width=300,
                height=50,
            ),
            alignment=ft.alignment.center,
            margin=ft.margin.symmetric(vertical=10),
        )
        self.upload_button = start_analysis_button.content
        
        # PDF 미리보기 버튼
        preview_button = ft.Container(
            content=ft.ElevatedButton(
                text="📄 PDF 미리보기",
                icon=ft.Icons.VISIBILITY,
                on_click=self.on_pdf_preview_click,
                disabled=True,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_100,
                    color=ft.Colors.BLUE_800,
                ),
                width=300,
                height=40,
            ),
            alignment=ft.alignment.center,
            margin=ft.margin.symmetric(vertical=5),
        )
        self.pdf_preview_button = preview_button.content
        
        return ft.Column([
            upload_section,
            ft.Divider(height=20),
            settings_section,
            ft.Divider(height=20),
            progress_section,
            ft.Divider(height=20),
            start_analysis_button,
            preview_button,
        ], expand=True, scroll=ft.ScrollMode.AUTO)
    
    def create_right_results_panel(self) -> ft.Column:
        """우측 결과 패널 생성"""
        
        # 결과 텍스트
        self.results_text = ft.Text(
            "분석 결과가 여기에 표시됩니다.\\n\\n좌측에서 PDF 파일을 선택하고 분석을 시작하세요.",
            size=14,
            selectable=True,
        )
        
        # 결과 컨테이너
        self.results_container = ft.Container(
            content=ft.Column([
                self.results_text,
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            expand=True,
        )
        
        # 저장 버튼들
        self.save_text_button = ft.ElevatedButton(
            text="💾 텍스트 저장",
            icon=ft.Icons.SAVE,
            disabled=True,
            on_click=self.on_save_text_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.TEAL_100,
                color=ft.Colors.TEAL_800,
            )
        )
        
        self.save_json_button = ft.ElevatedButton(
            text="📋 JSON 저장",
            icon=ft.Icons.SAVE_ALT,
            disabled=True,
            on_click=self.on_save_json_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.INDIGO_100,
                color=ft.Colors.INDIGO_800,
            )
        )
        
        # NEW - CSV 저장 버튼 (DXF 전용)
        self.save_csv_button = ft.ElevatedButton(
            text="📊 CSV 저장",
            icon=ft.Icons.TABLE_CHART,
            disabled=True,
            visible=False,  # 기본적으로 숨김, DXF 분석 시에만 표시
            on_click=self.on_save_csv_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        # 헤더와 버튼들
        header_row = ft.Row([
            ft.Text(
                "📋 분석 결과",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREEN_800
            ),
            ft.Row([
                self.save_text_button,
                self.save_json_button,
                self.save_csv_button,  # NEW - CSV 저장 버튼 추가
            ]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    header_row,
                    ft.Divider(),
                    self.results_container,
                ]),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                expand=True,
            )
        ], expand=True)
    
    def create_file_upload_section(self) -> ft.Container:
        """파일 업로드 섹션 생성"""
        
        # 파일 선택기
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)
        
        # 선택된 파일 정보
        self.selected_file_text = ft.Text(
            "선택된 파일이 없습니다",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        # 파일 선택 버튼
        select_button = ft.ElevatedButton(
            text="📁 PDF/DXF 파일 선택",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.on_select_file_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_100,
                color=ft.Colors.BLUE_800,
            ),
            width=280,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📄 PDF/DXF 파일 업로드",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800
                ),
                ft.Divider(),
                select_button,
                self.selected_file_text,
            ]),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    def create_analysis_settings_section(self) -> ft.Container:
        """분석 설정 섹션 생성"""
        
        # 조직 선택
        self.organization_selector = ft.Dropdown(
            label="분석 스키마",
            options=[
                ft.dropdown.Option("국토교통부", "국토교통부 - 일반 건설/토목 도면"),
                ft.dropdown.Option("한국도로공사", "한국도로공사 - 고속도로 전용 도면"),
            ],
            value="국토교통부",
            width=280,
            on_change=self.on_organization_change,
        )
        
        # 페이지 선택
        self.page_selector = ft.Dropdown(
            label="분석할 페이지",
            options=[
                ft.dropdown.Option("첫 번째 페이지"),
                ft.dropdown.Option("모든 페이지"),
            ],
            value="첫 번째 페이지",
            width=280,
        )
        
        # 분석 모드
        self.analysis_mode = ft.Dropdown(
            label="분석 모드",
            options=[
                ft.dropdown.Option("basic", "기본 분석"),
                ft.dropdown.Option("detailed", "상세 분석"),
                ft.dropdown.Option("custom", "사용자 정의"),
            ],
            value="basic",
            width=280,
            on_change=self.on_analysis_mode_change,
        )
        
        # 사용자 정의 프롬프트
        self.custom_prompt = ft.TextField(
            label="사용자 정의 프롬프트",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=280,
            visible=False,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "⚙️ 분석 설정",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PURPLE_800
                ),
                ft.Divider(),
                self.organization_selector,
                self.page_selector,
                self.analysis_mode,
                self.custom_prompt,
            ]),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    def create_progress_section(self) -> ft.Container:
        """진행률 섹션 생성"""
        
        # 진행률 바
        self.progress_bar = ft.ProgressBar(
            width=280,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.GREY_300,
            visible=False,
        )
        
        # 상태 텍스트
        self.status_text = ft.Text(
            "대기 중...",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        # 진행률 링
        self.progress_ring = ft.ProgressRing(
            width=30,
            height=30,
            stroke_width=3,
            visible=False,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📊 분석 진행 상황",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ORANGE_800
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
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    def init_pdf_viewer_dialog(self):
        """PDF 뷰어 다이얼로그 초기화"""
        
        # PDF 이미지 컨테이너
        self.pdf_image_container = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.PICTURE_AS_PDF,
                    size=100,
                    color=ft.Colors.GREY_400
                ),
                ft.Text(
                    "PDF를 선택하면 미리보기가 표시됩니다",
                    size=14,
                    color=ft.Colors.GREY_600
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=600,
            height=700,
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
            alignment=ft.alignment.center,
        )
        
        # 페이지 네비게이션
        self.prev_page_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            disabled=True,
            on_click=self.on_prev_page_click,
        )
        
        self.page_info_text = ft.Text("1 / 1", size=14)
        
        self.next_page_button = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            disabled=True,
            on_click=self.on_next_page_click,
        )
        
        page_nav = ft.Row([
            self.prev_page_button,
            self.page_info_text,
            self.next_page_button,
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # PDF 뷰어 다이얼로그
        self.pdf_viewer_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("PDF 미리보기"),
            content=ft.Column([
                self.pdf_image_container,
                page_nav,
            ], height=750, width=650),
            actions=[
                ft.TextButton("닫기", on_click=self.close_pdf_viewer)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    # 이벤트 핸들러들
    
    def on_select_file_click(self, e):
        """파일 선택 버튼 클릭 핸들러"""
        self.file_picker.pick_files(
            allowed_extensions=["pdf", "dxf"],
            allow_multiple=False
        )
    
    def on_file_selected(self, e: ft.FilePickerResultEvent):
        """파일 선택 결과 핸들러 - PDF/DXF 지원"""
        if e.files:
            file = e.files[0]
            self.current_file_path = file.path
            
            # 파일 확장자로 타입 결정
            file_extension = file.path.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                self.current_file_type = 'pdf'
                self._handle_pdf_file_selection(file)
            elif file_extension == 'dxf':
                self.current_file_type = 'dxf'
                self._handle_dxf_file_selection(file)
            else:
                self.selected_file_text.value = f"❌ 지원하지 않는 파일 형식입니다: {file_extension}"
                self.selected_file_text.color = ft.Colors.RED_600
                self.upload_button.disabled = True
                self.pdf_preview_button.disabled = True
                self._reset_file_state()
        else:
            self.selected_file_text.value = "선택된 파일이 없습니다"
            self.selected_file_text.color = ft.Colors.GREY_600
            self.upload_button.disabled = True
            self.pdf_preview_button.disabled = True
            self._reset_file_state()
            
        self.page.update()
    
    def _handle_pdf_file_selection(self, file):
        """PDF 파일 선택 처리"""
        if self.pdf_processor.validate_pdf_file(self.current_file_path):
            # PDF 정보 조회
            self.current_pdf_info = self.pdf_processor.get_pdf_info(self.current_file_path)
            
            # 파일 크기 정보 추가
            file_size_mb = self.current_pdf_info['file_size'] / (1024 * 1024)
            file_info = f"✅ {file.name} (PDF)\n📄 {self.current_pdf_info['page_count']}페이지, {file_size_mb:.1f}MB"
            self.selected_file_text.value = file_info
            self.selected_file_text.color = ft.Colors.GREEN_600
            self.upload_button.disabled = False
            self.pdf_preview_button.disabled = False
            
            # 페이지 정보 업데이트
            self.page_info_text.value = f"1 / {self.current_pdf_info['page_count']}"
            self.current_page_index = 0
            
            logger.info(f"PDF 파일 선택됨: {file.name}")
        else:
            self.selected_file_text.value = "❌ 유효하지 않은 PDF 파일입니다"
            self.selected_file_text.color = ft.Colors.RED_600
            self.upload_button.disabled = True
            self.pdf_preview_button.disabled = True
            self._reset_file_state()
    
    def _handle_dxf_file_selection(self, file):
        """DXF 파일 선택 처리"""
        try:
            if self.dxf_processor.validate_dxf_file(self.current_file_path):
                # DXF 파일 크기 계산
                import os
                file_size_mb = os.path.getsize(self.current_file_path) / (1024 * 1024)
                
                file_info = f"✅ {file.name} (DXF)\n🏗️ CAD 도면 파일, {file_size_mb:.1f}MB"
                self.selected_file_text.value = file_info
                self.selected_file_text.color = ft.Colors.GREEN_600
                self.upload_button.disabled = False
                self.pdf_preview_button.disabled = True  # DXF는 미리보기 비활성화
                
                # DXF는 페이지 개념이 없으므로 기본값 설정
                self.page_info_text.value = "DXF 파일"
                self.current_page_index = 0
                self.current_pdf_info = None  # DXF는 PDF 정보 없음
                
                logger.info(f"DXF 파일 선택됨: {file.name}")
            else:
                self.selected_file_text.value = "❌ 유효하지 않은 DXF 파일입니다"
                self.selected_file_text.color = ft.Colors.RED_600
                self.upload_button.disabled = True
                self.pdf_preview_button.disabled = True
                self._reset_file_state()
        except Exception as e:
            logger.error(f"DXF 파일 검증 오류: {e}")
            self.selected_file_text.value = f"❌ DXF 파일 처리 오류: {str(e)}"
            self.selected_file_text.color = ft.Colors.RED_600
            self.upload_button.disabled = True
            self.pdf_preview_button.disabled = True
            self._reset_file_state()
    
    def _reset_file_state(self):
        """파일 상태 초기화"""
        self.current_file_path = None
        self.current_file_type = None
        self.current_pdf_info = None
        self.current_title_block_info = None  # NEW - 타이틀블럭 정보 초기화
    
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
        self.page.update()
    
    def on_pdf_preview_click(self, e):
        """PDF 미리보기 버튼 클릭 핸들러"""
        if self.current_file_path and self.current_file_type == 'pdf':
            self.load_pdf_preview()
            self.page.dialog = self.pdf_viewer_dialog
            self.pdf_viewer_dialog.open = True
            self.page.update()
    
    def load_pdf_preview(self):
        """PDF 미리보기 로드"""
        try:
            # PDF 페이지를 이미지로 변환
            image_data = self.pdf_processor.pdf_page_to_image_bytes(
                self.current_file_path, 
                self.current_page_index
            )
            
            if image_data:
                # base64로 인코딩
                base64_data = base64.b64encode(image_data).decode()
                
                # 이미지 표시
                self.pdf_image_container.content = ft.Image(
                    src_base64=base64_data,
                    width=600,
                    height=700,
                    fit=ft.ImageFit.CONTAIN,
                )
                
                # 네비게이션 버튼 상태 업데이트
                self.prev_page_button.disabled = self.current_page_index == 0
                self.next_page_button.disabled = self.current_page_index >= self.current_pdf_info['page_count'] - 1
                self.page_info_text.value = f"{self.current_page_index + 1} / {self.current_pdf_info['page_count']}"
            else:
                self.pdf_image_container.content = ft.Text(
                    "PDF 페이지 로드 실패",
                    color=ft.Colors.RED_600
                )
        except Exception as e:
            logger.error(f"PDF 미리보기 로드 오류: {e}")
            self.pdf_image_container.content = ft.Text(
                f"미리보기 오류: {str(e)}",
                color=ft.Colors.RED_600
            )
    
    def on_prev_page_click(self, e):
        """이전 페이지 버튼 클릭"""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.load_pdf_preview()
            self.page.update()
    
    def on_next_page_click(self, e):
        """다음 페이지 버튼 클릭"""
        if self.current_page_index < self.current_pdf_info['page_count'] - 1:
            self.current_page_index += 1
            self.load_pdf_preview()
            self.page.update()
    
    def close_pdf_viewer(self, e):
        """PDF 뷰어 닫기"""
        self.pdf_viewer_dialog.open = False
        self.page.update()
    
    def on_analysis_start_click(self, e):
        """분석 시작 버튼 클릭 핸들러"""
        if not self.current_file_path or not self.current_file_type:
            return
            
        # PDF 분석의 경우 Gemini 분석기가 필요
        if self.current_file_type == 'pdf' and not self.gemini_analyzer:
            return
            
        # 분석을 별도 스레드에서 실행
        threading.Thread(target=self.run_analysis, daemon=True).start()
    
    def on_save_text_click(self, e):
        """텍스트 저장 버튼 클릭 핸들러"""
        self._save_results("text")
    
    def on_save_json_click(self, e):
        """JSON 저장 버튼 클릭 핸들러"""
        self._save_results("json")
    
    def on_save_csv_click(self, e):
        """CSV 저장 버튼 클릭 핸들러 (DXF 타이틀블럭 속성 전용)"""
        if not self.current_title_block_info:
            self.show_error_dialog("저장 오류", "저장할 타이틀블럭 속성 정보가 없습니다.")
            return
            
        try:
            # CSV 파일 저장
            import os
            filename = f"title_block_attributes_{os.path.basename(self.current_file_path).replace('.dxf', '')}"
            saved_path = self.csv_exporter.export_title_block_attributes(
                self.current_title_block_info, 
                filename
            )
            
            if saved_path:
                self.show_info_dialog(
                    "CSV 저장 완료", 
                    f"타이틀블럭 속성 정보가 CSV 파일로 저장되었습니다:\\n\\n{saved_path}"
                )
            else:
                self.show_error_dialog("저장 실패", "CSV 파일 저장 중 오류가 발생했습니다.")
                
        except Exception as e:
            logger.error(f"CSV 저장 중 오류: {e}")
            self.show_error_dialog("저장 오류", f"CSV 저장 중 오류가 발생했습니다:\\n{str(e)}")
    
    def _save_results(self, format_type: str):
        """결과 저장 공통 함수"""
        if not self.analysis_results or not self.current_pdf_info:
            self.show_error_dialog("저장 오류", "저장할 분석 결과가 없습니다.")
            return
            
        try:
            # 분석 설정 정보 수집
            analysis_settings = {
                "조직_유형": self.organization_selector.value,
                "페이지_선택": self.page_selector.value,
                "분석_모드": self.analysis_mode.value,
                "사용자_정의_프롬프트": self.custom_prompt.value if self.analysis_mode.value == "custom" else None,
                "분석_시간": DateTimeUtils.get_timestamp()
            }
            
            if format_type == "text":
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
        """분석 실행 (백그라운드 스레드) - PDF/DXF 지원"""
        try:
            self.analysis_start_time = time.time()
            
            if self.current_file_type == 'pdf':
                self._run_pdf_analysis()
            elif self.current_file_type == 'dxf':
                self._run_dxf_analysis()
            else:
                raise ValueError(f"지원하지 않는 파일 타입: {self.current_file_type}")
                
        except Exception as e:
            logger.error(f"분석 중 오류 발생: {e}")
            self.update_progress_ui(False, f"❌ 분석 오류: {str(e)}")
            self.show_error_dialog("분석 오류", f"분석 중 오류가 발생했습니다:\n{str(e)}")
    
    def _run_pdf_analysis(self):
        """PDF 파일 분석 실행"""
        self.update_progress_ui(True, "PDF 이미지 변환 중...")
        
        # 조직 유형 결정
        organization_type = "transportation"
        if self.organization_selector and self.organization_selector.value:
            if self.organization_selector.value == "한국도로공사":
                organization_type = "expressway"
            else:
                organization_type = "transportation"
        
        logger.info(f"선택된 조직 유형: {organization_type}")
        
        # 분석할 페이지 결정
        if self.page_selector.value == "첫 번째 페이지":
            pages_to_analyze = [0]
        else:
            pages_to_analyze = list(range(self.current_pdf_info['page_count']))
        
        # 분석 프롬프트 결정
        if self.analysis_mode.value == "custom":
            prompt = self.custom_prompt.value or Config.DEFAULT_PROMPT
        elif self.analysis_mode.value == "detailed":
            prompt = "이 PDF 이미지를 자세히 분석하여 다음 정보를 제공해주세요: 1) 문서 유형, 2) 주요 내용, 3) 도면/도표 정보, 4) 텍스트 내용, 5) 기타 특징"
        else:
            prompt = Config.DEFAULT_PROMPT
        
        # 페이지별 분석 수행
        total_pages = len(pages_to_analyze)
        self.analysis_results = {}
        
        for i, page_num in enumerate(pages_to_analyze):
            progress = (i + 1) / total_pages
            self.update_progress_ui(
                True, 
                f"페이지 {page_num + 1} 분석 중... ({i + 1}/{total_pages})",
                progress
            )
            
            # PDF 페이지를 base64로 변환
            base64_data = self.pdf_processor.pdf_page_to_base64(
                self.current_file_path, 
                page_num
            )
            
            if base64_data:
                # Gemini API로 분석
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
            self.update_progress_ui(False, f"✅ PDF 분석 완료! (소요시간: {duration_str})", 1.0)
        else:
            self.update_progress_ui(False, "✅ PDF 분석 완료!", 1.0)
    
    def _run_dxf_analysis(self):
        """DXF 파일 분석 실행"""
        self.update_progress_ui(True, "DXF 파일 분석 중...")
        
        try:
            # DXF 파일 처리
            result = self.dxf_processor.process_dxf_file_comprehensive(self.current_file_path)
            
            if result['success']:
                # 분석 결과 포맷팅
                self.analysis_results = {'dxf': result}
                
                # 결과 표시
                self.display_dxf_analysis_results(result)
                
                # 완료 상태로 업데이트
                if self.analysis_start_time:
                    duration = time.time() - self.analysis_start_time
                    duration_str = DateTimeUtils.format_duration(duration)
                    self.update_progress_ui(False, f"✅ DXF 분석 완료! (소요시간: {duration_str})", 1.0)
                else:
                    self.update_progress_ui(False, "✅ DXF 분석 완료!", 1.0)
            else:
                error_msg = result.get('error', '알 수 없는 오류')
                self.update_progress_ui(False, f"❌ DXF 분석 실패: {error_msg}")
                self.show_error_dialog("DXF 분석 오류", f"DXF 파일 분석에 실패했습니다:\n{error_msg}")
                
        except Exception as e:
            logger.error(f"DXF 분석 중 오류: {e}")
            self.update_progress_ui(False, f"❌ DXF 분석 오류: {str(e)}")
            self.show_error_dialog("DXF 분석 오류", f"DXF 분석 중 오류가 발생했습니다:\n{str(e)}")
    
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
                # 결과 텍스트 구성 - 줄바꿈 올바르게 처리
                result_text = "🎯 분석 요약\n"
                result_text += f"📊 분석된 페이지: {len(self.analysis_results)}개\n"
                result_text += f"⏰ 완료 시간: {DateTimeUtils.get_timestamp()}\n"
                result_text += f"🏢 조직 스키마: {self.organization_selector.value}\n"
                result_text += "=" * 60 + "\n\n"
                
                for page_num, result in self.analysis_results.items():
                    result_text += f"📋 페이지 {page_num + 1} 분석 결과\n"
                    result_text += "-" * 40 + "\n"
                    result_text += result
                    result_text += "\n\n" + "=" * 60 + "\n\n"
                
                self.results_text.value = result_text.strip()
                
                # 저장 버튼 활성화
                self.save_text_button.disabled = False
                self.save_json_button.disabled = False
                
                # PDF 분석이므로 CSV 버튼 숨김
                self.save_csv_button.visible = False
                self.save_csv_button.disabled = True
            else:
                self.results_text.value = "❌ 분석 결과가 없습니다."
                self.save_text_button.disabled = True
                self.save_json_button.disabled = True
                self.save_csv_button.visible = False
                self.save_csv_button.disabled = True
                
            self.page.update()
        
        # 메인 스레드에서 UI 업데이트
        self.page.run_thread(update_results)
    
    def display_dxf_analysis_results(self, dxf_result):
        """DXF 분석 결과 표시 - 타이틀블럭 속성 테이블 포함"""
        def update_results():
            if dxf_result and dxf_result['success']:
                # 타이틀블럭 정보 저장
                self.current_title_block_info = dxf_result.get('title_block')
                
                # 결과 텍스트 구성
                import os
                result_text = "🎯 DXF 분석 요약\n"
                result_text += f"📊 파일: {os.path.basename(dxf_result['file_path'])}\n"
                result_text += f"⏰ 완료 시간: {DateTimeUtils.get_timestamp()}\n"
                result_text += "=" * 60 + "\n\n"
                
                # 요약 정보
                summary = dxf_result.get('summary', {})
                result_text += "📋 분석 요약\n"
                result_text += "-" * 40 + "\n"
                result_text += f"전체 블록 수: {summary.get('total_blocks', 0)}\n"
                result_text += f"도곽 블록 발견: {'예' if summary.get('title_block_found', False) else '아니오'}\n"
                result_text += f"속성 수: {summary.get('attributes_count', 0)}\n"
                
                if summary.get('title_block_name'):
                    result_text += f"도곽 블록명: {summary['title_block_name']}\n"
                
                result_text += "\n"
                
                # 도곽 정보
                title_block = dxf_result.get('title_block')
                if title_block:
                    result_text += "🏗️ 도곽 정보\n"
                    result_text += "-" * 40 + "\n"
                    
                    fields = {
                        'drawing_name': '도면명',
                        'drawing_number': '도면번호',
                        'construction_field': '건설분야',
                        'construction_stage': '건설단계',
                        'scale': '축척',
                        'project_name': '프로젝트명',
                        'designer': '설계자',
                        'date': '날짜',
                        'revision': '리비전',
                        'location': '위치'
                    }
                    
                    for field, label in fields.items():
                        value = title_block.get(field)
                        if value:
                            result_text += f"{label}: {value}\n"
                    
                    # 바운딩 박스 정보
                    bbox = title_block.get('bounding_box')
                    if bbox:
                        result_text += "\n📐 도곽 위치 정보\n"
                        result_text += f"좌하단: ({bbox['min_x']:.2f}, {bbox['min_y']:.2f})\n"
                        result_text += f"우상단: ({bbox['max_x']:.2f}, {bbox['max_y']:.2f})\n"
                        result_text += f"크기: {bbox['max_x'] - bbox['min_x']:.2f} × {bbox['max_y'] - bbox['min_y']:.2f}\n"
                    
                    # 타이틀블럭 속성 테이블 생성
                    if title_block.get('all_attributes'):
                        result_text += "\n\n📊 타이틀블럭 속성 상세 정보\n"
                        result_text += "-" * 60 + "\n"
                        
                        # 테이블 데이터 생성
                        table_data = self.csv_exporter.create_attribute_table_data(title_block)
                        
                        if table_data:
                            # 테이블 헤더
                            result_text += f"{'No.':<4} {'Tag':<15} {'Text':<25} {'Prompt':<20} {'X':<8} {'Y':<8} {'Layer':<8}\n"
                            result_text += "-" * 100 + "\n"
                            
                            # 테이블 데이터 (최대 10개만 표시)
                            for i, row in enumerate(table_data[:10]):
                                result_text += f"{row['No.']:<4} {row['Tag'][:14]:<15} {row['Text'][:24]:<25} "
                                result_text += f"{row['Prompt'][:19]:<20} {row['X']:<8} {row['Y']:<8} {row['Layer'][:7]:<8}\n"
                            
                            if len(table_data) > 10:
                                result_text += f"... 외 {len(table_data) - 10}개 속성\n"
                            
                            result_text += f"\n💡 전체 {len(table_data)}개 속성을 CSV 파일로 저장할 수 있습니다.\n"
                
                # 블록 참조 정보
                block_refs = dxf_result.get('block_references', [])
                if block_refs:
                    result_text += f"\n📦 블록 참조 목록 ({len(block_refs)}개)\n"
                    result_text += "-" * 40 + "\n"
                    
                    for i, block_ref in enumerate(block_refs[:10]):  # 최대 10개까지만 표시
                        result_text += f"{i+1}. {block_ref.get('name', 'Unknown')}"
                        if block_ref.get('attributes'):
                            result_text += f" (속성 {len(block_ref['attributes'])}개)"
                        result_text += "\n"
                    
                    if len(block_refs) > 10:
                        result_text += f"... 외 {len(block_refs) - 10}개 블록\n"
                
                self.results_text.value = result_text.strip()
                
                # 저장 버튼 활성화
                self.save_text_button.disabled = False
                self.save_json_button.disabled = False
                
                # CSV 저장 버튼 표시 및 활성화 (타이틀블럭이 있는 경우)
                if self.current_title_block_info and self.current_title_block_info.get('all_attributes'):
                    self.save_csv_button.visible = True
                    self.save_csv_button.disabled = False
                else:
                    self.save_csv_button.visible = False
                    self.save_csv_button.disabled = True
                    
            else:
                self.results_text.value = "❌ DXF 분석 결과가 없습니다."
                self.save_text_button.disabled = True
                self.save_json_button.disabled = True
                self.save_csv_button.visible = False
                self.save_csv_button.disabled = True
                self.current_title_block_info = None
                
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
        app = DocumentAnalyzerApp(page)
        
        # UI 구성
        app.build_ui()
        
        logger.info("새로운 좌우 분할 레이아웃 애플리케이션 시작 완료")
        
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
