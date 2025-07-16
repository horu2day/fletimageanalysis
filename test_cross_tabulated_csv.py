"""
Cross-Tabulated CSV 내보내기 기능 테스트 스크립트

Author: Claude Assistant
Created: 2025-07-15
Version: 1.0.0
"""

import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import json

# 프로젝트 모듈 임포트
from cross_tabulated_csv_exporter import CrossTabulatedCSVExporter, generate_cross_tabulated_csv_filename


@dataclass
class MockFileProcessingResult:
    """테스트용 파일 처리 결과 모의 객체"""
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    
    # PDF 분석 결과
    pdf_analysis_result: Optional[str] = None
    
    # DXF 분석 결과
    dxf_title_blocks: Optional[List[Dict]] = None
    dxf_total_attributes: Optional[int] = None
    dxf_total_text_entities: Optional[int] = None
    
    # 공통 메타데이터
    processed_at: Optional[str] = None


def create_test_pdf_result() -> MockFileProcessingResult:
    """테스트용 PDF 분석 결과 생성"""
    
    # 복잡한 중첩 구조의 JSON 분석 결과 시뮬레이션
    analysis_result = {
        "도면_정보": {
            "제목": "황단면도",
            "도면번호": "A-001",
            "축척": "1:1000",
            "위치": "533, 48"  # 좌표 정보 포함
        },
        "건설_정보": {
            "건설단계": "실시설계",
            "건설분야": "토목",
            "사업명": "봉담~송산 고속도로",
            "좌표": "372, 802"  # 좌표 정보 포함
        },
        "도면_속성": [
            {"속성명": "작성자", "값": "김상균", "위치": "150, 200"},
            {"속성명": "작성일", "값": "2016.10", "위치": "250, 200"},
            {"속성명": "승인", "값": "실시설계 승인신청", "위치": "350, 200"}
        ],
        "메타데이터": {
            "분석_시간": datetime.now().isoformat(),
            "신뢰도": 0.95,
            "처리_상태": "완료"
        }
    }
    
    return MockFileProcessingResult(
        file_path="/test/황단면도.pdf",
        file_name="황단면도.pdf",
        file_type="PDF",
        file_size=2048000,  # 2MB
        processing_time=5.2,
        success=True,
        pdf_analysis_result=json.dumps(analysis_result, ensure_ascii=False),
        processed_at=datetime.now().isoformat()
    )


def create_test_dxf_result() -> MockFileProcessingResult:
    """테스트용 DXF 분석 결과 생성"""
    
    title_blocks = [
        {
            'block_name': 'TITLE_BLOCK',
            'block_position': '0.00, 0.00',
            'attributes_count': 5,
            'attributes': [
                {
                    'tag': 'DWG_TITLE',
                    'text': '평면도',
                    'prompt': '도면제목',
                    'insert_x': 100.5,
                    'insert_y': 50.25
                },
                {
                    'tag': 'DWG_NO',
                    'text': 'B-002',
                    'prompt': '도면번호',
                    'insert_x': 200.75,
                    'insert_y': 50.25
                },
                {
                    'tag': 'SCALE',
                    'text': '1:500',
                    'prompt': '축척',
                    'insert_x': 300.0,
                    'insert_y': 50.25
                },
                {
                    'tag': 'DESIGNER',
                    'text': '이동훈',
                    'prompt': '설계자',
                    'insert_x': 400.25,
                    'insert_y': 50.25
                },
                {
                    'tag': 'DATE',
                    'text': '2025.07.15',
                    'prompt': '작성일',
                    'insert_x': 500.5,
                    'insert_y': 50.25
                }
            ]
        }
    ]
    
    return MockFileProcessingResult(
        file_path="/test/평면도.dxf",
        file_name="평면도.dxf",
        file_type="DXF",
        file_size=1536000,  # 1.5MB
        processing_time=3.8,
        success=True,
        dxf_title_blocks=title_blocks,
        dxf_total_attributes=5,
        dxf_total_text_entities=25,
        processed_at=datetime.now().isoformat()
    )


