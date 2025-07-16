"""
다중 파일 처리 애플리케이션 클래스
여러 PDF/DXF 파일을 배치로 처리하고 결과를 CSV로 저장하는 기능을 제공합니다.

Author: Claude Assistant
Created: 2025-07-14
Version: 1.0.0
"""

import flet as ft
import asyncio
import logging
import os
from datetime import datetime
from typing import List, Optional
import time

# 프로젝트 모듈 임포트
from config import Config
from multi_file_processor import MultiFileProcessor, BatchProcessingConfig, generate_default_csv_filename
from ui_components import MultiFileUIComponents
from utils import DateTimeUtils

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiFileApp:
    """다중 파일 처리 애플리케이션 클래스"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_files = []
        self.processing_results = []
        self.is_processing = False
        self.is_cancelled = False
        self.is_paused = False
        self.processor = None
        
        # UI 컴포넌트 참조
        self.file_picker = None
        self.files_container = None
        self.clear_files_button = None
        self.batch_analysis_button = None
        
        # 배치 설정 컴포넌트
        self.organization_selector = None
        self.concurrent_files_slider = None
        self.enable_batch_mode = None
        self.save_intermediate_results = None
        self.include_error_files = None
        self.csv_output_path = None
        self.browse_button = None
        
        # 진행률 컴포넌트
        self.overall_progress_bar = None
        self.progress_text = None
        self.current_status_text = None
        self.timing_info = None
        self.log_container = None
        self.cancel_button = None
        self.pause_resume_button = None
        
        # 결과 컴포넌트
        self.summary_stats = None
        self.results_table = None
        self.save_csv_button = None
        self.save_cross_csv_button = None  # 새로 추가
        self.save_excel_button = None
        self.clear_results_button = None
        
        # 시간 추적
        self.start_time = None
        
        # Gemini API 키 확인
        self.init_processor()
    
    def init_processor(self):
        """다중 파일 처리기 초기화"""
        try:
            config_errors = Config.validate_config()
            if config_errors:
                logger.error(f"설정 오류: {config_errors}")
                return
                
            # Gemini API 키가 있는지 확인
            gemini_api_key = Config.get_gemini_api_key()
            if not gemini_api_key:
                logger.error("Gemini API 키가 설정되지 않았습니다")
                return
                
            self.processor = MultiFileProcessor(gemini_api_key)
            logger.info("다중 파일 처리기 초기화 완료")
            
        except Exception as e:
            logger.error(f"다중 파일 처리기 초기화 실패: {e}")
    
    def build_ui(self) -> ft.Column:
        """다중 파일 처리 UI 구성"""
        
        # 파일 업로드 섹션
        upload_section = self.create_file_upload_section()
        
        # 배치 설정 섹션
        settings_section = self.create_batch_settings_section()
        
        # 진행률 섹션
        progress_section = self.create_progress_section()
        
        # 결과 섹션
        results_section = self.create_results_section()
        
        # 좌측 컨트롤 패널
        left_panel = ft.Container(
            content=ft.Column([
                upload_section,
                ft.Divider(height=10),
                settings_section,
                ft.Divider(height=10),
                progress_section,
            ], scroll=ft.ScrollMode.AUTO),
            col={"sm": 12, "md": 5, "lg": 4},
            padding=10,
        )
        
        # 우측 결과 패널
        right_panel = ft.Container(
            content=results_section,
            col={"sm": 12, "md": 7, "lg": 8},
            padding=10,
        )
        
        # ResponsiveRow를 사용한 좌우 분할 레이아웃
        main_layout = ft.ResponsiveRow([left_panel, right_panel])
        
        return ft.Column([
            main_layout
        ], expand=True, scroll=ft.ScrollMode.AUTO)
    
    def create_file_upload_section(self) -> ft.Container:
        """파일 업로드 섹션 생성"""
        upload_container = MultiFileUIComponents.create_multi_file_upload_section(
            on_files_selected=self.on_files_selected,
            on_batch_analysis_click=self.on_batch_analysis_click,
            on_clear_files_click=self.on_clear_files_click
        )
        
        # 참조 저장
        self.file_picker = upload_container.content.controls[-1]  # 마지막 요소가 file_picker
        self.files_container = upload_container.content.controls[4]  # files_container
        self.clear_files_button = upload_container.content.controls[2].controls[1]
        self.batch_analysis_button = upload_container.content.controls[2].controls[2]
        
        # overlay에 추가
        self.page.overlay.append(self.file_picker)
        
        return upload_container
    
    def create_batch_settings_section(self) -> ft.Container:
        """배치 설정 섹션 생성"""
        (
            container,
            self.organization_selector,
            self.concurrent_files_slider,
            self.enable_batch_mode,
            self.save_intermediate_results,
            self.include_error_files,
            self.csv_output_path,
            self.browse_button
        ) = MultiFileUIComponents.create_batch_settings_section()
        
        # 슬라이더 변경 이벤트 처리
        self.concurrent_files_slider.on_change = self.on_concurrent_files_change
        
        # 경로 선택 버튼 이벤트 처리
        self.browse_button.on_click = self.on_browse_csv_path_click
        
        return container
    
    def create_progress_section(self) -> ft.Container:
        """진행률 섹션 생성"""
        (
            container,
            self.overall_progress_bar,
            self.progress_text,
            self.current_status_text,
            self.timing_info,
            self.log_container,
            self.cancel_button,
            self.pause_resume_button
        ) = MultiFileUIComponents.create_batch_progress_section()
        
        # 버튼 이벤트 처리
        self.cancel_button.on_click = self.on_cancel_click
        self.pause_resume_button.on_click = self.on_pause_resume_click
        
        return container
    
    def create_results_section(self) -> ft.Container:
        """결과 섹션 생성"""
        (
            container,
            self.summary_stats,
            self.results_table,
            self.save_csv_button,
            self.save_cross_csv_button,  # 새로 추가
            self.save_excel_button,
            self.clear_results_button
        ) = MultiFileUIComponents.create_batch_results_section()
        
        # 버튼 이벤트 처리
        self.save_csv_button.on_click = self.on_save_csv_click
        self.save_cross_csv_button.on_click = self.on_save_cross_csv_click  # 새로 추가
        self.save_excel_button.on_click = self.on_save_excel_click
        self.clear_results_button.on_click = self.on_clear_results_click
        
        return container
    
    # 이벤트 핸들러들
    
    def on_files_selected(self, e: ft.FilePickerResultEvent):
        """파일 선택 이벤트 핸들러"""
        if e.files:
            # 선택된 파일들을 기존 목록에 추가 (중복 제거)
            existing_paths = {f.path for f in self.selected_files}
            new_files = [f for f in e.files if f.path not in existing_paths]
            
            if new_files:
                self.selected_files.extend(new_files)
                MultiFileUIComponents.update_selected_files_list(
                    self.files_container,
                    self.selected_files,
                    self.clear_files_button,
                    self.batch_analysis_button
                )
                
                MultiFileUIComponents.add_log_message(
                    self.log_container,
                    f"{len(new_files)}개 파일 추가됨 (총 {len(self.selected_files)}개)",
                    "info"
                )
            else:
                MultiFileUIComponents.add_log_message(
                    self.log_container,
                    "선택된 파일들이 이미 목록에 있습니다",
                    "warning"
                )
        else:
            MultiFileUIComponents.add_log_message(
                self.log_container,
                "파일 선택이 취소되었습니다",
                "info"
            )
        
        self.page.update()
    
    def on_clear_files_click(self, e):
        """파일 목록 지우기 이벤트 핸들러"""
        file_count = len(self.selected_files)
        self.selected_files.clear()
        
        MultiFileUIComponents.update_selected_files_list(
            self.files_container,
            self.selected_files,
            self.clear_files_button,
            self.batch_analysis_button
        )
        
        MultiFileUIComponents.add_log_message(
            self.log_container,
            f"{file_count}개 파일 목록 초기화",
            "info"
        )
        
        self.page.update()
    
    def on_batch_analysis_click(self, e):
        """배치 분석 시작 이벤트 핸들러"""
        if not self.selected_files:
            return
            
        if self.is_processing:
            return
            
        if not self.processor:
            self.show_error_dialog("처리기 오류", "다중 파일 처리기가 초기화되지 않았습니다.")
            return
        
        # 비동기 처리 시작
        self.page.run_task(self.start_batch_processing)
    
    def on_concurrent_files_change(self, e):
        """동시 처리 수 변경 이벤트 핸들러"""
        value = int(e.control.value)
        # 슬라이더 레이블 업데이트
        # 상위 Container에서 텍스트 찾아서 업데이트
        try:
            settings_container = e.control.parent.parent  # Column -> Container
            text_control = settings_container.content.controls[2].controls[1].controls[0]  # 해당 텍스트
            text_control.value = f"동시 처리 수: {value}개"
            self.page.update()
        except:
            logger.warning("슬라이더 레이블 업데이트 실패")
    
    def on_browse_csv_path_click(self, e):
        """CSV 저장 경로 선택 이벤트 핸들러"""
        # 간단한 구현 - 현재 디렉토리 + 자동 생성 파일명 설정
        default_filename = generate_default_csv_filename()
        default_path = os.path.join(os.getcwd(), "results", default_filename)
        
        self.csv_output_path.value = default_path
        self.page.update()
        
        MultiFileUIComponents.add_log_message(
            self.log_container,
            f"CSV 저장 경로 설정: {default_filename}",
            "info"
        )
    
    def on_cancel_click(self, e):
        """처리 취소 이벤트 핸들러"""
        if self.is_processing:
            self.is_cancelled = True
            MultiFileUIComponents.add_log_message(
                self.log_container,
                "사용자가 처리를 취소했습니다",
                "warning"
            )
            self.page.update()
    
    def on_pause_resume_click(self, e):
        """일시정지/재개 이벤트 핸들러"""
        # 현재 구현에서는 단순한 토글 기능만 제공
        if self.is_processing:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_resume_button.text = "재개"
                self.pause_resume_button.icon = ft.Icons.PLAY_ARROW
                MultiFileUIComponents.add_log_message(
                    self.log_container,
                    "처리가 일시정지되었습니다",
                    "warning"
                )
            else:
                self.pause_resume_button.text = "일시정지"
                self.pause_resume_button.icon = ft.Icons.PAUSE
                MultiFileUIComponents.add_log_message(
                    self.log_container,
                    "처리가 재개되었습니다",
                    "success"
                )
            self.page.update()
    
    def on_save_csv_click(self, e):
        """CSV 저장 이벤트 핸들러"""
        if not self.processing_results:
            self.show_error_dialog("저장 오류", "저장할 결과가 없습니다.")
            return
        
        self.page.run_task(self.save_results_to_csv)
    
    def on_save_cross_csv_click(self, e):
        """Cross-Tabulated CSV 저장 이벤트 핸들러 (새로 추가)"""
        if not self.processing_results:
            self.show_error_dialog("저장 오류", "저장할 결과가 없습니다.")
            return
        
        self.page.run_task(self.save_cross_tabulated_csv)
    
    def on_save_excel_click(self, e):
        """Excel 저장 이벤트 핸들러"""
        if not self.processing_results:
            self.show_error_dialog("저장 오류", "저장할 결과가 없습니다.")
            return
        
        # Excel 저장 기능 (향후 구현)
        self.show_info_dialog("개발 중", "Excel 저장 기능은 곧 추가될 예정입니다.")
    
    def on_clear_results_click(self, e):
        """결과 초기화 이벤트 핸들러"""
        self.processing_results.clear()
        
        MultiFileUIComponents.update_batch_results(
            self.summary_stats,
            self.results_table,
            self.processing_results,
            self.save_csv_button,
            self.save_cross_csv_button,  # 새로 추가
            self.save_excel_button,
            self.clear_results_button
        )
        
        MultiFileUIComponents.add_log_message(
            self.log_container,
            "결과가 초기화되었습니다",
            "info"
        )
        
        self.page.update()
    
    # 비동기 처리 함수들
    
    async def start_batch_processing(self):
        """배치 처리 시작"""
        try:
            self.is_processing = True
            self.is_cancelled = False
            self.is_paused = False
            self.start_time = time.time()
            
            # UI 상태 업데이트
            self.batch_analysis_button.disabled = True
            self.cancel_button.disabled = False
            self.pause_resume_button.disabled = False
            
            # 처리 설정 구성
            config = BatchProcessingConfig(
                organization_type=self.organization_selector.value,
                enable_gemini_batch_mode=self.enable_batch_mode.value,
                max_concurrent_files=int(self.concurrent_files_slider.value),
                save_intermediate_results=self.save_intermediate_results.value,
                output_csv_path=self.csv_output_path.value or None,
                include_error_files=self.include_error_files.value
            )
            
            MultiFileUIComponents.add_log_message(
                self.log_container,
                f"배치 처리 시작: {len(self.selected_files)}개 파일",
                "info"
            )
            
            # 파일 경로 추출
            file_paths = [f.path for f in self.selected_files]
            
            # 진행률 콜백 함수
            def progress_callback(current: int, total: int, status: str):
                elapsed_time = time.time() - self.start_time if self.start_time else 0
                estimated_remaining = (elapsed_time / current * (total - current)) if current > 0 else 0
                
                MultiFileUIComponents.update_batch_progress(
                    self.overall_progress_bar,
                    self.progress_text,
                    self.current_status_text,
                    self.timing_info,
                    current,
                    total,
                    status,
                    elapsed_time,
                    estimated_remaining
                )
                
                MultiFileUIComponents.add_log_message(
                    self.log_container,
                    status,
                    "success" if "완료" in status else "info"
                )
                
                self.page.update()
            
            # 처리 실행
            self.processing_results = await self.processor.process_multiple_files(
                file_paths, config, progress_callback
            )
            
            # 결과 표시
            MultiFileUIComponents.update_batch_results(
                self.summary_stats,
                self.results_table,
                self.processing_results,
                self.save_csv_button,
                self.save_cross_csv_button,  # 새로 추가
                self.save_excel_button,
                self.clear_results_button
            )
            
            # 요약 정보
            summary = self.processor.get_processing_summary()
            MultiFileUIComponents.add_log_message(
                self.log_container,
                f"처리 완료! 성공: {summary['success_files']}, 실패: {summary['failed_files']}, 성공률: {summary['success_rate']}%",
                "success"
            )
            
        except Exception as e:
            logger.error(f"배치 처리 오류: {e}")
            MultiFileUIComponents.add_log_message(
                self.log_container,
                f"처리 오류: {str(e)}",
                "error"
            )
            self.show_error_dialog("처리 오류", f"배치 처리 중 오류가 발생했습니다:\n{str(e)}")
        
        finally:
            # UI 상태 복원
            self.is_processing = False
            self.batch_analysis_button.disabled = False
            self.cancel_button.disabled = True
            self.pause_resume_button.disabled = True
            self.pause_resume_button.text = "일시정지"
            self.pause_resume_button.icon = ft.Icons.PAUSE
            self.page.update()
    
    async def save_results_to_csv(self):
        """결과를 CSV로 저장"""
        try:
            if not self.processor:
                self.show_error_dialog("오류", "처리기가 초기화되지 않았습니다.")
                return
            
            # CSV 경로 설정
            output_path = self.csv_output_path.value
            if not output_path:
                # 자동 생성
                results_dir = os.path.join(os.getcwd(), "results")
                os.makedirs(results_dir, exist_ok=True)
                output_path = os.path.join(results_dir, generate_default_csv_filename())
            
            # CSV 저장
            await self.processor.save_results_to_csv(output_path)
            
            self.show_info_dialog(
                "저장 완료",
                f"배치 처리 결과가 CSV 파일로 저장되었습니다:\n\n{output_path}"
            )
            
            MultiFileUIComponents.add_log_message(
                self.log_container,
                f"CSV 저장 완료: {os.path.basename(output_path)}",
                "success"
            )
            
        except Exception as e:
            logger.error(f"CSV 저장 오류: {e}")
            self.show_error_dialog("저장 오류", f"CSV 저장 중 오류가 발생했습니다:\n{str(e)}")
            
            MultiFileUIComponents.add_log_message(
                self.log_container,
                f"CSV 저장 실패: {str(e)}",
                "error"
            )
    
    async def save_cross_tabulated_csv(self):
        """Cross-tabulated CSV로 저장 (새로 추가)"""
        try:
            # Cross-tabulated CSV 내보내기 모듈 임포트
            from cross_tabulated_csv_exporter import CrossTabulatedCSVExporter, generate_cross_tabulated_csv_filename
            
            exporter = CrossTabulatedCSVExporter()
            
            # CSV 경로 설정
            results_dir = os.path.join(os.getcwd(), "results")
            os.makedirs(results_dir, exist_ok=True)
            
            # Cross-tabulated CSV 파일명 생성
            cross_csv_filename = generate_cross_tabulated_csv_filename("batch_key_value_analysis")
            output_path = os.path.join(results_dir, cross_csv_filename)
            
            # Cross-tabulated CSV 저장
            success = exporter.export_cross_tabulated_csv(
                self.processing_results,
                output_path,
                include_coordinates=True,
                coordinate_source="auto"
            )
            
            if success:
                self.show_info_dialog(
                    "Key-Value CSV 저장 완료",
                    f"분석 결과가 Key-Value 형태의 CSV 파일로 저장되었습니다:\n\n{output_path}\n\n" +
                    "이 CSV는 다음과 같은 형태로 구성됩니다:\n" +
                    "- file_name: 파일명\n" +
                    "- file_type: 파일 형식\n" +
                    "- key: 속성 키\n" +
                    "- value: 속성 값\n" +
                    "- x, y: 좌표 정보 (가능한 경우)"
                )
                
                MultiFileUIComponents.add_log_message(
                    self.log_container,
                    f"Key-Value CSV 저장 완료: {os.path.basename(output_path)}",
                    "success"
                )
            else:
                self.show_error_dialog(
                    "저장 실패", 
                    "Key-Value CSV 저장에 실패했습니다. 로그를 확인해주세요."
                )
                
                MultiFileUIComponents.add_log_message(
                    self.log_container,
                    "Key-Value CSV 저장 실패",
                    "error"
                )
            
        except Exception as e:
            logger.error(f"Cross-tabulated CSV 저장 오류: {e}")
            self.show_error_dialog(
                "저장 오류", 
                f"Key-Value CSV 저장 중 오류가 발생했습니다:\n{str(e)}"
            )
            
            MultiFileUIComponents.add_log_message(
                self.log_container,
                f"Key-Value CSV 저장 실패: {str(e)}",
                "error"
            )
    
    # 유틸리티 함수들
    
    def show_error_dialog(self, title: str, message: str):
        """오류 다이얼로그 표시"""
        from ui_components import UIComponents
        
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
        from ui_components import UIComponents
        
        dialog = UIComponents.create_info_dialog(title, message)
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            
        dialog.actions[0].on_click = close_dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()


# 사용 예시
if __name__ == "__main__":
    def main_multi_file(page: ft.Page):
        """다중 파일 처리 앱 테스트 실행"""
        page.title = "다중 파일 처리 테스트"
        page.theme_mode = ft.ThemeMode.LIGHT
        
        app = MultiFileApp(page)
        ui = app.build_ui()
        page.add(ui)
    
    ft.app(target=main_multi_file)
