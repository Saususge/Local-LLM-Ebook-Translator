import sys
import os
import time
import threading
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QLineEdit, QPushButton, QFileDialog, 
                            QProgressBar, QTextEdit, QGroupBox, QFormLayout, QMessageBox,
                            QSpinBox, QCheckBox, QTabWidget, QSplitter, QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSettings
from PyQt5.QtGui import QFont, QIcon

from ebook_parser import EbookParser
from translator import EbookTranslator
from language import LanguageResources

try:
    import ollama
except ImportError:
    ollama = None

class TranslationWorker(QThread):
    """Worker class that executes translation tasks in a separate thread"""
    progress_updated = pyqtSignal(int, int)  # current, total
    status_updated = pyqtSignal(str)
    translation_done = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    sample_updated = pyqtSignal(str, str)  # source text, translated text
    
    def __init__(self, file_path, model_name, source_lang, target_lang, server_url=None, ui_lang="ko"):
        super().__init__()
        self.file_path = file_path
        self.model_name = model_name
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.server_url = server_url
        self.stop_requested = False
        self.ui_lang = ui_lang
        
    def run(self):
        try:
            # Parse ebook
            self.status_updated.emit(LanguageResources.get(self.ui_lang, "parsing_file"))
            parser = EbookParser()
            chapters = parser.parse_ebook(self.file_path)
            self.status_updated.emit(f"{len(chapters)} {LanguageResources.get(self.ui_lang, 'chunks_parsed')}.")
            
            # Initialize translator
            kwargs = {"model_name": self.model_name, "target_language": self.target_lang}
            if self.server_url:
                kwargs["base_url"] = self.server_url
                
            translator = EbookTranslator(**kwargs)
            
            # Start translation
            self.status_updated.emit(f"{self.model_name} {LanguageResources.get(self.ui_lang, 'translating_with')}")
            translated_chapters = {}
            
            for i, (chapter_id, content) in enumerate(chapters):
                if self.stop_requested:
                    self.status_updated.emit(LanguageResources.get(self.ui_lang, "translation_stopped"))
                    return
                
                # Update progress
                self.progress_updated.emit(i + 1, len(chapters))
                self.status_updated.emit(f"{LanguageResources.get(self.ui_lang, 'translating_chunk')} {i+1}/{len(chapters)}...")
                
                # Translate
                translated_text = translator.translate_text(content)
                translated_chapters[chapter_id] = translated_text
                
                # Display first chunk as sample
                if i == 0:
                    self.sample_updated.emit(content[:500] + "...", translated_text[:500] + "...")
            
            # Translation completed
            self.status_updated.emit(LanguageResources.get(self.ui_lang, "translation_completed"))
            self.translation_done.emit(translated_chapters)
            
        except Exception as e:
            self.error_occurred.emit(f"{LanguageResources.get(self.ui_lang, 'error_occurred')}: {str(e)}")
            
    def stop(self):
        self.stop_requested = True
        self.status_updated.emit(LanguageResources.get(self.ui_lang, "stop_requested"))


