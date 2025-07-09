#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 임포트 테스트
DXF 지원 통합 후 모든 모듈이 정상적으로 임포트되는지 확인
"""

import sys
import os

# 현재 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """모든 주요 모듈 임포트 테스트"""
    try:
        print("🔍 모듈 임포트 테스트 시작...")
        
        # 기본 라이브러리
        import flet as ft
        print("✅ Flet 임포트 성공")
        
        # 프로젝트 모듈들
        from config import Config
        print("✅ Config 임포트 성공")
        
        from pdf_processor import PDFProcessor
        print("✅ PDFProcessor 임포트 성공")
        
        from dxf_processor import DXFProcessor
        print("✅ DXFProcessor 임포트 성공")
        
        from gemini_analyzer import GeminiAnalyzer
        print("✅ GeminiAnalyzer 임포트 성공")
        
        from ui_components import UIComponents
        print("✅ UIComponents 임포트 성공")
        
        from utils import AnalysisResultSaver, DateTimeUtils
        print("✅ Utils 임포트 성공")
        
        # 메인 애플리케이션
        from main import DocumentAnalyzerApp
        print("✅ DocumentAnalyzerApp 임포트 성공")
        
        print("\n🎉 모든 모듈 임포트 성공!")
        print(f"📦 Flet 버전: {ft.__version__}")
        
        # DXF 관련 라이브러리
        try:
            import ezdxf
            print(f"📐 ezdxf 버전: {ezdxf.version}")
        except ImportError:
            print("⚠️ ezdxf 라이브러리가 설치되지 않았습니다")
        
        try:
            import numpy
            print(f"🔢 numpy 버전: {numpy.__version__}")
        except ImportError:
            print("⚠️ numpy 라이브러리가 설치되지 않았습니다")
        
        return True
        
    except Exception as e:
        print(f"❌ 임포트 오류: {e}")
        return False

def test_basic_functionality():
    """기본 기능 테스트"""
    try:
        print("\n🔧 기본 기능 테스트 시작...")
        
        # Config 테스트
        config_errors = Config.validate_config()
        if config_errors:
            print(f"⚠️ 설정 오류: {config_errors}")
        else:
            print("✅ Config 검증 성공")
        
        # PDF Processor 테스트
        pdf_processor = PDFProcessor()
        print("✅ PDFProcessor 인스턴스 생성 성공")
        
        # DXF Processor 테스트
        dxf_processor = DXFProcessor()
        print("✅ DXFProcessor 인스턴스 생성 성공")
        
        # DateTimeUtils 테스트
        from utils import DateTimeUtils
        timestamp = DateTimeUtils.get_timestamp()
        print(f"✅ 현재 시간: {timestamp}")
        
        print("\n🎉 기본 기능 테스트 성공!")
        return True
        
    except Exception as e:
        print(f"❌ 기능 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📋 PDF/DXF 분석기 통합 테스트")
    print("=" * 60)
    
    import_success = test_imports()
    functionality_success = test_basic_functionality()
    
    print("\n" + "=" * 60)
    if import_success and functionality_success:
        print("🎉 모든 테스트 통과! 애플리케이션 준비 완료")
        print("💡 main.py를 실행하여 애플리케이션을 시작할 수 있습니다")
    else:
        print("❌ 일부 테스트 실패. 설정을 확인하세요")
    print("=" * 60)
