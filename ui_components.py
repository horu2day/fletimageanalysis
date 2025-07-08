"""
UI 컴포넌트 모듈
Flet 기반 사용자 인터페이스 컴포넌트들을 정의합니다.
"""

import flet as ft
from typing import Callable, Optional, List, Dict, Any
import logging
from config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UIComponents:
    """UI 컴포넌트 클래스"""
    
    @staticmethod
    def create_app_bar() -> ft.AppBar:
        """애플리케이션 상단 바 생성"""
        return ft.AppBar(
            title=ft.Text(
                Config.APP_TITLE,
                size=20,
                weight=ft.FontWeight.BOLD
            ),
            center_title=True,
            bgcolor=ft.colors.BLUE_600,
            color=ft.colors.WHITE,
            automatically_imply_leading=False,
        )
    
    @staticmethod
    def create_file_upload_section(
        on_file_selected: Callable,
        on_upload_click: Callable
    ) -> ft.Container:
        """파일 업로드 섹션 생성"""
        
        # 파일 선택기
        file_picker = ft.FilePicker(
            on_result=on_file_selected
        )
        
        # 선택된 파일 정보 텍스트
        selected_file_text = ft.Text(
            "선택된 파일이 없습니다",
            size=14,
            color=ft.colors.GREY_600
        )
        
        # 파일 선택 버튼
        select_button = ft.ElevatedButton(
            text="PDF 파일 선택",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: file_picker.pick_files(
                allowed_extensions=Config.ALLOWED_EXTENSIONS,
                allow_multiple=False
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_100,
                color=ft.colors.BLUE_800,
            )
        )
        
        # 업로드 버튼
        upload_button = ft.ElevatedButton(
            text="분석 시작",
            icon=ft.icons.ANALYTICS,
            on_click=on_upload_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.GREEN_100,
                color=ft.colors.GREEN_800,
            )
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📄 PDF 파일 업로드",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_800
                ),
                ft.Divider(),
                ft.Row([
                    select_button,
                    upload_button,
                ], alignment=ft.MainAxisAlignment.START),
                selected_file_text,
                file_picker,  # overlay에 추가될 컴포넌트
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    @staticmethod
    def create_analysis_settings_section() -> ft.Container:
        """분석 설정 섹션 생성"""
        
        # 페이지 선택 드롭다운
        page_selector = ft.Dropdown(
            label="분석할 페이지",
            value="첫 번째 페이지",
            options=[
                ft.dropdown.Option("첫 번째 페이지"),
                ft.dropdown.Option("모든 페이지"),
                ft.dropdown.Option("사용자 지정"),
            ],
            width=200,
        )
        
        # 분석 모드 선택
        analysis_mode = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="basic", label="기본 분석"),
                ft.Radio(value="detailed", label="상세 분석"),
                ft.Radio(value="custom", label="사용자 정의"),
            ]),
            value="basic"
        )
        
        # 사용자 정의 프롬프트
        custom_prompt = ft.TextField(
            label="사용자 정의 분석 요청",
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="분석하고 싶은 내용을 자세히 입력하세요...",
            visible=False,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "⚙️ 분석 설정",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ORANGE_800
                ),
                ft.Divider(),
                ft.Row([
                    ft.Column([
                        ft.Text("페이지 선택:", weight=ft.FontWeight.BOLD),
                        page_selector,
                    ], expand=1),
                    ft.Column([
                        ft.Text("분석 모드:", weight=ft.FontWeight.BOLD),
                        analysis_mode,
                    ], expand=1),
                ]),
                custom_prompt,
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    @staticmethod
    def create_progress_section() -> ft.Container:
        """진행률 표시 섹션 생성"""
        
        # 진행률 바
        progress_bar = ft.ProgressBar(
            width=400,
            color=ft.colors.BLUE_600,
            bgcolor=ft.colors.GREY_300,
            visible=False,
        )
        
        # 상태 텍스트
        status_text = ft.Text(
            "대기 중...",
            size=14,
            color=ft.colors.GREY_600
        )
        
        # 스피너
        progress_ring = ft.ProgressRing(
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
                    color=ft.colors.PURPLE_800
                ),
                ft.Divider(),
                ft.Row([
                    progress_ring,
                    ft.Column([
                        status_text,
                        progress_bar,
                    ], expand=1),
                ], alignment=ft.MainAxisAlignment.START),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    @staticmethod
    def create_results_section() -> ft.Container:
        """결과 표시 섹션 생성"""
        
        # 결과 텍스트 영역
        results_text = ft.Text(
            "분석 결과가 여기에 표시됩니다.",
            size=14,
            selectable=True,
        )
        
        # 결과 컨테이너
        results_container = ft.Container(
            content=ft.Column([
                results_text,
            ], scroll=ft.ScrollMode.AUTO),
            padding=15,
            height=300,
            bgcolor=ft.colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
        
        # 저장 버튼
        save_button = ft.ElevatedButton(
            text="결과 저장",
            icon=ft.icons.SAVE,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.TEAL_100,
                color=ft.colors.TEAL_800,
            )
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📋 분석 결과",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREEN_800
                    ),
                    save_button,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                results_container,
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    @staticmethod
    def create_pdf_preview_section() -> ft.Container:
        """PDF 미리보기 섹션 생성"""
        
        # 이미지 컨테이너
        image_container = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.icons.PICTURE_AS_PDF,
                    size=100,
                    color=ft.colors.GREY_400
                ),
                ft.Text(
                    "PDF 미리보기",
                    size=14,
                    color=ft.colors.GREY_600
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=300,
            height=400,
            bgcolor=ft.colors.GREY_100,
            border_radius=8,
            border=ft.border.all(1, ft.colors.GREY_300),
            alignment=ft.alignment.center,
        )
        
        # 페이지 네비게이션
        page_nav = ft.Row([
            ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                disabled=True,
            ),
            ft.Text("1 / 1", size=14),
            ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                disabled=True,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "👁️ PDF 미리보기",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.INDIGO_800
                ),
                ft.Divider(),
                image_container,
                page_nav,
            ], alignment=ft.MainAxisAlignment.START),
            padding=20,
            margin=10,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    @staticmethod
    def create_error_dialog(title: str, message: str) -> ft.AlertDialog:
        """오류 다이얼로그 생성"""
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Text(message),
            actions=[
                ft.TextButton("확인", on_click=lambda e: None),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    @staticmethod
    def create_info_dialog(title: str, message: str) -> ft.AlertDialog:
        """정보 다이얼로그 생성"""
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Text(message),
            actions=[
                ft.TextButton("확인", on_click=lambda e: None),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    @staticmethod
    def create_loading_overlay() -> ft.Container:
        """로딩 오버레이 생성"""
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text("처리 중...", size=16, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=200,
            height=100,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            border=ft.border.all(2, ft.colors.BLUE_600),
            alignment=ft.alignment.center,
        )

# 사용 예시
if __name__ == "__main__":
    def dummy_callback(*args, **kwargs):
        """더미 콜백 함수"""
        pass
    
    # UI 컴포넌트 테스트
    print("UI 컴포넌트 모듈 로드 완료")
    print(f"앱 제목: {Config.APP_TITLE}")
