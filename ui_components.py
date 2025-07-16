"""
UI 컴포넌트 모듈
Flet 기반 사용자 인터페이스 컴포넌트들을 정의합니다.
"""

import flet as ft
from typing import Callable
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
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            automatically_imply_leading=False,
        )
    
    @staticmethod
    def create_file_upload_section(
        on_file_selected: Callable,
        on_upload_click: Callable,
        organization_selector_ref: Callable = None
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
            color=ft.Colors.GREY_600
        )
        
        # 파일 선택 버튼
        select_button = ft.ElevatedButton(
            text="PDF/DXF 파일 선택",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=lambda _: file_picker.pick_files(
                allowed_extensions=Config.ALLOWED_EXTENSIONS,
                allow_multiple=False
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_100,
                color=ft.Colors.BLUE_800,
            )
        )
        
        # 업로드 버튼
        upload_button = ft.ElevatedButton(
            text="분석 시작",
            icon=ft.Icons.ANALYTICS,
            on_click=on_upload_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        # 반환되는 컨테이너에 organization_selector를 포함
        container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "📄 PDF/DXF 파일 업로드",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800
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
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return container
    
    @staticmethod  
    def create_analysis_settings_section_with_refs() -> tuple:
        """분석 설정 섹션 생성 및 참조 반환"""
        
        # 조직 선택 드롭다운
        organization_selector = ft.Dropdown(
            label="조직 유형",
            value="국토교통부",
            options=[
                ft.dropdown.Option("국토교통부"),
                ft.dropdown.Option("한국도로공사"),
            ],
            width=180,
            tooltip="분석할 도면의 조직 유형을 선택하세요",
        )
        
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
        
        # 조직별 설명 텍스트
        org_description = ft.Text(
            "💡 국토교통부: 일반 토목/건설 도면 스키마 적용\n" +
            "🛣️ 한국도로공사: 고속도로 전용 도면 스키마 적용",
            size=12,
            color=ft.Colors.BLUE_700,
            italic=True,
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "⚙️ 분석 설정",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ORANGE_800
                ),
                ft.Divider(),
                org_description,
                ft.Row([
                    ft.Column([
                        ft.Text("조직 유형:", weight=ft.FontWeight.BOLD),
                        organization_selector,
                    ], expand=1),
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
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # 컴포넌트 참조들과 함께 반환
        return container, organization_selector, page_selector, analysis_mode, custom_prompt
    
    @staticmethod
    def create_analysis_settings_section() -> ft.Container:
        """기본 분석 설정 섹션 생성 (이전 버전 호환성)"""
        container, _, _, _, _ = UIComponents.create_analysis_settings_section_with_refs()
        return container
    
    @staticmethod
    def create_progress_section() -> ft.Container:
        """진행률 표시 섹션 생성"""
        
        # 진행률 바
        progress_bar = ft.ProgressBar(
            width=400,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.GREY_300,
            visible=False,
        )
        
        # 상태 텍스트
        status_text = ft.Text(
            "대기 중...",
            size=14,
            color=ft.Colors.GREY_600
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
                    color=ft.Colors.PURPLE_800
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
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
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
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # 저장 버튼
        save_button = ft.ElevatedButton(
            text="결과 저장",
            icon=ft.Icons.SAVE,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.TEAL_100,
                color=ft.Colors.TEAL_800,
            )
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📋 분석 결과",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_800
                    ),
                    save_button,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                results_container,
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    @staticmethod
    def create_pdf_preview_section() -> ft.Container:
        """PDF 미리보기 섹션 생성"""
        
        # 이미지 컨테이너
        image_container = ft.Container(
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
        page_nav = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                disabled=True,
            ),
            ft.Text("1 / 1", size=14),
            ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD,
                disabled=True,
            ),
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
                image_container,
                page_nav,
            ], alignment=ft.MainAxisAlignment.START),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
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
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(2, ft.Colors.BLUE_600),
            alignment=ft.alignment.center,
        )
    
    @staticmethod
    def create_comprehensive_text_display(text_entities: list = None) -> ft.Container:
        """포괄적 텍스트 추출 결과 표시 섹션 생성"""
        
        # 텍스트 엔티티 데이터 테이블
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("유형", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("텍스트", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("위치 (X, Y)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("레이어", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("위치 종류", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("블록명", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=5,
            divider_thickness=1,
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=50,
            data_row_max_height=60,
        )
        
        # 통계 정보 표시
        stats_container = ft.Container(
            content=ft.Column([
                ft.Text("📊 추출 통계", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("총 텍스트 엔티티: 0개", size=14),
                ft.Text("모델스페이스: 0개", size=14),
                ft.Text("페이퍼스페이스: 0개", size=14),
                ft.Text("블록 내부: 0개", size=14),
                ft.Text("비도곽 속성: 0개", size=14),
            ]),
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            width=250,
        )
        
        # CSV 저장 버튼
        csv_save_button = ft.ElevatedButton(
            text="CSV로 저장",
            icon=ft.Icons.SAVE_AS,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        # JSON 저장 버튼
        json_save_button = ft.ElevatedButton(
            text="JSON으로 저장",
            icon=ft.Icons.CODE,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        # 필터링 옵션
        filter_container = ft.Container(
            content=ft.Row([
                ft.Dropdown(
                    label="유형 필터",
                    value="전체",
                    options=[
                        ft.dropdown.Option("전체"),
                        ft.dropdown.Option("TEXT"),
                        ft.dropdown.Option("MTEXT"),
                        ft.dropdown.Option("ATTRIB"),
                    ],
                    width=150,
                ),
                ft.Dropdown(
                    label="위치 필터",
                    value="전체",
                    options=[
                        ft.dropdown.Option("전체"),
                        ft.dropdown.Option("ModelSpace"),
                        ft.dropdown.Option("PaperSpace"),
                        ft.dropdown.Option("Block"),
                    ],
                    width=150,
                ),
                ft.TextField(
                    label="텍스트 검색",
                    hint_text="검색할 텍스트 입력...",
                    width=200,
                ),
            ], spacing=10),
            padding=10,
        )
        
        # 테이블 컨테이너 (스크롤 가능)
        table_container = ft.Container(
            content=ft.Column([
                filter_container,
                ft.Container(
                    content=data_table,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=5,
                ),
            ], scroll=ft.ScrollMode.AUTO),
            height=400,
            expand=True,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📝 DXF 텍스트 엔티티 추출 결과",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.TEAL_800
                    ),
                    ft.Row([
                        csv_save_button,
                        json_save_button,
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row([
                    stats_container,
                    table_container,
                ], spacing=20, expand=True),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            expand=True,
        )
    
    @staticmethod
    def update_comprehensive_text_display(container: ft.Container, text_entities: list, stats: dict) -> None:
        """포괄적 텍스트 표시 업데이트"""
        try:
            # 통계 정보 업데이트
            stats_column = container.content.controls[2].controls[0].content  # stats_container의 Column
            stats_column.controls[2] = ft.Text(f"총 텍스트 엔티티: {stats.get('total_count', 0)}개", size=14)
            stats_column.controls[3] = ft.Text(f"모델스페이스: {len(stats.get('modelspace_texts', []))}개", size=14)
            stats_column.controls[4] = ft.Text(f"페이퍼스페이스: {len(stats.get('paperspace_texts', []))}개", size=14)
            stats_column.controls[5] = ft.Text(f"블록 내부: {len(stats.get('block_texts', []))}개", size=14)
            stats_column.controls[6] = ft.Text(f"비도곽 속성: {len(stats.get('non_title_block_attributes', []))}개", size=14)
            
            # 데이터 테이블 업데이트
            table_container = container.content.controls[2].controls[1]  # table_container
            data_table = table_container.content.controls[1].content  # data_table
            
            # 테이블 행 생성
            rows = []
            for i, entity in enumerate(text_entities[:100]):  # 처음 100개만 표시
                # 텍스트 길이 제한
                display_text = entity.get('text', '')[:30] + '...' if len(entity.get('text', '')) > 30 else entity.get('text', '')
                position_text = f"({entity.get('position_x', 0):.1f}, {entity.get('position_y', 0):.1f})"
                
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(entity.get('entity_type', 'N/A'), size=12)),
                            ft.DataCell(ft.Text(display_text, size=12, tooltip=entity.get('text', ''))),
                            ft.DataCell(ft.Text(position_text, size=12)),
                            ft.DataCell(ft.Text(entity.get('layer', 'N/A'), size=12)),
                            ft.DataCell(ft.Text(entity.get('location_type', 'N/A'), size=12)),
                            ft.DataCell(ft.Text(entity.get('parent_block', 'N/A') or 'N/A', size=12)),
                        ],
                        color=ft.Colors.BLUE_50 if i % 2 == 0 else ft.Colors.WHITE
                    )
                )
            
            data_table.rows = rows
            
            # 저장 버튼 활성화
            header_row = container.content.controls[0]  # 헤더 Row
            button_row = header_row.controls[1]  # 버튼들이 있는 Row
            button_row.controls[0].disabled = False  # CSV 버튼
            button_row.controls[1].disabled = False  # JSON 버튼
            
            logger.info(f"포괄적 텍스트 표시 업데이트 완료: {len(text_entities)}개 엔티티")
            
        except Exception as e:
            logger.error(f"포괄적 텍스트 표시 업데이트 실패: {e}")
    
    @staticmethod
    def create_dxf_analysis_summary(title_block_info: dict = None, block_count: int = 0) -> ft.Container:
        """DXF 분석 요약 정보 표시"""
        
        # 도곽 정보 표시
        title_block_content = []
        if title_block_info:
            title_block_content = [
                ft.Text("📋 도곽 정보", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Divider(),
                ft.Text(f"블록명: {title_block_info.get('block_name', 'N/A')}", size=14),
                ft.Text(f"도면명: {title_block_info.get('drawing_name', 'N/A')}", size=14),
                ft.Text(f"도면번호: {title_block_info.get('drawing_number', 'N/A')}", size=14),
                ft.Text(f"축척: {title_block_info.get('scale', 'N/A')}", size=14),
                ft.Text(f"속성 개수: {title_block_info.get('attributes_count', 0)}개", size=14),
            ]
        else:
            title_block_content = [
                ft.Text("📋 도곽 정보", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Text("도곽 블록을 찾을 수 없습니다.", size=14, color=ft.Colors.GREY_600),
            ]
        
        # 전체 분석 요약
        summary_content = [
            ft.Text("📊 분석 요약", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800),
            ft.Divider(),
            ft.Text(f"총 블록 참조: {block_count}개", size=14),
            ft.Text(f"도곽 발견: {'예' if title_block_info else '아니오'}", size=14),
        ]
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column(title_block_content),
                    padding=15,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    expand=1,
                ),
                ft.Container(
                    content=ft.Column(summary_content),
                    padding=15,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREEN_200),
                    expand=1,
                ),
            ], spacing=20),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )

