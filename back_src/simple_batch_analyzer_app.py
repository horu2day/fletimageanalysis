"""
간단한 다중 파일 PDF 분석 UI
getcode.py 스타일의 간단한 분석을 여러 파일에 적용하는 Flet 애플리케이션

Author: Claude Assistant
Created: 2025-07-14
Version: 1.0.0
Features:
- 다중 PDF 파일 선택
- getcode.py 프롬프트를 그대로 사용한 간단한 분석
- 실시간 진행률 표시
- 자동 CSV 저장
- 결과 요약 표시
"""

import asyncio
import flet as ft
import os
from datetime import datetime
from typing import List, Optional
import threading
import logging

from simple_batch_processor import SimpleBatchProcessor
from config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleBatchAnalyzerApp:
    """간단한 배치 분석 애플리케이션"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_files: List[str] = []
        self.processor: Optional[SimpleBatchProcessor] = None
        self.is_processing = False
        
        # UI 컴포넌트들
        self.file_picker = None
        self.selected_files_text = None
        self.progress_bar = None
        self.progress_text = None
        self.analyze_button = None
        self.results_text = None
        self.custom_prompt_field = None
        
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        """페이지 기본 설정"""
        self.page.title = "간단한 다중 PDF 분석기"
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.window.min_width = 800
        self.page.window.min_height = 600
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        
        # API 키 확인
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            self.show_error_dialog("Gemini API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            return
            
        self.processor = SimpleBatchProcessor(api_key)
        logger.info("간단한 배치 분석 앱 초기화 완료")
    
    def build_ui(self):
        """UI 구성 요소 생성"""
        
        # 제목
        title = ft.Text(
            "🔍 간단한 다중 PDF 분석기",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )
        
        subtitle = ft.Text(
            "getcode.py 스타일의 간단한 프롬프트로 여러 PDF 파일을 분석하고 결과를 CSV로 저장합니다.",
            size=14,
            color=ft.Colors.GREY_700
        )
        
        # 파일 선택 섹션
        self.file_picker = ft.FilePicker(
            on_result=self.on_files_selected
        )
        self.page.overlay.append(self.file_picker)
        
        file_select_button = ft.ElevatedButton(
            "📁 PDF 파일 선택",
            icon=ft.icons.FOLDER_OPEN,
            on_click=self.select_files,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600
            )
        )
        
        self.selected_files_text = ft.Text(
            "선택된 파일이 없습니다",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        # 사용자 정의 프롬프트 섹션
        self.custom_prompt_field = ft.TextField(
            label="사용자 정의 프롬프트 (비워두면 기본 프롬프트 사용)",
            hint_text="예: PDF 이미지를 분석하여 도면의 주요 정보를 알려주세요",
            multiline=True,
            min_lines=2,
            max_lines=4,
            width=850
        )
        
        default_prompt_text = ft.Text(
            "🔸 기본 프롬프트: \"pdf 이미지 분석하여 도면인지 어떤 정보들이 있는지 알려줘.\"",
            size=12,
            color=ft.Colors.GREY_600,
            italic=True
        )
        
        # 분석 시작 섹션
        self.analyze_button = ft.ElevatedButton(
            "🚀 분석 시작",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.start_analysis,
            disabled=True,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600
            )
        )
        
        # 진행률 섹션
        self.progress_bar = ft.ProgressBar(
            width=850,
            visible=False,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.BLUE_100
        )
        
        self.progress_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.BLUE_700,
            visible=False
        )
        
        # 결과 섹션
        self.results_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.BLACK,
            selectable=True
        )
        
        # 레이아웃 구성
        content = ft.Column([
            # 헤더
            ft.Container(
                content=ft.Column([title, subtitle]),
                margin=ft.margin.only(bottom=20)
            ),
            
            # 파일 선택
            ft.Container(
                content=ft.Column([
                    ft.Text("📁 파일 선택", size=16, weight=ft.FontWeight.BOLD),
                    file_select_button,
                    self.selected_files_text
                ]),
                bgcolor=ft.colors.GREY_50,
                padding=15,
                border_radius=10,
                margin=ft.margin.only(bottom=15)
            ),
            
            # 프롬프트 설정
            ft.Container(
                content=ft.Column([
                    ft.Text("✏️ 프롬프트 설정", size=16, weight=ft.FontWeight.BOLD),
                    self.custom_prompt_field,
                    default_prompt_text
                ]),
                bgcolor=ft.colors.GREY_50,
                padding=15,
                border_radius=10,
                margin=ft.margin.only(bottom=15)
            ),
            
            # 분석 시작
            ft.Container(
                content=ft.Column([
                    ft.Text("🔄 분석 실행", size=16, weight=ft.FontWeight.BOLD),
                    self.analyze_button,
                    self.progress_bar,
                    self.progress_text
                ]),
                bgcolor=ft.colors.GREY_50,
                padding=15,
                border_radius=10,
                margin=ft.margin.only(bottom=15)
            ),
            
            # 결과 표시
            ft.Container(
                content=ft.Column([
                    ft.Text("📊 분석 결과", size=16, weight=ft.FontWeight.BOLD),
                    self.results_text
                ]),
                bgcolor=ft.colors.GREY_50,
                padding=15,
                border_radius=10
            )
        ])
        
        # 스크롤 가능한 컨테이너로 감싸기
        scrollable_content = ft.Container(
            content=content,
            alignment=ft.alignment.top_center
        )
        
        self.page.add(scrollable_content)
        self.page.update()
    
    def select_files(self, e):
        """파일 선택 대화상자 열기"""
        self.file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["pdf"],
            dialog_title="분석할 PDF 파일들을 선택하세요"
        )
    
    def on_files_selected(self, e: ft.FilePickerResultEvent):
        """파일 선택 완료 후 처리"""
        if e.files:
            self.selected_files = [file.path for file in e.files]
            file_count = len(self.selected_files)
            
            if file_count == 1:
                self.selected_files_text.value = f"✅ {file_count}개 파일 선택됨: {os.path.basename(self.selected_files[0])}"
            else:
                self.selected_files_text.value = f"✅ {file_count}개 파일 선택됨"
            
            self.selected_files_text.color = ft.colors.GREEN_700
            self.analyze_button.disabled = False
            
            logger.info(f"{file_count}개 PDF 파일 선택완료")
        else:
            self.selected_files = []
            self.selected_files_text.value = "선택된 파일이 없습니다"
            self.selected_files_text.color = ft.colors.GREY_600
            self.analyze_button.disabled = True
        
        self.page.update()
    
    def start_analysis(self, e):
        """분석 시작"""
        if self.is_processing or not self.selected_files:
            return
        
        self.is_processing = True
        self.analyze_button.disabled = True
        self.progress_bar.visible = True
        self.progress_text.visible = True
        self.progress_bar.value = 0
        self.progress_text.value = "분석 준비 중..."
        self.results_text.value = ""
        
        self.page.update()
        
        # 백그라운드에서 비동기 처리 실행
        threading.Thread(target=self.run_analysis_async, daemon=True).start()
    
    def run_analysis_async(self):
        """비동기 분석 실행"""
        try:
            # 새 이벤트 루프 생성 (백그라운드 스레드에서)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 분석 실행
            loop.run_until_complete(self.process_files())
            
        except Exception as e:
            logger.error(f"분석 실행 중 오류: {e}")
            self.update_ui_on_error(str(e))
        finally:
            loop.close()
    
    async def process_files(self):
        """파일 처리 실행"""
        try:
            # 사용자 정의 프롬프트 확인
            custom_prompt = self.custom_prompt_field.value.strip()
            if not custom_prompt:
                custom_prompt = None
            
            # 진행률 콜백 함수
            def progress_callback(current: int, total: int, status: str):
                progress_value = current / total
                self.update_progress(progress_value, f"{current}/{total} - {status}")
            
            # 배치 처리 실행
            results = await self.processor.process_multiple_pdf_files(
                pdf_file_paths=self.selected_files,
                custom_prompt=custom_prompt,
                max_concurrent_files=2,  # 안정성을 위해 낮게 설정
                progress_callback=progress_callback
            )
            
            # 결과 요약
            summary = self.processor.get_processing_summary()
            self.update_ui_on_completion(summary)
            
        except Exception as e:
            logger.error(f"파일 처리 중 오류: {e}")
            self.update_ui_on_error(str(e))
    
    def update_progress(self, value: float, text: str):
        """진행률 업데이트 (스레드 안전)"""
        def update():
            self.progress_bar.value = value
            self.progress_text.value = text
            self.page.update()
        
        self.page.run_thread_safe(update)
    
    def update_ui_on_completion(self, summary: dict):
        """분석 완료 시 UI 업데이트"""
        def update():
            self.progress_bar.visible = False
            self.progress_text.visible = False
            self.analyze_button.disabled = False
            self.is_processing = False
            
            # 결과 요약 텍스트 생성
            result_text = "🎉 분석 완료!\n\n"
            result_text += f"📊 처리 요약:\n"
            result_text += f"• 전체 파일: {summary.get('total_files', 0)}개\n"
            result_text += f"• 성공: {summary.get('success_files', 0)}개\n"
            result_text += f"• 실패: {summary.get('failed_files', 0)}개\n"
            result_text += f"• 성공률: {summary.get('success_rate', 0)}%\n"
            result_text += f"• 전체 처리 시간: {summary.get('total_processing_time', 0)}초\n"
            result_text += f"• 평균 처리 시간: {summary.get('avg_processing_time', 0)}초/파일\n"
            result_text += f"• 전체 파일 크기: {summary.get('total_file_size_mb', 0)}MB\n\n"
            result_text += "💾 결과가 CSV 파일로 자동 저장되었습니다.\n"
            result_text += "파일 위치: D:/MYCLAUDE_PROJECT/fletimageanalysis/results/"
            
            self.results_text.value = result_text
            self.results_text.color = ft.colors.GREEN_700
            self.page.update()
            
            # 완료 알림
            self.show_success_dialog("분석이 완료되었습니다!", result_text)
        
        self.page.run_thread_safe(update)
    
    def update_ui_on_error(self, error_message: str):
        """오류 발생 시 UI 업데이트"""
        def update():
            self.progress_bar.visible = False
            self.progress_text.visible = False
            self.analyze_button.disabled = False
            self.is_processing = False
            
            self.results_text.value = f"❌ 분석 중 오류가 발생했습니다:\n{error_message}"
            self.results_text.color = ft.colors.RED_700
            self.page.update()
            
            self.show_error_dialog("분석 오류", error_message)
        
        self.page.run_thread_safe(update)
    
    def show_success_dialog(self, title: str, message: str):
        """성공 다이얼로그 표시"""
        def show():
            dialog = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Text(message, selectable=True),
                actions=[
                    ft.TextButton("확인", on_click=lambda e: self.close_dialog())
                ]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        
        self.page.run_thread_safe(show)
    
    def show_error_dialog(self, title: str, message: str = ""):
        """오류 다이얼로그 표시"""
        def show():
            dialog = ft.AlertDialog(
                title=ft.Text(title, color=ft.colors.RED_700),
                content=ft.Text(message if message else title, selectable=True),
                actions=[
                    ft.TextButton("확인", on_click=lambda e: self.close_dialog())
                ]
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        
        self.page.run_thread_safe(show)
    
    def close_dialog(self):
        """다이얼로그 닫기"""
        if self.page.overlay:
            for overlay in self.page.overlay:
                if isinstance(overlay, ft.AlertDialog):
                    overlay.open = False
            self.page.update()


async def main(page: ft.Page):
    """메인 함수"""
    app = SimpleBatchAnalyzerApp(page)


if __name__ == "__main__":
    # Flet 애플리케이션 실행
    ft.app(target=main, view=ft.AppView.FLET_APP)
