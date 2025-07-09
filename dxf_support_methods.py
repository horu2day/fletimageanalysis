# -*- coding: utf-8 -*-
"""
DXF 파일 지원을 위한 추가 메서드들
main.py에 추가할 메서드들을 정의합니다.
"""

def handle_file_selection_update(self, e):
    """
    기존 on_file_selected 메서드를 DXF 지원으로 업데이트하는 로직
    이 메서드들을 main.py에 추가하거나 기존 메서드를 대체해야 합니다.
    """
    
    def on_file_selected_updated(self, e):
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

    def run_analysis_updated(self):
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
            result = self.dxf_processor.process_dxf_file(self.current_file_path)
            
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
    
    def display_dxf_analysis_results(self, dxf_result):
        """DXF 분석 결과 표시"""
        def update_results():
            if dxf_result and dxf_result['success']:
                # 결과 텍스트 구성
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
                        result_text += f"\n📐 도곽 위치 정보\n"
                        result_text += f"좌하단: ({bbox['min_x']:.2f}, {bbox['min_y']:.2f})\n"
                        result_text += f"우상단: ({bbox['max_x']:.2f}, {bbox['max_y']:.2f})\n"
                        result_text += f"크기: {bbox['max_x'] - bbox['min_x']:.2f} × {bbox['max_y'] - bbox['min_y']:.2f}\n"
                
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
            else:
                self.results_text.value = "❌ DXF 분석 결과가 없습니다."
                self.save_text_button.disabled = True
                self.save_json_button.disabled = True
                
            self.page.update()
        
        # 메인 스레드에서 UI 업데이트
        self.page.run_thread(update_results)