# 사용 예시
if __name__ == "__main__":
    def dummy_callback(*args, **kwargs):
        """더미 콜백 함수"""
        pass
    
    # UI 컴포넌트 테스트
    print("UI 컴포넌트 모듈 로드 완료")
    print(f"앱 제목: {Config.APP_TITLE}")


class MultiFileUIComponents:
    """다중 파일 처리를 위한 UI 컴포넌트 클래스"""
    
    @staticmethod
    def create_multi_file_upload_section(
        on_files_selected: Callable,
        on_batch_analysis_click: Callable,
        on_clear_files_click: Callable
    ) -> ft.Container:
        """다중 파일 업로드 섹션 생성"""
        
        # 파일 선택기
        file_picker = ft.FilePicker(
            on_result=on_files_selected
        )
        
        # 선택된 파일 목록 표시
        selected_files_list = ft.Column(
            controls=[
                ft.Text(
                    "선택된 파일이 없습니다",
                    size=14,
                    color=ft.Colors.GREY_600
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            height=150,
        )
        
        # 파일 선택 버튰
        select_files_button = ft.ElevatedButton(
            text="여러 PDF/DXF 파일 선택",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=lambda _: file_picker.pick_files(
                allowed_extensions=Config.ALLOWED_EXTENSIONS,
                allow_multiple=True
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_100,
                color=ft.Colors.BLUE_800,
            )
        )
        
        # 파일 지우기 버튰
        clear_files_button = ft.ElevatedButton(
            text="목록 지우기",
            icon=ft.Icons.CLEAR,
            on_click=on_clear_files_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        # 배치 분석 버튰
        batch_analysis_button = ft.ElevatedButton(
            text="배치 분석 시작",
            icon=ft.Icons.BATCH_PREDICTION,
            on_click=on_batch_analysis_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        # 파일 목록 컸테이너
        files_container = ft.Container(
            content=selected_files_list,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📄 다중 PDF/DXF 파일 배치 처리",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800
                ),
                ft.Divider(),
                ft.Row([
                    select_files_button,
                    clear_files_button,
                    batch_analysis_button,
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Text(
                    "선택된 파일 목록:",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700
                ),
                files_container,
                file_picker,  # overlay에 추가될 컴포넌트
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    @staticmethod
    def create_batch_settings_section() -> tuple:
        """배치 처리 설정 섹션 생성 및 참조 반환"""
        
        # 조직 선택 드롭다운
        organization_selector = ft.Dropdown(
            label="조직 유형",
            value="국토교통부",
            options=[
                ft.dropdown.Option("국토교통부"),
                ft.dropdown.Option("한국도로공사"),
            ],
            width=180,
            tooltip="분석할 도면의 조직 유형을 선택하세요",
        )
        
        # 동시 처리 수 설정
        concurrent_files_slider = ft.Slider(
            min=1,
            max=5,
            divisions=4,
            value=3,
            label="{value}개",
            width=200,
        )
        
        # Gemini 배치 모드 설정
        enable_batch_mode = ft.Switch(
            label="Gemini 배치 모드 (50% 할인)",
            value=False,
            tooltip="비실시간 처리로 24시간 내 결과, 50% 비용 절약",
        )
        
        # 중간 결과 저장 설정
        save_intermediate_results = ft.Switch(
            label="중간 결과 저장",
            value=True,
            tooltip="각 파일 처리 후 즉시 결과 저장",
        )
        
        # 오류 파일 포함 설정
        include_error_files = ft.Switch(
            label="오류 파일 CSV 포함",
            value=True,
            tooltip="처리 실패한 파일도 CSV에 기록",
        )
        
        # CSV 출력 경로 설정
        csv_output_path = ft.TextField(
            label="CSV 출력 경로 (선택사항)",
            hint_text="비워두면 자동 생성...",
            width=300,
        )
        
        # 경로 선택 버튰
        browse_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="저장 위치 선택",
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "⚙️ 배치 처리 설정",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ORANGE_800
                ),
                ft.Divider(),
                ft.Row([
                    ft.Column([
                        ft.Text("조직 유형:", weight=ft.FontWeight.BOLD),
                        organization_selector,
                    ], expand=1),
                    ft.Column([
                        ft.Text(f"동시 처리 수: {int(concurrent_files_slider.value)}개", weight=ft.FontWeight.BOLD),
                        concurrent_files_slider,
                    ], expand=1),
                ]),
                ft.Divider(),
                ft.Column([
                    enable_batch_mode,
                    save_intermediate_results,
                    include_error_files,
                ], spacing=10),
                ft.Divider(),
                ft.Row([
                    csv_output_path,
                    browse_button,
                ], alignment=ft.MainAxisAlignment.START),
                ft.Text(
                    "💡 팁: 배치 모드를 사용하면 비용을 50% 절약할 수 있지만, 결과를 받기까지 더 오래 걸립니다.",
                    size=12,
                    color=ft.Colors.BLUE_700,
                    italic=True,
                ),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return (
            container,
            organization_selector,
            concurrent_files_slider,
            enable_batch_mode,
            save_intermediate_results,
            include_error_files,
            csv_output_path,
            browse_button
        )
    
    @staticmethod
    def create_batch_progress_section() -> tuple:
        """배치 처리 진행률 섹션 생성"""
        
        # 전체 진행률 바
        overall_progress_bar = ft.ProgressBar(
            width=400,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.GREY_300,
            value=0,
            visible=False,
        )
        
        # 진행률 텅스트
        progress_text = ft.Text(
            "0 / 0 파일 처리 완료 (0%)",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_800
        )
        
        # 현재 처리 중인 파일 상태
        current_status_text = ft.Text(
            "대기 중...",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        # 처리 시간 정보
        timing_info = ft.Text(
            "추정 남은 시간: -",
            size=12,
            color=ft.Colors.GREY_500
        )
        
        # 실시간 로그
        log_container = ft.Container(
            content=ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
            ),
            height=150,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # 취소 버튰
        cancel_button = ft.ElevatedButton(
            text="처리 취소",
            icon=ft.Icons.CANCEL,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_100,
                color=ft.Colors.RED_800,
            )
        )
        
        # 일시정지/재개 버튰
        pause_resume_button = ft.ElevatedButton(
            text="일시정지",
            icon=ft.Icons.PAUSE,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.YELLOW_100,
                color=ft.Colors.YELLOW_800,
            )
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📈 배치 처리 진행상황",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PURPLE_800
                    ),
                    ft.Row([
                        pause_resume_button,
                        cancel_button,
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                progress_text,
                overall_progress_bar,
                current_status_text,
                timing_info,
                ft.Text(
                    "📜 실시간 로그:",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_700
                ),
                log_container,
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return (
            container,
            overall_progress_bar,
            progress_text,
            current_status_text,
            timing_info,
            log_container,
            cancel_button,
            pause_resume_button
        )
    
    @staticmethod
    def create_batch_results_section() -> tuple:
        """배치 처리 결과 섹션 생성"""
        
        # 결과 요약 통계
        summary_stats = ft.Container(
            content=ft.Column([
                ft.Text("📈 처리 요약", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("총 파일: 0개", size=14),
                ft.Text("성공: 0개", size=14, color=ft.Colors.GREEN_600),
                ft.Text("실패: 0개", size=14, color=ft.Colors.RED_600),
                ft.Text("성공률: 0%", size=14),
                ft.Text("총 처리시간: 0초", size=14),
                ft.Text("평균 처리시간: 0초", size=14),
            ]),
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            width=250,
        )
        
        # 결과 테이블
        results_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("파일명", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("유형", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("크기(MB)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("상태", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("처리시간(s)", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=5,
            divider_thickness=1,
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=50,
            data_row_max_height=60,
        )
        
        # 테이블 컸테이너 (스크롤 가능)
        table_container = ft.Container(
            content=results_table,
            height=300,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=5,
            expand=True,
        )
        
        # CSV 저장 버튰
        save_csv_button = ft.ElevatedButton(
            text="CSV로 저장",
            icon=ft.Icons.SAVE_AS,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        # Excel 저장 버튰
        save_excel_button = ft.ElevatedButton(
            text="Excel로 저장",
            icon=ft.Icons.TABLE_CHART,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        # 결과 초기화 버튴
        clear_results_button = ft.ElevatedButton(
            text="결과 초기화",
            icon=ft.Icons.REFRESH,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_100,
                color=ft.Colors.GREY_800,
            )
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📄 배치 처리 결과",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_800
                    ),
                    ft.Row([
                        save_csv_button,
                        save_excel_button,
                        clear_results_button,
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row([
                    summary_stats,
                    table_container,
                ], spacing=20, expand=True),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            expand=True,
        )
        
        return (
            container,
            summary_stats,
            results_table,
            save_csv_button,
            save_excel_button,
            clear_results_button
        )
    
    @staticmethod
    def update_selected_files_list(
        files_container: ft.Container,
        selected_files: list,
        clear_button: ft.ElevatedButton,
        batch_button: ft.ElevatedButton
    ) -> None:
        """선택된 파일 목록 업데이트"""
        try:
            # 파일 목록 컸테이너 찾기
            column = files_container.content  # Column
            
            if not selected_files:
                # 파일이 없을 때
                column.controls = [
                    ft.Text(
                        "선택된 파일이 없습니다",
                        size=14,
                        color=ft.Colors.GREY_600
                    )
                ]
                clear_button.disabled = True
                batch_button.disabled = True
            else:
                # 파일 목록 표시
                file_controls = []
                total_size = 0
                
                for i, file_info in enumerate(selected_files, 1):
                    file_size_mb = file_info.size / (1024 * 1024) if file_info.size else 0
                    total_size += file_size_mb
                    
                    file_controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(
                                    ft.Icons.PICTURE_AS_PDF if file_info.name.lower().endswith('.pdf') else ft.Icons.ARCHITECTURE,
                                    size=20,
                                    color=ft.Colors.BLUE_600
                                ),
                                ft.Column([
                                    ft.Text(
                                        f"{i}. {file_info.name}",
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK87
                                    ),
                                    ft.Text(
                                        f"{file_size_mb:.1f} MB",
                                        size=11,
                                        color=ft.Colors.GREY_600
                                    ),
                                ], spacing=2, expand=True),
                            ], spacing=10),
                            padding=8,
                            bgcolor=ft.Colors.BLUE_50 if i % 2 == 0 else ft.Colors.WHITE,
                            border_radius=4,
                        )
                    )
                
                # 요약 정보 추가
                file_controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"전체: {len(selected_files)}개 파일, {total_size:.1f} MB",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_800
                        ),
                        padding=ft.padding.symmetric(vertical=5),
                        bgcolor=ft.Colors.BLUE_100,
                        border_radius=4,
                        alignment=ft.alignment.center,
                    )
                )
                
                column.controls = file_controls
                clear_button.disabled = False
                batch_button.disabled = False
            
            logger.info(f"파일 목록 업데이트 완료: {len(selected_files)}개 파일")
            
        except Exception as e:
            logger.error(f"파일 목록 업데이트 실패: {e}")
    
    @staticmethod
    def update_batch_progress(
        progress_bar: ft.ProgressBar,
        progress_text: ft.Text,
        current_status_text: ft.Text,
        timing_info: ft.Text,
        current: int,
        total: int,
        status: str,
        elapsed_time: float = 0,
        estimated_remaining: float = 0
    ) -> None:
        """배치 처리 진행률 업데이트"""
        try:
            if total > 0:
                progress_value = current / total
                progress_bar.value = progress_value
                progress_bar.visible = True
                
                progress_percentage = progress_value * 100
                progress_text.value = f"{current} / {total} 파일 처리 완료 ({progress_percentage:.1f}%)"
            else:
                progress_bar.visible = False
                progress_text.value = "처리 대기 중..."
            
            current_status_text.value = status
            
            # 시간 정보 업데이트
            if elapsed_time > 0 and estimated_remaining > 0:
                timing_info.value = f"경과 시간: {elapsed_time:.1f}초, 추정 남은 시간: {estimated_remaining:.1f}초"
            elif elapsed_time > 0:
                timing_info.value = f"경과 시간: {elapsed_time:.1f}초"
            else:
                timing_info.value = "추정 남은 시간: -"
            
        except Exception as e:
            logger.error(f"진행률 업데이트 실패: {e}")
    
    @staticmethod
    def add_log_message(
        log_container: ft.Container,
        message: str,
        level: str = "info"
    ) -> None:
        """로그 메시지 추가"""
        try:
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # 레벨에 따른 색상 설정
            color = ft.Colors.BLACK87
            icon = ft.Icons.INFO
            
            if level == "error":
                color = ft.Colors.RED_600
                icon = ft.Icons.ERROR
            elif level == "warning":
                color = ft.Colors.ORANGE_600
                icon = ft.Icons.WARNING
            elif level == "success":
                color = ft.Colors.GREEN_600
                icon = ft.Icons.CHECK_CIRCLE
            
            log_entry = ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=16, color=color),
                    ft.Text(f"[{timestamp}]", size=11, color=ft.Colors.GREY_600),
                    ft.Text(message, size=12, color=color, expand=True),
                ], spacing=5),
                padding=ft.padding.symmetric(vertical=2, horizontal=5),
            )
            
            # 로그 컸테이너에 추가
            log_column = log_container.content
            log_column.controls.append(log_entry)
            
            # 최대 100개 로그만 유지
            if len(log_column.controls) > 100:
                log_column.controls = log_column.controls[-100:]
            
            # 자동 스크롤 (마지막 메시지로)
            # log_column.scroll_to(offset=-1)  # Flet에서 지원 시 사용
            
        except Exception as e:
            logger.error(f"로그 메시지 추가 실패: {e}")
    
    @staticmethod
    def update_batch_results(
        summary_stats: ft.Container,
        results_table: ft.DataTable,
        processing_results: list,
        save_csv_button: ft.ElevatedButton,
        save_excel_button: ft.ElevatedButton,
        clear_results_button: ft.ElevatedButton
    ) -> None:
        """배치 처리 결과 업데이트"""
        try:
            # 요약 통계 계산
            total_files = len(processing_results)
            success_files = sum(1 for r in processing_results if r.success)
            failed_files = total_files - success_files
            success_rate = (success_files / total_files * 100) if total_files > 0 else 0
            
            total_processing_time = sum(r.processing_time for r in processing_results)
            avg_processing_time = total_processing_time / total_files if total_files > 0 else 0
            
            # 요약 통계 업데이트
            stats_column = summary_stats.content
            stats_column.controls[2] = ft.Text(f"총 파일: {total_files}개", size=14)
            stats_column.controls[3] = ft.Text(f"성공: {success_files}개", size=14, color=ft.Colors.GREEN_600)
            stats_column.controls[4] = ft.Text(f"실패: {failed_files}개", size=14, color=ft.Colors.RED_600)
            stats_column.controls[5] = ft.Text(f"성공률: {success_rate:.1f}%", size=14)
            stats_column.controls[6] = ft.Text(f"총 처리시간: {total_processing_time:.1f}초", size=14)
            stats_column.controls[7] = ft.Text(f"평균 처리시간: {avg_processing_time:.1f}초", size=14)
            
            # 결과 테이블 업데이트
            rows = []
            for i, result in enumerate(processing_results):
                status_icon = "✅" if result.success else "❌"
                status_text = f"{status_icon} 성공" if result.success else f"{status_icon} 실패"
                file_size_mb = result.file_size / (1024 * 1024) if result.file_size else 0
                
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(result.file_name[:30] + '...' if len(result.file_name) > 30 else result.file_name, size=12)),
                            ft.DataCell(ft.Text(result.file_type, size=12)),
                            ft.DataCell(ft.Text(f"{file_size_mb:.1f}", size=12)),
                            ft.DataCell(ft.Text(status_text, size=12)),
                            ft.DataCell(ft.Text(f"{result.processing_time:.1f}", size=12)),
                        ],
                        color=ft.Colors.GREEN_50 if result.success else ft.Colors.RED_50
                    )
                )
            
            results_table.rows = rows
            
            # 저장 버튴 활성화
            has_results = total_files > 0
            save_csv_button.disabled = not has_results
            save_excel_button.disabled = not has_results
            clear_results_button.disabled = not has_results
            
            logger.info(f"배치 결과 업데이트 완료: {total_files}개 파일")
            
        except Exception as e:
            logger.error(f"배치 결과 업데이트 실패: {e}")