class EbookTranslatorApp(QMainWindow):
    """PyQt-based Ebook Translator Application"""
    
    def __init__(self):
        super().__init__()
        # Load application settings
        self.settings = QSettings("LocalLLM", "EbookTranslator")
        self.ui_language = self.settings.value("language", "ko")  # Default language is Korean
        
        self.init_ui()
        self.translation_worker = None
        self.translated_result = None
        
        # Update UI when language setting changes
        self.update_ui_language(self.ui_language)
        
        # 모델 목록 불러오기
        self.load_ollama_models()
    
    def get_ollama_models(self, server_url="http://localhost:11434"):
        """Ollama 서버에서 사용 가능한 모델 목록 가져오기"""
        try:
            if ollama:
                # ollama 라이브러리 사용
                try:
                    # 서버 URL 설정
                    client = ollama.Client(host=server_url)
                    models = client.list()
                    return [model['name'] for model in models['models']]
                except Exception as e:
                    self.log(f"Ollama API 오류: {str(e)}")
                    return []
            else:
                # 직접 REST API 호출
                response = requests.get(f"{server_url}/api/tags")
                if response.status_code == 200:
                    models = response.json()
                    return [model['name'] for model in models['models']]
                else:
                    self.log(f"Ollama 서버 응답 오류: {response.status_code}")
                    return []
        except Exception as e:
            self.log(f"Ollama 모델 목록 가져오기 실패: {str(e)}")
            return []
    
    def load_ollama_models(self):
        """Ollama 모델 목록을 콤보박스에 로드"""
        # 기본 모델 목록
        default_models = ["gemma3:12b-it-qat", "llama3", "mistral", "mixtral", "phi3"]
        
        # 현재 선택된 모델 저장
        current_model = self.model_combo.currentText()
        
        # 콤보박스 초기화
        self.model_combo.clear()
        
        # Ollama 서버에서 모델 목록 가져오기
        server_url = self.server_url.text() if hasattr(self, 'server_url') else "http://localhost:11434"
        models = self.get_ollama_models(server_url)
        
        # 모델이 없으면 기본 모델 사용
        if not models:
            self.log(LanguageResources.get(self.ui_language, "ollama_connection_error") 
                     if hasattr(LanguageResources, "get") else "Ollama 서버 연결 실패. 기본 모델 목록을 사용합니다.")
            models = default_models
        
        # 모델 목록 추가
        self.model_combo.addItems(models)
        
        # 이전에 선택한 모델이 있으면 다시 선택
        if current_model and current_model in models:
            self.model_combo.setCurrentText(current_model)
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle(LanguageResources.get(self.ui_language, "app_title"))
        self.setGeometry(100, 100, 1000, 700)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top settings area
        self.settings_group = QGroupBox(LanguageResources.get(self.ui_language, "translation_settings"))
        settings_layout = QVBoxLayout()
        
        # Server and model settings
        server_model_layout = QHBoxLayout()
        
        # Ollama server settings
        self.server_group = QGroupBox(LanguageResources.get(self.ui_language, "server_settings"))
        server_form = QFormLayout()
        self.server_url = QLineEdit("http://localhost:11434")
        self.server_url.editingFinished.connect(self.on_server_url_changed)
        server_form.addRow(LanguageResources.get(self.ui_language, "server_address"), self.server_url)
        self.server_group.setLayout(server_form)
        server_model_layout.addWidget(self.server_group)
        
        # Model settings
        self.model_group = QGroupBox(LanguageResources.get(self.ui_language, "model_settings"))
        model_form = QFormLayout()
        
        # 모델 선택 콤보박스와 새로고침 버튼을 위한 레이아웃
        model_select_layout = QHBoxLayout()
        
        # 모델 선택 콤보박스
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gemma3:12b-it-qat", "llama3", "mistral", "mixtral", "phi3"])
        model_select_layout.addWidget(self.model_combo)
        
        # 새로고침 버튼
        self.refresh_models_btn = QPushButton(LanguageResources.get(self.ui_language, "refresh") 
                                              if "refresh" in LanguageResources.resources.get(self.ui_language, {}) 
                                              else "새로고침")
        self.refresh_models_btn.setMaximumWidth(80)
        self.refresh_models_btn.clicked.connect(self.load_ollama_models)
        model_select_layout.addWidget(self.refresh_models_btn)
        
        model_form.addRow(LanguageResources.get(self.ui_language, "model_selection"), model_select_layout)
        self.model_group.setLayout(model_form)
        server_model_layout.addWidget(self.model_group)
        
        settings_layout.addLayout(server_model_layout)
        
        # Language settings
        lang_layout = QHBoxLayout()
        
        # Source language
        self.source_group = QGroupBox(LanguageResources.get(self.ui_language, "source_language"))
        source_form = QFormLayout()
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems(["영어", "한국어", "일본어", "중국어", "프랑스어", "독일어", "스페인어"])
        self.source_lang_combo.setCurrentText("영어")
        source_form.addRow(LanguageResources.get(self.ui_language, "source_lang_selection"), self.source_lang_combo)
        self.source_group.setLayout(source_form)
        lang_layout.addWidget(self.source_group)
        
        # Target language
        self.target_group = QGroupBox(LanguageResources.get(self.ui_language, "target_language"))
        target_form = QFormLayout()
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(["한국어", "영어", "일본어", "중국어", "프랑스어", "독일어", "스페인어"])
        target_form.addRow(LanguageResources.get(self.ui_language, "target_lang_selection"), self.target_lang_combo)
        self.target_group.setLayout(target_form)
        lang_layout.addWidget(self.target_group)
        
        settings_layout.addLayout(lang_layout)
        
        # File settings
        file_layout = QHBoxLayout()
        
        # Input file
        self.input_group = QGroupBox(LanguageResources.get(self.ui_language, "input_file"))
        input_layout = QHBoxLayout()
        self.input_file_path = QLineEdit()
        self.input_file_path.setReadOnly(True)
        input_layout.addWidget(self.input_file_path)
        
        self.browse_btn = QPushButton(LanguageResources.get(self.ui_language, "browse"))
        self.browse_btn.clicked.connect(self.browse_input_file)
        input_layout.addWidget(self.browse_btn)
        
        self.input_group.setLayout(input_layout)
        file_layout.addWidget(self.input_group)
        
        # Output file
        self.output_group = QGroupBox(LanguageResources.get(self.ui_language, "output_file"))
        output_layout = QHBoxLayout()
        self.output_file_path = QLineEdit()
        output_layout.addWidget(self.output_file_path)
        
        self.output_browse_btn = QPushButton(LanguageResources.get(self.ui_language, "browse"))
        self.output_browse_btn.clicked.connect(self.browse_output_file)
        output_layout.addWidget(self.output_browse_btn)
        
        self.output_group.setLayout(output_layout)
        file_layout.addWidget(self.output_group)
        
        settings_layout.addLayout(file_layout)
        self.settings_group.setLayout(settings_layout)
        main_layout.addWidget(self.settings_group)
        
        # Control buttons area
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton(LanguageResources.get(self.ui_language, "start_translation"))
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_btn.clicked.connect(self.start_translation)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton(LanguageResources.get(self.ui_language, "stop_translation"))
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.clicked.connect(self.stop_translation)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton(LanguageResources.get(self.ui_language, "save_translation"))
        self.save_btn.clicked.connect(self.save_translation)
        self.save_btn.setEnabled(False)
        control_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(control_layout)
        
        # Progress bar
        progress_layout = QVBoxLayout()
        self.progress_label = QLabel(LanguageResources.get(self.ui_language, "waiting"))
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(progress_layout)
        
        # Tab widget (translation sample and log)
        self.tab_widget = QTabWidget()
        
        # Translation sample tab
        sample_widget = QWidget()
        sample_layout = QHBoxLayout(sample_widget)
        
        # Source text example
        self.source_sample = QTextEdit()
        self.source_sample.setReadOnly(True)
        self.source_sample.setPlaceholderText(LanguageResources.get(self.ui_language, "source_placeholder"))
        sample_layout.addWidget(self.source_sample)
        
        # Translation example
        self.target_sample = QTextEdit()
        self.target_sample.setReadOnly(True)
        self.target_sample.setPlaceholderText(LanguageResources.get(self.ui_language, "target_placeholder"))
        sample_layout.addWidget(self.target_sample)
        
        self.tab_widget.addTab(sample_widget, LanguageResources.get(self.ui_language, "translation_sample"))
        
        # Log tab
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        self.tab_widget.addTab(log_widget, LanguageResources.get(self.ui_language, "log_tab"))
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage(LanguageResources.get(self.ui_language, "waiting"))
        
        # Initial log messages
        self.log(LanguageResources.get(self.ui_language, "app_started"))
        self.log(LanguageResources.get(self.ui_language, "ollama_required"))
        self.log(LanguageResources.get(self.ui_language, "download_model"))
        
    def browse_input_file(self):
        """Input file selection dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            LanguageResources.get(self.ui_language, "input_file_selection"), 
            "", 
            LanguageResources.get(self.ui_language, "ebook_files")
        )
        if file_path:
            self.input_file_path.setText(file_path)
            # Generate default output filename with same extension as input
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            ext = os.path.splitext(file_path)[1].lower()
            output_dir = os.path.dirname(file_path)
            self.output_file_path.setText(os.path.join(output_dir, f"{base_name}_translated{ext}"))
            self.log(f"{LanguageResources.get(self.ui_language, 'file_selected')}: {file_path}")
            
    def browse_output_file(self):
        """Output file selection dialog"""
        # 입력 파일의 확장자 가져오기
        input_path = self.input_file_path.text()
        ext = os.path.splitext(input_path)[1].lower() if input_path else ".epub"
        
        # 출력 파일 필터 설정
        if ext == '.epub':
            file_filter = "EPUB 파일 (*.epub)"
        elif ext == '.pdf':
            file_filter = "PDF 파일 (*.pdf);;텍스트 파일 (*.txt)"
        else:
            file_filter = LanguageResources.get(self.ui_language, "ebook_files")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            LanguageResources.get(self.ui_language, "output_file_selection"), 
            "", 
            file_filter
        )
        if file_path:
            self.output_file_path.setText(file_path)
            self.log(f"{LanguageResources.get(self.ui_language, 'output_selected')}: {file_path}")
            
    def on_server_url_changed(self):
        """서버 URL이 변경되었을 때 모델 목록 업데이트"""
        self.log(f"Ollama 서버 URL이 {self.server_url.text()}(으)로 변경되었습니다. 모델 목록을 새로고침합니다.")
        self.load_ollama_models()
            
    def start_translation(self):
        """Start translation"""
        # Input validation
        if not self.input_file_path.text():
            QMessageBox.warning(self, LanguageResources.get(self.ui_language, "warning"), 
                              LanguageResources.get(self.ui_language, "select_file"))
            return
            
        if not self.output_file_path.text():
            QMessageBox.warning(self, LanguageResources.get(self.ui_language, "warning"), 
                              LanguageResources.get(self.ui_language, "specify_output"))
            return
            
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText(LanguageResources.get(self.ui_language, "loading"))
        
        # Initialize log
        self.log(LanguageResources.get(self.ui_language, "translation_started"))
        
        # Create and start translation worker thread
        self.translation_worker = TranslationWorker(
            self.input_file_path.text(),
            self.model_combo.currentText(),
            self.source_lang_combo.currentText(),
            self.target_lang_combo.currentText(),
            self.server_url.text() if self.server_url.text() else None,
            self.ui_language
        )
        
        # Connect signals
        self.translation_worker.progress_updated.connect(self.update_progress)
        self.translation_worker.status_updated.connect(self.update_status)
        self.translation_worker.translation_done.connect(self.handle_translation_done)
        self.translation_worker.error_occurred.connect(self.handle_error)
        self.translation_worker.sample_updated.connect(self.update_sample)
        
        # Start worker
        self.translation_worker.start()
        
    def stop_translation(self):
        """Stop translation"""
        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.stop()
            self.log(LanguageResources.get(self.ui_language, "stop_requested"))
            self.stop_btn.setEnabled(False)
            
    def save_translation(self):
        """Save translation results"""
        if not self.translated_result:
            QMessageBox.warning(self, LanguageResources.get(self.ui_language, "warning"), 
                              LanguageResources.get(self.ui_language, "no_translation"))
            return
            
        output_path = self.output_file_path.text()
        try:
            translator = EbookTranslator()  # 임시 인스턴스
            translator.save_translation(self.translated_result, output_path)
            self.log(f"{LanguageResources.get(self.ui_language, 'saved_to')}: {output_path}")
            QMessageBox.information(
                self, 
                LanguageResources.get(self.ui_language, "info"), 
                f"{LanguageResources.get(self.ui_language, 'save_success')}.\n{output_path}"
            )
        except Exception as e:
            self.log(f"{LanguageResources.get(self.ui_language, 'save_error')}: {str(e)}")
            QMessageBox.critical(
                self, 
                LanguageResources.get(self.ui_language, "error"), 
                f"{LanguageResources.get(self.ui_language, 'save_error_msg')}.\n{str(e)}"
            )
            
    @pyqtSlot(int, int)
    def update_progress(self, current, total):
        """Update progress status"""
        progress_percent = int((current / total) * 100)
        self.progress_bar.setValue(progress_percent)
        self.progress_label.setText(f"{LanguageResources.get(self.ui_language, 'translation_progress')} {current}/{total} ({progress_percent}%)")
        
    @pyqtSlot(str)
    def update_status(self, status):
        """Update status message"""
        self.statusBar().showMessage(status)
        self.log(status)
        
    @pyqtSlot(dict)
    def handle_translation_done(self, translated_chapters):
        """Handle translation completion"""
        self.translated_result = translated_chapters
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.log(LanguageResources.get(self.ui_language, "translation_completed"))
        
    @pyqtSlot(str)
    def handle_error(self, error_msg):
        """Handle errors"""
        self.log(f"{LanguageResources.get(self.ui_language, 'error')}: {error_msg}")
        self.statusBar().showMessage(f"{LanguageResources.get(self.ui_language, 'error_occurred')}: {error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, LanguageResources.get(self.ui_language, "error"), error_msg)
        
    @pyqtSlot(str, str)
    def update_sample(self, source, target):
        """Update translation sample"""
        self.source_sample.setText(source)
        self.target_sample.setText(target)
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(LanguageResources.get(self.ui_language, "file_menu"))
        
        # Settings menu
        settings_menu = menubar.addMenu(LanguageResources.get(self.ui_language, "settings_menu"))
        
        # Language menu
        language_menu = settings_menu.addMenu(LanguageResources.get(self.ui_language, "language_menu"))
        
        # Korean action
        korean_action = QAction(LanguageResources.get(self.ui_language, "korean"), self)
        korean_action.setCheckable(True)
        korean_action.setChecked(self.ui_language == "ko")
        korean_action.triggered.connect(lambda: self.change_language("ko"))
        language_menu.addAction(korean_action)
        
        # English action
        english_action = QAction(LanguageResources.get(self.ui_language, "english"), self)
        english_action.setCheckable(True)
        english_action.setChecked(self.ui_language == "en")
        english_action.triggered.connect(lambda: self.change_language("en"))
        language_menu.addAction(english_action)
        
        # 출력 형식 설정 메뉴 (Output Format menu)
        format_menu = settings_menu.addMenu(LanguageResources.get(self.ui_language, "output_format_menu") 
                                            if self.ui_language in LanguageResources.resources and "output_format_menu" in LanguageResources.resources[self.ui_language] 
                                            else "출력 형식")
        
        # EPUB 원본 형식 유지 옵션
        keep_format_action = QAction("원본 포맷 유지 (EPUB → EPUB)", self)
        keep_format_action.setCheckable(True)
        keep_format_action.setChecked(True)
        format_menu.addAction(keep_format_action)
        
        # Help menu
        help_menu = menubar.addMenu(LanguageResources.get(self.ui_language, "help_menu"))
    
    def change_language(self, lang_code):
        """Change UI language"""
        if lang_code != self.ui_language:
            self.ui_language = lang_code
            self.settings.setValue("language", lang_code)
            self.update_ui_language(lang_code)
    
    def update_ui_language(self, lang_code):
        """Update UI language"""
        # Update window title and menu bar
        self.setWindowTitle(LanguageResources.get(lang_code, "app_title"))
        
        # Recreate menu bar
        self.menuBar().clear()
        self.create_menu_bar()
        
        # Update group box titles
        self.settings_group.setTitle(LanguageResources.get(lang_code, "translation_settings"))
        self.server_group.setTitle(LanguageResources.get(lang_code, "server_settings"))
        self.model_group.setTitle(LanguageResources.get(lang_code, "model_settings"))
        self.source_group.setTitle(LanguageResources.get(lang_code, "source_language"))
        self.target_group.setTitle(LanguageResources.get(lang_code, "target_language"))
        self.input_group.setTitle(LanguageResources.get(lang_code, "input_file"))
        self.output_group.setTitle(LanguageResources.get(lang_code, "output_file"))
        
        # Update button text
        self.browse_btn.setText(LanguageResources.get(lang_code, "browse"))
        self.output_browse_btn.setText(LanguageResources.get(lang_code, "browse"))
        self.start_btn.setText(LanguageResources.get(lang_code, "start_translation"))
        self.stop_btn.setText(LanguageResources.get(lang_code, "stop_translation"))
        self.save_btn.setText(LanguageResources.get(lang_code, "save_translation"))
        
        # Update tab names
        self.tab_widget.setTabText(0, LanguageResources.get(lang_code, "translation_sample"))
        self.tab_widget.setTabText(1, LanguageResources.get(lang_code, "log_tab"))
        
        # Update progress label
        self.progress_label.setText(LanguageResources.get(lang_code, "waiting"))
        
        # Update placeholder text
        self.source_sample.setPlaceholderText(LanguageResources.get(lang_code, "source_placeholder"))
        self.target_sample.setPlaceholderText(LanguageResources.get(lang_code, "target_placeholder"))
        
        # Update status bar
        self.statusBar().showMessage(LanguageResources.get(lang_code, "waiting"))
        
        # Add log message
        self.log(f"{LanguageResources.get(lang_code, 'language_menu')}: {LanguageResources.get_language_names()[lang_code]}")
        
    def log(self, message):
        """Add log message"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
    def closeEvent(self, event):
        """Handle application exit"""
        if self.translation_worker and self.translation_worker.isRunning():
            reply = QMessageBox.question(
                self, 
                LanguageResources.get(self.ui_language, "exit_confirmation"), 
                LanguageResources.get(self.ui_language, "exit_message"),
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.translation_worker.stop()
                self.translation_worker.wait(2000)  # Wait up to 2 seconds
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    translator_app = EbookTranslatorApp()
    translator_app.show()
    sys.exit(app.exec_())
