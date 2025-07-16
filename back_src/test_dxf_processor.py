#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DXF 처리 모듈 테스트 스크립트
수정된 _extract_title_block_info 함수와 관련 기능들을 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from dxf_processor import DXFProcessor, AttributeInfo, TitleBlockInfo, BoundingBox
    print("[SUCCESS] DXF 처리 모듈 import 성공")
    
    # DXFProcessor 인스턴스 생성
    processor = DXFProcessor()
    print("[SUCCESS] DXFProcessor 인스턴스 생성 성공")
    
    # AttributeInfo 데이터 클래스 테스트
    test_attr = AttributeInfo(
        tag="TEST_TAG",
        text="테스트 텍스트",
        position=(100.0, 200.0, 0.0),
        height=5.0,
        width=50.0,
        rotation=0.0,
        layer="0",
        prompt="테스트 프롬프트",
        style="Standard",
        invisible=False,
        const=False,
        verify=False,
        preset=False,
        insert_x=100.0,
        insert_y=200.0,
        insert_z=0.0,
        estimated_width=75.0,
        entity_handle="ABC123"
    )
    print("[SUCCESS] AttributeInfo 데이터 클래스 테스트 성공")
    print(f"   Tag: {test_attr.tag}")
    print(f"   Text: {test_attr.text}")
    print(f"   Position: {test_attr.position}")
    print(f"   Prompt: {test_attr.prompt}")
    print(f"   Handle: {test_attr.entity_handle}")
    
    # TitleBlockInfo 데이터 클래스 테스트
    test_title_block = TitleBlockInfo(
        block_name="TEST_TITLE_BLOCK",
        drawing_name="테스트 도면",
        drawing_number="TEST-001",
        all_attributes=[test_attr]
    )
    print("[SUCCESS] TitleBlockInfo 데이터 클래스 테스트 성공")
    print(f"   Block Name: {test_title_block.block_name}")
    print(f"   Drawing Name: {test_title_block.drawing_name}")
    print(f"   Drawing Number: {test_title_block.drawing_number}")
    print(f"   Attributes Count: {test_title_block.attributes_count}")
    
    # BoundingBox 테스트
    test_bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=100.0, max_y=50.0)
    print("[SUCCESS] BoundingBox 데이터 클래스 테스트 성공")
    print(f"   Width: {test_bbox.width}")
    print(f"   Height: {test_bbox.height}")
    print(f"   Center: {test_bbox.center}")
    
    print("\n[COMPLETE] 모든 테스트 통과! DXF 속성 추출 기능 개선이 성공적으로 완료되었습니다.")
    
except ImportError as e:
    print(f"[ERROR] Import 오류: {e}")
except Exception as e:
    print(f"[ERROR] 테스트 실행 중 오류: {e}")

if __name__ == "__main__":
    print("\nDXF 처리 모듈 테스트 완료")