class MultiFileUIComponents:
    """다중 파일 처리 UI 컴포넌트 클래스"""
    
    @staticmethod
    def create_multi_file_upload_section(
        on_files_selected: Callable,
        on_batch_analysis_click: Callable,
        on_clear_files_click: Callable
    ) -> ft.Container:
        """다중 파일 업로드 섹션 생성"""
        
        # 파일 선택기 (다중 선택 지원)
        file_picker = ft.FilePicker(
            on_result=on_files_selected
        )
        
        # 파일 선택 버튼
        select_files_button = ft.ElevatedButton(
            text="파일 선택",
            icon=ft.Icons.ADD_CIRCLE,
            on_click=lambda _: file_picker.pick_files(
                allowed_extensions=Config.ALLOWED_EXTENSIONS,
                allow_multiple=True  # 다중 선택 허용
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_100,
                color=ft.Colors.BLUE_800,
            )
        )
        
        # 파일 목록 지우기 버튼
        clear_files_button = ft.ElevatedButton(
            text="목록 지우기",
            icon=ft.Icons.CLEAR_ALL,
            on_click=on_clear_files_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        # 배치 분석 시작 버튼
        batch_analysis_button = ft.ElevatedButton(
            text="배치 분석 시작",
            icon=ft.Icons.PLAY_ARROW,
            on_click=on_batch_analysis_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        # 선택된 파일 목록 컨테이너
        files_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "선택된 파일이 없습니다",
                    size=14,
                    color=ft.Colors.GREY_600
                )
            ], scroll=ft.ScrollMode.AUTO),
            height=200,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "📁 다중 파일 업로드",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800
                ),
                ft.Divider(),
                ft.Row([
                    select_files_button,
                    clear_files_button,
                    batch_analysis_button,
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Text("선택된 파일 목록:", weight=ft.FontWeight.BOLD),
                files_container,
                file_picker,  # overlay에 추가될 컴포넌트
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return container
    
    @staticmethod
    def create_batch_settings_section() -> tuple:
        """배치 설정 섹션 생성"""
        
        # 조직 선택 드롭다운
        organization_selector = ft.Dropdown(
            label="조직 유형",
            value="국토교통부",
            options=[
                ft.dropdown.Option("국토교통부"),
                ft.dropdown.Option("한국도로공사"),
            ],
            width=180,
            tooltip="분석할 도면의 조직 유형을 선택하세요",
        )
        
        # 동시 처리 수 슬라이더
        concurrent_files_slider = ft.Slider(
            min=1,
            max=5,
            value=3,
            divisions=4,
            label="{value}개",
            width=200,
        )
        
        # 배치 모드 체크박스
        enable_batch_mode = ft.Checkbox(
            label="Gemini 배치 모드 사용",
            value=False,
            tooltip="대량 파일 처리 시 성능 향상",
        )
        
        # 중간 결과 저장 체크박스
        save_intermediate_results = ft.Checkbox(
            label="중간 결과 저장",
            value=True,
            tooltip="처리 중 중간 결과 자동 저장",
        )
        
        # 오류 파일 포함 체크박스
        include_error_files = ft.Checkbox(
            label="실패한 파일도 결과에 포함",
            value=True,
            tooltip="처리 실패한 파일도 결과 CSV에 포함",
        )
        
        # CSV 출력 경로
        csv_output_path = ft.TextField(
            label="CSV 저장 경로",
            hint_text="비어있으면 자동 생성됩니다",
            expand=True,
        )
        
        # 경로 선택 버튼
        browse_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="저장 경로 선택",
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "⚙️ 배치 처리 설정",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ORANGE_800
                ),
                ft.Divider(),
                ft.Row([
                    organization_selector,
                ]),
                ft.Column([
                    ft.Text("동시 처리 수: 3개", size=14, weight=ft.FontWeight.BOLD),
                    concurrent_files_slider,
                ]),
                ft.Column([
                    enable_batch_mode,
                    save_intermediate_results,
                    include_error_files,
                ]),
                ft.Row([
                    csv_output_path,
                    browse_button,
                ]),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return (
            container,
            organization_selector,
            concurrent_files_slider,
            enable_batch_mode,
            save_intermediate_results,
            include_error_files,
            csv_output_path,
            browse_button
        )
    
    @staticmethod
    def create_batch_progress_section() -> tuple:
        """배치 처리 진행률 섹션 생성"""
        
        # 전체 진행률 바
        overall_progress_bar = ft.ProgressBar(
            width=400,
            color=ft.Colors.GREEN_600,
            bgcolor=ft.Colors.GREY_300,
            visible=False,
        )
        
        # 진행률 텍스트
        progress_text = ft.Text(
            "대기 중...",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        # 현재 상태 텍스트
        current_status_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.BLUE_600,
            italic=True,
        )
        
        # 시간 정보
        timing_info = ft.Text(
            "추정 남은 시간: -",
            size=12,
            color=ft.Colors.GREY_600,
        )
        
        # 로그 컨테이너
        log_container = ft.Container(
            content=ft.Column([], scroll=ft.ScrollMode.AUTO),
            height=150,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # 취소 버튼
        cancel_button = ft.ElevatedButton(
            text="취소",
            icon=ft.Icons.CANCEL,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_100,
                color=ft.Colors.RED_800,
            )
        )
        
        # 일시정지/재개 버튼
        pause_resume_button = ft.ElevatedButton(
            text="일시정지",
            icon=ft.Icons.PAUSE,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📊 배치 처리 진행률",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PURPLE_800
                    ),
                    ft.Row([
                        cancel_button,
                        pause_resume_button,
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                progress_text,
                overall_progress_bar,
                current_status_text,
                timing_info,
                ft.Text("처리 로그:", weight=ft.FontWeight.BOLD, size=14),
                log_container,
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return (
            container,
            overall_progress_bar,
            progress_text,
            current_status_text,
            timing_info,
            log_container,
            cancel_button,
            pause_resume_button
        )
    
    @staticmethod
    def create_batch_results_section() -> tuple:
        """배치 처리 결과 섹션 생성"""
        
        # 요약 통계
        summary_stats = ft.Container(
            content=ft.Column([
                ft.Text("📊 처리 요약", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("총 파일: 0개", size=14),
                ft.Text("성공: 0개", size=14, color=ft.Colors.GREEN_600),
                ft.Text("실패: 0개", size=14, color=ft.Colors.RED_600),
                ft.Text("성공률: 0%", size=14),
                ft.Text("총 처리시간: 0초", size=14),
                ft.Text("평균 처리시간: 0초", size=14),
            ]),
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            width=250,
        )
        
        # 결과 테이블
        results_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("파일명", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("형식", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("크기(MB)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("상태", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("처리시간(초)", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=5,
            divider_thickness=1,
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=50,
            data_row_max_height=60,
        )
        
        # 테이블 컨테이너
        table_container = ft.Container(
            content=ft.Column([
                ft.Text("처리 결과 상세:", weight=ft.FontWeight.BOLD, size=14),
                results_table,
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # CSV 저장 버튼 (기존)
        save_csv_button = ft.ElevatedButton(
            text="CSV로 저장",
            icon=ft.Icons.SAVE_ALT,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        # Cross-Tabulated CSV 저장 버튼 (새로 추가)
        save_cross_csv_button = ft.ElevatedButton(
            text="Key-Value CSV",
            icon=ft.Icons.VIEW_LIST,
            disabled=True,
            tooltip="JSON 분석 결과를 key-value 형태의 CSV로 저장",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PURPLE_100,
                color=ft.Colors.PURPLE_800,
            )
        )
        
        # Excel 저장 버튼
        save_excel_button = ft.ElevatedButton(
            text="Excel로 저장",
            icon=ft.Icons.TABLE_CHART,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        # 결과 초기화 버튼
        clear_results_button = ft.ElevatedButton(
            text="결과 초기화",
            icon=ft.Icons.REFRESH,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_100,
                color=ft.Colors.GREY_800,
            )
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📄 배치 처리 결과",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_800
                    ),
                    ft.Row([
                        save_csv_button,
                        save_cross_csv_button,  # 새로운 버튼 추가
                        save_excel_button,
                        clear_results_button,
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row([
                    summary_stats,
                    table_container,
                ], spacing=20, expand=True),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            expand=True,
        )
        
        return (
            container,
            summary_stats,
            results_table,
            save_csv_button,
            save_cross_csv_button,  # 새로운 버튼 반환
            save_excel_button,
            clear_results_button
        )


class MultiFileUIComponents:
    """다중 파일 처리 UI 컴포넌트 클래스"""
    
    @staticmethod
    def create_multi_file_upload_section(
        on_files_selected: Callable,
        on_batch_analysis_click: Callable,
        on_clear_files_click: Callable
    ) -> ft.Container:
        """다중 파일 업로드 섹션 생성"""
        
        # 파일 선택기
        file_picker = ft.FilePicker(
            on_result=on_files_selected
        )
        
        # 선택된 파일 목록 컨테이너
        files_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "선택된 파일이 없습니다",
                    size=12,
                    color=ft.Colors.GREY_600
                )
            ]),
            height=150,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # 파일 선택 버튼
        select_button = ft.ElevatedButton(
            text="📁 파일 선택",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=lambda _: file_picker.pick_files(
                allowed_extensions=["pdf", "dxf"],
                allow_multiple=True
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_100,
                color=ft.Colors.BLUE_800,
            )
        )
        
        # 파일 목록 지우기 버튼
        clear_files_button = ft.ElevatedButton(
            text="🗑️ 목록 지우기",
            icon=ft.Icons.CLEAR,
            on_click=on_clear_files_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_100,
                color=ft.Colors.RED_800,
            )
        )
        
        # 배치 분석 버튼
        batch_analysis_button = ft.ElevatedButton(
            text="🚀 배치 분석",
            icon=ft.Icons.BATCH_PREDICTION,
            on_click=on_batch_analysis_click,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "📄 다중 파일 업로드",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800
                ),
                ft.Divider(),
                ft.Row([
                    select_button,
                    clear_files_button,
                    batch_analysis_button,
                ], alignment=ft.MainAxisAlignment.START),
                ft.Text("선택된 파일 목록:", size=14, weight=ft.FontWeight.BOLD),
                files_container,
                file_picker,  # overlay에 추가될 컴포넌트
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return container
    
    @staticmethod
    def create_batch_settings_section() -> tuple:
        """배치 설정 섹션 생성"""
        
        # 조직 선택
        organization_selector = ft.Dropdown(
            label="분석 스키마",
            options=[
                ft.dropdown.Option("국토교통부", "국토교통부 - 일반 건설/토목 도면"),
                ft.dropdown.Option("한국도로공사", "한국도로공사 - 고속도로 전용 도면"),
            ],
            value="국토교통부",
            width=280,
        )
        
        # 동시 처리 수 슬라이더
        concurrent_files_slider = ft.Slider(
            min=1,
            max=10,
            divisions=9,
            value=3,
            label="동시 처리 수: {value}개",
            width=280,
        )
        
        # 배치 모드 활성화
        enable_batch_mode = ft.Checkbox(
            label="Gemini 배치 모드 활성화",
            value=True,
        )
        
        # 중간 결과 저장
        save_intermediate_results = ft.Checkbox(
            label="중간 결과 저장",
            value=False,
        )
        
        # 오류 파일 포함
        include_error_files = ft.Checkbox(
            label="오류 파일도 CSV에 포함",
            value=True,
        )
        
        # CSV 출력 경로
        csv_output_path = ft.TextField(
            label="CSV 저장 경로 (선택사항)",
            hint_text="비워두면 자동 생성",
            width=200,
        )
        
        # 경로 선택 버튼
        browse_button = ft.ElevatedButton(
            text="📁",
            tooltip="경로 선택",
            width=50,
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "⚙️ 배치 설정",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PURPLE_800
                ),
                ft.Divider(),
                organization_selector,
                ft.Row([
                    ft.Text("동시 처리 수:", size=14),
                    ft.Column([
                        ft.Text("동시 처리 수: 3개", size=12, color=ft.Colors.GREY_600),
                        concurrent_files_slider,
                    ], spacing=0),
                ]),
                enable_batch_mode,
                save_intermediate_results,
                include_error_files,
                ft.Row([
                    csv_output_path,
                    browse_button,
                ], alignment=ft.MainAxisAlignment.START),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return (
            container,
            organization_selector,
            concurrent_files_slider,
            enable_batch_mode,
            save_intermediate_results,
            include_error_files,
            csv_output_path,
            browse_button
        )
    
    @staticmethod
    def create_batch_progress_section() -> tuple:
        """배치 진행률 섹션 생성"""
        
        # 전체 진행률 바
        overall_progress_bar = ft.ProgressBar(
            width=280,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.GREY_300,
            value=0,
        )
        
        # 진행률 텍스트
        progress_text = ft.Text(
            "0 / 0 파일 처리됨",
            size=14,
            weight=ft.FontWeight.BOLD,
        )
        
        # 현재 상태 텍스트
        current_status_text = ft.Text(
            "대기 중...",
            size=12,
            color=ft.Colors.GREY_600,
        )
        
        # 시간 정보
        timing_info = ft.Text(
            "소요 시간: 00:00:00",
            size=12,
            color=ft.Colors.GREY_600,
        )
        
        # 로그 컨테이너
        log_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "처리 시작 전...",
                    size=12,
                    color=ft.Colors.GREY_600
                )
            ], scroll=ft.ScrollMode.AUTO),
            height=100,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # 취소 버튼
        cancel_button = ft.ElevatedButton(
            text="취소",
            icon=ft.Icons.CANCEL,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_100,
                color=ft.Colors.RED_800,
            )
        )
        
        # 일시정지/재개 버튼
        pause_resume_button = ft.ElevatedButton(
            text="일시정지",
            icon=ft.Icons.PAUSE,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "📊 진행 상황",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ORANGE_800
                ),
                ft.Divider(),
                progress_text,
                overall_progress_bar,
                current_status_text,
                timing_info,
                ft.Text("처리 로그:", size=14, weight=ft.FontWeight.BOLD),
                log_container,
                ft.Row([
                    cancel_button,
                    pause_resume_button,
                ], alignment=ft.MainAxisAlignment.START),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return (
            container,
            overall_progress_bar,
            progress_text,
            current_status_text,
            timing_info,
            log_container,
            cancel_button,
            pause_resume_button
        )
    
    @staticmethod
    def create_batch_results_section() -> tuple:
        """배치 결과 섹션 생성"""
        
        # 요약 통계
        summary_stats = ft.Container(
            content=ft.Column([
                ft.Text("처리 요약", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("처리된 파일: 0개", size=12),
                ft.Text("성공: 0개", size=12, color=ft.Colors.GREEN_600),
                ft.Text("실패: 0개", size=12, color=ft.Colors.RED_600),
                ft.Text("성공률: 0%", size=12, color=ft.Colors.BLUE_600),
            ]),
            width=200,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # 결과 테이블
        results_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("파일명", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("타입", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("상태", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("처리 시간", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("결과", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(2, ft.Colors.GREY_300),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        )
        
        # 테이블 컨테이너
        table_container = ft.Container(
            content=ft.Column([
                ft.Text("처리 결과 상세:", weight=ft.FontWeight.BOLD, size=14),
                results_table,
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        # CSV 저장 버튼 (기존)
        save_csv_button = ft.ElevatedButton(
            text="CSV로 저장",
            icon=ft.Icons.SAVE_ALT,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_800,
            )
        )
        
        # Cross-Tabulated CSV 저장 버튼 (새로 추가)
        save_cross_csv_button = ft.ElevatedButton(
            text="Key-Value CSV",
            icon=ft.Icons.VIEW_LIST,
            disabled=True,
            tooltip="JSON 분석 결과를 key-value 형태의 CSV로 저장",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PURPLE_100,
                color=ft.Colors.PURPLE_800,
            )
        )
        
        # Excel 저장 버튼
        save_excel_button = ft.ElevatedButton(
            text="Excel로 저장",
            icon=ft.Icons.TABLE_CHART,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_800,
            )
        )
        
        # 결과 초기화 버튼
        clear_results_button = ft.ElevatedButton(
            text="결과 초기화",
            icon=ft.Icons.REFRESH,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_100,
                color=ft.Colors.GREY_800,
            )
        )
        
        container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "📄 배치 처리 결과",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_800
                    ),
                    ft.Row([
                        save_csv_button,
                        save_cross_csv_button,  # 새로운 버튼 추가
                        save_excel_button,
                        clear_results_button,
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row([
                    summary_stats,
                    table_container,
                ], spacing=20, expand=True),
            ]),
            padding=20,
            margin=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            expand=True,
        )
        
        return (
            container,
            summary_stats,
            results_table,
            save_csv_button,
            save_cross_csv_button,  # 새로운 버튼 반환
            save_excel_button,
            clear_results_button
        )
    
    @staticmethod
    def update_selected_files_list(files_container, selected_files, clear_button, batch_button):
        """선택된 파일 목록 업데이트"""
        if not selected_files:
            files_container.content = ft.Column([
                ft.Text(
                    "선택된 파일이 없습니다",
                    size=12,
                    color=ft.Colors.GREY_600
                )
            ])
            clear_button.disabled = True
            batch_button.disabled = True
        else:
            file_items = []
            for i, file in enumerate(selected_files):
                file_items.append(
                    ft.Row([
                        ft.Text(f"{i+1}.", size=12, width=30),
                        ft.Text(
                            file.name,
                            size=12,
                            expand=True,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            f"({file.path.split('.')[-1].upper()})",
                            size=10,
                            color=ft.Colors.GREY_600,
                            width=50,
                        ),
                    ])
                )
            
            files_container.content = ft.Column(
                file_items,
                scroll=ft.ScrollMode.AUTO,
                spacing=2,
            )
            clear_button.disabled = False
            batch_button.disabled = False
    
    @staticmethod
    def add_log_message(log_container, message, level="info"):
        """로그 메시지 추가"""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if level == "error":
            color = ft.Colors.RED_600
            icon = "❌"
        elif level == "warning":
            color = ft.Colors.ORANGE_600
            icon = "⚠️"
        elif level == "success":
            color = ft.Colors.GREEN_600
            icon = "✅"
        else:
            color = ft.Colors.BLUE_600
            icon = "ℹ️"
        
        log_text = ft.Text(
            f"{icon} {timestamp} - {message}",
            size=11,
            color=color,
        )
        
        if log_container.content:
            log_container.content.controls.append(log_text)
        else:
            log_container.content = ft.Column([log_text])
        
        # 로그가 너무 많으면 오래된 것부터 제거
        if len(log_container.content.controls) > 20:
            log_container.content.controls = log_container.content.controls[-20:]
    
    @staticmethod
    def update_batch_progress(progress_bar, progress_text, status_text, timing_info, 
                            current, total, status, elapsed_time, estimated_remaining):
        """배치 처리 진행률 업데이트"""
        progress_value = current / total if total > 0 else 0
        progress_bar.value = progress_value
        
        progress_text.value = f"{current} / {total} 파일 처리됨"
        status_text.value = status
        
        elapsed_str = f"{int(elapsed_time // 3600):02d}:{int((elapsed_time % 3600) // 60):02d}:{int(elapsed_time % 60):02d}"
        remaining_str = f"{int(estimated_remaining // 3600):02d}:{int((estimated_remaining % 3600) // 60):02d}:{int(estimated_remaining % 60):02d}"
        
        timing_info.value = f"소요 시간: {elapsed_str} | 예상 남은 시간: {remaining_str}"
    
    @staticmethod
    def update_batch_results(summary_stats, results_table, results, save_csv_button, 
                           save_cross_csv_button, save_excel_button, clear_results_button):
        """배치 결과 업데이트"""
        if not results:
            summary_stats.content.controls[1].value = "처리된 파일: 0개"
            summary_stats.content.controls[2].value = "성공: 0개"
            summary_stats.content.controls[3].value = "실패: 0개"
            summary_stats.content.controls[4].value = "성공률: 0%"
            
            results_table.rows = []
            
            save_csv_button.disabled = True
            save_cross_csv_button.disabled = True
            save_excel_button.disabled = True
            clear_results_button.disabled = True
            return
        
        # 요약 통계 업데이트
        total_files = len(results)
        success_count = sum(1 for r in results if r.success)
        failed_count = total_files - success_count
        success_rate = (success_count / total_files * 100) if total_files > 0 else 0
        
        summary_stats.content.controls[1].value = f"처리된 파일: {total_files}개"
        summary_stats.content.controls[2].value = f"성공: {success_count}개"
        summary_stats.content.controls[3].value = f"실패: {failed_count}개"
        summary_stats.content.controls[4].value = f"성공률: {success_rate:.1f}%"
        
        # 결과 테이블 업데이트
        table_rows = []
        for result in results:
            status_text = "성공" if result.success else "실패"
            status_color = ft.Colors.GREEN_600 if result.success else ft.Colors.RED_600
            
            # 결과 요약 (처음 50자까지)
            result_summary = ""
            if hasattr(result, 'analysis_result') and result.analysis_result:
                result_summary = str(result.analysis_result)[:50] + "..."
            elif hasattr(result, 'error_message') and result.error_message:
                result_summary = str(result.error_message)[:50] + "..."
            
            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(result.file_name, size=12)),
                        ft.DataCell(ft.Text(result.file_type.upper(), size=12)),
                        ft.DataCell(ft.Text(status_text, size=12, color=status_color)),
                        ft.DataCell(ft.Text(f"{result.processing_time:.2f}s", size=12)),
                        ft.DataCell(ft.Text(result_summary, size=10, overflow=ft.TextOverflow.ELLIPSIS)),
                    ]
                )
            )
        
        results_table.rows = table_rows
        
        # 버튼 활성화
        save_csv_button.disabled = False
        save_cross_csv_button.disabled = False
        save_excel_button.disabled = False
        clear_results_button.disabled = False