def create_test_failed_result() -> MockFileProcessingResult:
    """테스트용 실패 결과 생성"""
    
    return MockFileProcessingResult(
        file_path="/test/손상된파일.pdf",
        file_name="손상된파일.pdf",
        file_type="PDF",
        file_size=512000,  # 0.5MB
        processing_time=1.0,
        success=False,
        error_message="파일이 손상되어 분석할 수 없습니다",
        processed_at=datetime.now().isoformat()
    )


def test_cross_tabulated_csv_export():
    """Cross-tabulated CSV 내보내기 기능 테스트"""
    
    print("Cross-Tabulated CSV 내보내기 기능 테스트 시작")
    print("=" * 60)
    
    # 테스트 데이터 생성
    test_results = [
        create_test_pdf_result(),
        create_test_dxf_result(),
        create_test_failed_result()  # 실패 케이스도 포함
    ]
    
    print(f"테스트 데이터: {len(test_results)}개 파일")
    for i, result in enumerate(test_results, 1):
        status = "성공" if result.success else "실패"
        print(f"  {i}. {result.file_name} ({result.file_type}) - {status}")
    
    # 출력 디렉토리 생성
    output_dir = os.path.join(os.getcwd(), "test_results")
    os.makedirs(output_dir, exist_ok=True)
    
    # CrossTabulatedCSVExporter 인스턴스 생성
    exporter = CrossTabulatedCSVExporter()
    
    # 테스트 1: 기본 내보내기 (좌표 포함)
    print("\n테스트 1: 기본 내보내기 (좌표 포함)")
    output_file_1 = os.path.join(output_dir, generate_cross_tabulated_csv_filename("test_basic"))
    
    success_1 = exporter.export_cross_tabulated_csv(
        test_results,
        output_file_1,
        include_coordinates=True,
        coordinate_source="auto"
    )
    
    if success_1:
        print(f"성공: {output_file_1}")
        print(f"파일 크기: {os.path.getsize(output_file_1)} bytes")
    else:
        print("실패")
    
    # 테스트 2: 좌표 제외 내보내기
    print("\n테스트 2: 좌표 제외 내보내기")
    output_file_2 = os.path.join(output_dir, generate_cross_tabulated_csv_filename("test_no_coords"))
    
    success_2 = exporter.export_cross_tabulated_csv(
        test_results,
        output_file_2,
        include_coordinates=False,
        coordinate_source="none"
    )
    
    if success_2:
        print(f"성공: {output_file_2}")
        print(f"파일 크기: {os.path.getsize(output_file_2)} bytes")
    else:
        print("실패")
    
    # 테스트 3: 성공한 파일만 내보내기
    print("\n테스트 3: 성공한 파일만 내보내기")
    success_only_results = [r for r in test_results if r.success]
    output_file_3 = os.path.join(output_dir, generate_cross_tabulated_csv_filename("test_success_only"))
    
    success_3 = exporter.export_cross_tabulated_csv(
        success_only_results,
        output_file_3,
        include_coordinates=True,
        coordinate_source="auto"
    )
    
    if success_3:
        print(f"성공: {output_file_3}")
        print(f"파일 크기: {os.path.getsize(output_file_3)} bytes")
    else:
        print("실패")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약:")
    test_results_summary = [
        ("기본 내보내기 (좌표 포함)", success_1),
        ("좌표 제외 내보내기", success_2),
        ("성공한 파일만 내보내기", success_3)
    ]
    
    for test_name, success in test_results_summary:
        status = "통과" if success else "실패"
        print(f"  - {test_name}: {status}")
    
    total_success = sum(1 for _, success in test_results_summary if success)
    print(f"\n전체 테스트 결과: {total_success}/{len(test_results_summary)} 통과")
    
    if total_success == len(test_results_summary):
        print("모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("일부 테스트가 실패했습니다. 로그를 확인해주세요.")
    
    # 생성된 파일 목록 표시
    print(f"\n생성된 테스트 파일들 ({output_dir}):")
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"  - {file} ({file_size} bytes)")
    
    print("\n생성된 CSV 파일을 열어서 key-value 형태로 데이터가 올바르게 저장되었는지 확인해보세요.")
    

if __name__ == "__main__":
    test_cross_tabulated_csv_export()
