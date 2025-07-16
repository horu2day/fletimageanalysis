"""
Cross-Tabulated CSV 내보내기 개선 테스트 스크립트
키 통합 기능 테스트

Author: Claude Assistant  
Created: 2025-07-16
Version: 1.0.0
"""

import sys
import os
from datetime import datetime
import json

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cross_tabulated_csv_exporter import CrossTabulatedCSVExporter

class MockResult:
    """테스트용 모의 결과 객체"""
    
    def __init__(self, file_name, file_type, success=True, **kwargs):
        self.file_name = file_name
        self.file_type = file_type
        self.success = success
        
        # PDF 관련 속성
        if 'pdf_analysis_result' in kwargs:
            self.pdf_analysis_result = kwargs['pdf_analysis_result']
        
        # DXF 관련 속성
        if 'dxf_title_blocks' in kwargs:
            self.dxf_title_blocks = kwargs['dxf_title_blocks']
        
        # 오류 메시지
        if 'error_message' in kwargs:
            self.error_message = kwargs['error_message']


def test_key_integration():
    """키 통합 기능 테스트"""
    print("=== Cross-Tabulated CSV 키 통합 기능 테스트 ===\n")
    
    # 테스트용 CSV 내보내기 객체 생성
    exporter = CrossTabulatedCSVExporter()
    
    # 테스트 케이스 1: PDF 분석 결과 (키 분리 형태)
    print("테스트 케이스 1: PDF 분석 결과 (키 분리 → 통합)")
    
    pdf_analysis_result = {
        "사업명_value": "고속국도 제30호선 대산~당진 고속도로 건설공사",
        "사업명_x": "40",
        "사업명_y": "130",
        "시설_공구_value": "제2공구 : 온산~사성",
        "시설_공구_x": "41", 
        "시설_공구_y": "139",
        "건설분야_value": "토목",
        "건설분야_x": "199",
        "건설분야_y": "1069",
        "건설단계_value": "실시설계",
        "건설단계_x": "263",
        "건설단계_y": "1069",
        "계절자수_value": "1",
        "계절자수_x": "309",
        "계절자수_y": "1066",
        "작성일자_value": "2023. 03",
        "작성일자_x": "332",
        "작성일자_y": "1069"
    }
    
    mock_pdf_result = MockResult(
        "황단면도.pdf",
        "PDF",
        success=True,
        pdf_analysis_result=json.dumps(pdf_analysis_result)
    )
    
    # 테스트 케이스 2: DXF 분석 결과
    print("테스트 케이스 2: DXF 분석 결과")
    
    dxf_title_blocks = [
        {
            "block_name": "TITLE_BLOCK",
            "attributes": [
                {
                    "tag": "DWG_NO",
                    "text": "A-001",
                    "insert_x": 150,
                    "insert_y": 25
                },
                {
                    "tag": "TITLE",
                    "text": "도면제목",
                    "insert_x": 200,
                    "insert_y": 50
                },
                {
                    "tag": "SCALE",
                    "text": "1:100",
                    "insert_x": 250,
                    "insert_y": 75
                }
            ]
        }
    ]
    
    mock_dxf_result = MockResult(
        "도면001.dxf",
        "DXF",
        success=True,
        dxf_title_blocks=dxf_title_blocks
    )
    
    # 테스트 케이스 3: 실패한 결과
    mock_failed_result = MockResult(
        "오류파일.pdf",
        "PDF",
        success=False,
        error_message="분석 실패"
    )
    
    # 모든 테스트 결과를 리스트로 구성
    test_results = [mock_pdf_result, mock_dxf_result, mock_failed_result]
    
    # 출력 디렉토리 생성
    output_dir = "test_results_integrated"
    os.makedirs(output_dir, exist_ok=True)
    
    # 테스트 실행: 통합된 CSV 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"integrated_test_results_{timestamp}.csv")
    
    print(f"CSV 저장 위치: {output_path}")
    
    success = exporter.export_cross_tabulated_csv(
        test_results,
        output_path,
        include_coordinates=True,
        coordinate_source="auto"
    )
    
    if success:
        print(f"✅ 테스트 성공: 통합된 CSV 파일이 저장되었습니다.")
        print(f"📁 파일 위치: {output_path}")
        
        # 저장된 CSV 파일 내용 미리보기
        try:
            with open(output_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                print(f"\n📋 CSV 파일 미리보기 (상위 10행):")
                for i, line in enumerate(lines[:10]):
                    print(f"{i+1:2d}: {line.rstrip()}")
                
                if len(lines) > 10:
                    print(f"    ... 총 {len(lines)}행")
                    
        except Exception as e:
            print(f"⚠️ 파일 읽기 오류: {e}")
            
    else:
        print("❌ 테스트 실패: CSV 저장에 실패했습니다.")
    
    return success


def test_key_extraction():
    """키 추출 및 그룹화 기능 단위 테스트"""
    print("\n=== 키 추출 및 그룹화 단위 테스트 ===\n")
    
    exporter = CrossTabulatedCSVExporter()
    
    # 테스트 케이스: 다양한 키 형태
    test_keys = [
        "사업명_value",
        "사업명_x", 
        "사업명_y",
        "시설_공구_val",
        "시설_공구_x_coord",
        "시설_공구_y_coord",
        "건설분야_text",
        "건설분야_left",
        "건설분야_top",
        "일반키",
        "축척_content",
        "축척_x_position",
        "축척_y_position"
    ]
    
    print("🔍 키 분석 결과:")
    for key in test_keys:
        base_key = exporter._extract_base_key(key)
        key_type = exporter._determine_key_type(key)
        print(f"   {key:20s} → 기본키: '{base_key:12s}' 타입: {key_type}")
    
    print("\n✅ 키 추출 및 그룹화 단위 테스트 완료")


def test_expected_output():
    """예상 출력 형태 테스트"""
    print("\n=== 예상 출력 형태 확인 ===\n")
    
    print("📊 기대하는 CSV 출력 형태:")
    print("file_name,file_type,key,value,x,y")
    print("황단면도.pdf,PDF,사업명,고속국도 제30호선 대산~당진 고속도로 건설공사,40,130")
    print("황단면도.pdf,PDF,시설_공구,제2공구 : 온산~사성,41,139")
    print("황단면도.pdf,PDF,건설분야,토목,199,1069")
    print("황단면도.pdf,PDF,건설단계,실시설계,263,1069")
    print("도면001.dxf,DXF,DWG_NO,A-001,150,25")
    print("도면001.dxf,DXF,TITLE,도면제목,200,50")
    print("도면001.dxf,DXF,SCALE,1:100,250,75")
    
    print("\n🎯 개선사항:")
    print("- 기존: 사업명_value, 사업명_x, 사업명_y가 별도 행으로 분리")
    print("- 개선: 사업명 하나의 행에 value, x, y 정보 통합")
    

if __name__ == "__main__":
    try:
        print("Cross-Tabulated CSV 키 통합 기능 테스트 시작\n")
        
        # 1. 키 추출 및 그룹화 단위 테스트
        test_key_extraction()
        
        # 2. 예상 출력 형태 확인
        test_expected_output()
        
        # 3. 실제 통합 기능 테스트
        success = test_key_integration()
        
        print(f"\n{'='*60}")
        if success:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
            print("✨ 키 통합 기능이 정상적으로 동작합니다.")
        else:
            print("😞 테스트 중 일부가 실패했습니다.")
            print("🔧 코드를 점검해주세요.")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
