"""
테스트용 DXF 파일 생성 스크립트
도곽 블록과 속성을 포함한 간단한 DXF 파일 생성
"""

import ezdxf
import os

def create_test_dxf():
    """테스트용 DXF 파일 생성"""
    # 새 문서 생성
    doc = ezdxf.new('R2010')
    
    # 모델스페이스 가져오기
    msp = doc.modelspace()
    
    # 도곽 블록 생성
    title_block = doc.blocks.new(name='TITLE_BLOCK')
    
    # 블록에 기본 도형 추가 (도곽 테두리)
    title_block.add_lwpolyline([
        (0, 0), (210, 0), (210, 297), (0, 297), (0, 0)
    ], dxfattribs={'layer': 'BORDER'})
    
    # 도곽 블록에 속성 정의 추가
    title_block.add_attdef('DRAWING_NAME', (150, 20), 
                          dxfattribs={'height': 5, 'prompt': '도면명'})
    title_block.add_attdef('DRAWING_NUMBER', (150, 15), 
                          dxfattribs={'height': 3, 'prompt': '도면번호'})
    title_block.add_attdef('SCALE', (150, 10), 
                          dxfattribs={'height': 3, 'prompt': '축척'})
    title_block.add_attdef('DESIGNER', (150, 5), 
                          dxfattribs={'height': 3, 'prompt': '설계자'})
    title_block.add_attdef('DATE', (200, 5), 
                          dxfattribs={'height': 3, 'prompt': '날짜'})
    
    # 블록에 일반 텍스트도 추가
    title_block.add_text('도면 제목', dxfattribs={'height': 4, 'insert': (10, 280)})
    title_block.add_text('프로젝트명', dxfattribs={'height': 3, 'insert': (10, 275)})
    
    # 모델스페이스에 도곽 블록 참조 추가
    blockref = msp.add_blockref('TITLE_BLOCK', (0, 0))
    
    # 블록 참조에 속성 값 추가
    blockref.add_auto_attribs({
        'DRAWING_NAME': '평면도 및 종단면도',
        'DRAWING_NUMBER': 'DWG-001',
        'SCALE': '1:1000',
        'DESIGNER': '김설계',
        'DATE': '2025-07-09'
    })
    
    # 추가 블록 생성 (일반 블록)
    detail_block = doc.blocks.new(name='DETAIL_MARK')
    detail_block.add_circle((0, 0), 5)
    detail_block.add_attdef('DETAIL_NO', (0, 0), 
                           dxfattribs={'height': 3, 'prompt': '상세번호'})
    
    # 상세 마크 블록 참조 추가
    detail_ref = msp.add_blockref('DETAIL_MARK', (50, 50))
    detail_ref.add_auto_attribs({'DETAIL_NO': 'A'})
    
    detail_ref2 = msp.add_blockref('DETAIL_MARK', (100, 100))
    detail_ref2.add_auto_attribs({'DETAIL_NO': 'B'})
    
    # 독립적인 텍스트 엔티티 추가
    msp.add_text('독립 텍스트 1', dxfattribs={'height': 5, 'insert': (30, 150)})
    msp.add_mtext('여러줄\n텍스트', dxfattribs={'char_height': 4, 'insert': (30, 130)})
    
    return doc

def main():
    """메인 함수"""
    try:
        # 테스트 DXF 파일 생성
        doc = create_test_dxf()
        
        # uploads 폴더 생성
        os.makedirs('uploads', exist_ok=True)
        
        # 파일 저장
        output_path = 'uploads/test_drawing.dxf'
        doc.saveas(output_path)
        
        print(f"[SUCCESS] 테스트 DXF 파일 생성 완료: {output_path}")
        print("   - TITLE_BLOCK: 도곽 블록 (5개 속성)")
        print("   - DETAIL_MARK: 상세 마크 블록 (2개 인스턴스)")
        print("   - 독립 텍스트 엔티티 2개")
        
    except Exception as e:
        print(f"[ERROR] DXF 파일 생성 실패: {e}")

if __name__ == "__main__":
    main()
