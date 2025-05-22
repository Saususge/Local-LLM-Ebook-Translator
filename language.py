"""
다국어 지원을 위한 언어 리소스 모듈
"""

class LanguageResources:
    """다국어 UI를 위한 텍스트 리소스 관리 클래스"""
    
    # 언어 리소스 딕셔너리
    resources = {
        # 한국어 리소스
        "ko": {
            # 공통
            "app_title": "로컬 LLM 이북 번역기",
            "loading": "로딩 중...",
            "waiting": "대기 중...",
            "error": "오류",
            "warning": "경고",
            "info": "정보",
            "success": "성공",
            "ok": "확인",
            "cancel": "취소",
            "apply": "적용",
            
            # 메뉴
            "file_menu": "파일",
            "edit_menu": "편집",
            "settings_menu": "설정",
            "help_menu": "도움말",
            "language_menu": "언어",
            "korean": "한국어",
            "english": "영어",
            
            # 설정
            "translation_settings": "번역 설정",
            "server_settings": "Ollama 서버",
            "server_address": "서버 주소:",
            "model_settings": "모델 설정",
            "model_selection": "모델 선택:",
            "source_language": "원본 언어",
            "source_lang_selection": "소스 언어:",
            "target_language": "번역 언어",
            "target_lang_selection": "타겟 언어:",
            
            # 파일
            "input_file": "입력 파일",
            "output_file": "출력 파일",
            "browse": "찾아보기",
            "input_file_selection": "번역할 이북 파일 선택",
            "output_file_selection": "번역 결과 저장 위치 선택",
            "ebook_files": "이북 파일 (*.epub *.pdf)",
            "text_files": "텍스트 파일 (*.txt)",
            "file_uploaded": "파일이 업로드되었습니다",
            "file_selected": "입력 파일이 선택되었습니다",
            "output_selected": "출력 파일이 선택되었습니다",
            
            # 버튼
            "start_translation": "번역 시작",
            "stop_translation": "번역 중지",
            "save_translation": "번역 결과 저장",
            "download_translation": "번역 결과 다운로드",
            
            # 번역 상태
            "parsing_file": "파일 파싱 중...",
            "chunks_parsed": "개의 텍스트 청크를 파싱했습니다",
            "translating_with": "모델을 사용하여 번역 중...",
            "translating_chunk": "청크 번역 중...",
            "translation_stopped": "번역이 중단되었습니다",
            "translation_completed": "번역이 완료되었습니다",
            "translation_started": "번역을 시작합니다...",
            "translation_progress": "진행 중...",
            "stop_requested": "번역 중지 요청...",
            "save_error": "저장 오류",
            "save_success": "번역 결과가 성공적으로 저장되었습니다",
            "saved_to": "번역 결과가 저장되었습니다",
            
            # 오류 메시지
            "select_file": "번역할 파일을 선택해주세요",
            "specify_output": "결과를 저장할 파일을 지정해주세요",
            "no_translation": "저장할 번역 결과가 없습니다",
            "save_error_msg": "번역 결과 저장 중 오류가 발생했습니다",
            "error_occurred": "오류가 발생했습니다",
            
            # 번역 샘플
            "translation_sample": "번역 샘플",
            "source_sample": "원문 예시",
            "target_sample": "번역 예시",
            "source_placeholder": "원문 예시가 여기에 표시됩니다",
            "target_placeholder": "번역 예시가 여기에 표시됩니다",
            
            # 로그
            "log_tab": "로그",
            "app_started": "이북 번역기가 시작되었습니다",
            "ollama_required": "Ollama가 로컬에서 실행 중이어야 합니다",
            "download_model": "모델이 없다면 'ollama pull [모델명]'으로 다운로드하세요",
            
            # 종료
            "exit_confirmation": "종료 확인",
            "exit_message": "번역이 진행 중입니다. 정말 종료하시겠습니까?",
            
            # 웹 인터페이스
            "web_description": "EPUB 또는 PDF 파일을 업로드하여 번역해보세요",
            "web_settings": "설정",
            "web_model_select": "Ollama 모델 선택",
            "web_target_lang": "번역할 언어",
            "web_upload": "EPUB 또는 PDF 파일 업로드",
            "web_usage": "사용 방법",
            "web_usage_steps": """
            1. 사이드바에서 Ollama 모델과 번역할 언어를 선택합니다.
            2. EPUB 또는 PDF 파일을 업로드합니다.
            3. '번역 시작' 버튼을 클릭합니다.
            4. 번역이 완료되면 결과를 다운로드할 수 있습니다.
            """,
            "web_notes": """
            **참고사항:**
            - Ollama가 로컬에 설치되어 있어야 합니다.
            - 번역에 사용할 모델이 미리 다운로드되어 있어야 합니다.
            - 대용량 파일의 경우 번역에 시간이 많이 소요될 수 있습니다.
            """
        },
        
        # 영어 리소스
        "en": {
            # 공통
            "app_title": "Local LLM Ebook Translator",
            "loading": "Loading...",
            "waiting": "Waiting...",
            "error": "Error",
            "warning": "Warning",
            "info": "Information",
            "success": "Success",
            "ok": "OK",
            "cancel": "Cancel",
            "apply": "Apply",
            
            # 메뉴
            "file_menu": "File",
            "edit_menu": "Edit",
            "settings_menu": "Settings",
            "help_menu": "Help",
            "language_menu": "Language",
            "korean": "Korean",
            "english": "English",
            
            # 설정
            "translation_settings": "Translation Settings",
            "server_settings": "Ollama Server",
            "server_address": "Server Address:",
            "model_settings": "Model Settings",
            "model_selection": "Select Model:",
            "source_language": "Source Language",
            "source_lang_selection": "Source Language:",
            "target_language": "Target Language",
            "target_lang_selection": "Target Language:",
            
            # 파일
            "input_file": "Input File",
            "output_file": "Output File",
            "browse": "Browse",
            "input_file_selection": "Select Ebook File to Translate",
            "output_file_selection": "Select Location to Save Translation",
            "ebook_files": "Ebook Files (*.epub *.pdf)",
            "text_files": "Text Files (*.txt)",
            "file_uploaded": "File has been uploaded",
            "file_selected": "Input file has been selected",
            "output_selected": "Output file has been selected",
            
            # 버튼
            "start_translation": "Start Translation",
            "stop_translation": "Stop Translation",
            "save_translation": "Save Translation",
            "download_translation": "Download Translation",
            
            # 번역 상태
            "parsing_file": "Parsing file...",
            "chunks_parsed": "text chunks parsed",
            "translating_with": "Translating with model...",
            "translating_chunk": "Translating chunk...",
            "translation_stopped": "Translation has been stopped",
            "translation_completed": "Translation completed",
            "translation_started": "Starting translation...",
            "translation_progress": "In progress...",
            "stop_requested": "Stop requested...",
            "save_error": "Save Error",
            "save_success": "Translation has been saved successfully",
            "saved_to": "Translation has been saved to",
            
            # 오류 메시지
            "select_file": "Please select a file to translate",
            "specify_output": "Please specify a file to save the results",
            "no_translation": "No translation results to save",
            "save_error_msg": "An error occurred while saving the translation",
            "error_occurred": "An error occurred",
            
            # 번역 샘플
            "translation_sample": "Translation Sample",
            "source_sample": "Source Sample",
            "target_sample": "Translation Sample",
            "source_placeholder": "Source text will be displayed here",
            "target_placeholder": "Translation will be displayed here",
            
            # 로그
            "log_tab": "Log",
            "app_started": "Ebook Translator has started",
            "ollama_required": "Ollama must be running locally",
            "download_model": "If you don't have the model, download it with 'ollama pull [model_name]'",
            
            # 종료
            "exit_confirmation": "Confirm Exit",
            "exit_message": "Translation is in progress. Are you sure you want to exit?",
            
            # 웹 인터페이스
            "web_description": "Upload an EPUB or PDF file to translate it",
            "web_settings": "Settings",
            "web_model_select": "Select Ollama Model",
            "web_target_lang": "Target Language",
            "web_upload": "Upload EPUB or PDF File",
            "web_usage": "How to Use",
            "web_usage_steps": """
            1. Select Ollama model and target language in the sidebar.
            2. Upload an EPUB or PDF file.
            3. Click the 'Start Translation' button.
            4. Once translation is complete, you can download the results.
            """,
            "web_notes": """
            **Notes:**
            - Ollama must be installed locally.
            - The translation model must be downloaded in advance.
            - Large files may take a long time to translate.
            """
        }
    }
    
    @classmethod
    def get(cls, lang_code, key):
        """특정 언어의 리소스 키에 해당하는 텍스트 반환"""
        if lang_code not in cls.resources:
            lang_code = "ko"  # 기본 언어는 한국어
        
        if key not in cls.resources[lang_code]:
            # 해당 키가 없으면 기본 언어에서 검색
            return cls.resources["ko"].get(key, key)
        
        return cls.resources[lang_code][key]
    
    @classmethod
    def get_languages(cls):
        """지원되는 언어 코드 목록 반환"""
        return list(cls.resources.keys())
    
    @classmethod
    def get_language_names(cls):
        """지원되는 언어 이름 목록 반환"""
        return {
            "ko": "한국어", 
            "en": "English"
        }
