import sys
import os
import time
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QLineEdit, QPushButton, QFileDialog, 
                            QProgressBar, QTextEdit, QGroupBox, QFormLayout, QMessageBox,
                            QSpinBox, QCheckBox, QTabWidget, QSplitter, QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSettings
from PyQt5.QtGui import QFont, QIcon

from ebook_parser import EbookParser
from translator import EbookTranslator
from language import LanguageResources

class TranslationWorker(QThread):
    """번역 작업을 별도 스레드에서 실행하는 워커 클래스"""
    progress_updated = pyqtSignal(int, int)  # 현재, 전체
    status_updated = pyqtSignal(str)
    translation_done = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    sample_updated = pyqtSignal(str, str)  # 원문, 번역문
    
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
            # 이북 파싱
            self.status_updated.emit(LanguageResources.get(self.ui_lang, "parsing_file"))
            parser = EbookParser()
            chapters = parser.parse_ebook(self.file_path)
            self.status_updated.emit(f"{len(chapters)} {LanguageResources.get(self.ui_lang, 'chunks_parsed')}.")
            
            # 번역기 초기화
            kwargs = {"model_name": self.model_name, "target_language": self.target_lang}
            if self.server_url:
                kwargs["base_url"] = self.server_url
                
            translator = EbookTranslator(**kwargs)
            
            # 번역 시작
            self.status_updated.emit(f"{self.model_name} {LanguageResources.get(self.ui_lang, 'translating_with')}")
            translated_chapters = {}
            
            for i, (chapter_id, content) in enumerate(chapters):
                if self.stop_requested:
                    self.status_updated.emit(LanguageResources.get(self.ui_lang, "translation_stopped"))
                    return
                
                # 진행상황 업데이트
                self.progress_updated.emit(i + 1, len(chapters))
                self.status_updated.emit(f"{LanguageResources.get(self.ui_lang, 'translating_chunk')} {i+1}/{len(chapters)}...")
                
                # 번역
                translated_text = translator.translate_text(content)
                translated_chapters[chapter_id] = translated_text
                
                # 첫 번째 청크는 샘플로 표시
                if i == 0:
                    self.sample_updated.emit(content[:500] + "...", translated_text[:500] + "...")
            
            # 번역 완료
            self.status_updated.emit(LanguageResources.get(self.ui_lang, "translation_completed"))
            self.translation_done.emit(translated_chapters)
            
        except Exception as e:
            self.error_occurred.emit(f"{LanguageResources.get(self.ui_lang, 'error_occurred')}: {str(e)}")
            
    def stop(self):
        self.stop_requested = True
        self.status_updated.emit(LanguageResources.get(self.ui_lang, "stop_requested"))


class EbookTranslatorApp(QMainWindow):
    """PyQt 기반 이북 번역기 애플리케이션"""
    
    def __init__(self):
        super().__init__()
        # 애플리케이션 설정 로드
        self.settings = QSettings("LocalLLM", "EbookTranslator")
        self.ui_language = self.settings.value("language", "ko")  # 기본 언어는 한국어
        
        self.init_ui()
        self.translation_worker = None
        self.translated_result = None
        
        # 언어 설정이 변경되면 UI 업데이트
        self.update_ui_language(self.ui_language)
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(LanguageResources.get(self.ui_language, "app_title"))
        self.setGeometry(100, 100, 1000, 700)
        
        # 메뉴바 생성
        self.create_menu_bar()
        
        # 메인 위젯과 레이아웃
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 상단 설정 영역
        self.settings_group = QGroupBox(LanguageResources.get(self.ui_language, "translation_settings"))
        settings_layout = QVBoxLayout()
        
        # 서버 및 모델 설정
        server_model_layout = QHBoxLayout()
        
        # Ollama 서버 설정
        self.server_group = QGroupBox(LanguageResources.get(self.ui_language, "server_settings"))
        server_form = QFormLayout()
        self.server_url = QLineEdit("http://localhost:11434")
        server_form.addRow(LanguageResources.get(self.ui_language, "server_address"), self.server_url)
        self.server_group.setLayout(server_form)
        server_model_layout.addWidget(self.server_group)
        
        # 모델 설정
        self.model_group = QGroupBox(LanguageResources.get(self.ui_language, "model_settings"))
        model_form = QFormLayout()
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gemma3:12b-it-qat", "llama3", "mistral", "mixtral", "phi3"])
        model_form.addRow(LanguageResources.get(self.ui_language, "model_selection"), self.model_combo)
        self.model_group.setLayout(model_form)
        server_model_layout.addWidget(self.model_group)
        
        settings_layout.addLayout(server_model_layout)
        
        # 언어 설정
        lang_layout = QHBoxLayout()
        
        # 소스 언어
        self.source_group = QGroupBox(LanguageResources.get(self.ui_language, "source_language"))
        source_form = QFormLayout()
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems(["영어", "한국어", "일본어", "중국어", "프랑스어", "독일어", "스페인어"])
        self.source_lang_combo.setCurrentText("영어")
        source_form.addRow(LanguageResources.get(self.ui_language, "source_lang_selection"), self.source_lang_combo)
        self.source_group.setLayout(source_form)
        lang_layout.addWidget(self.source_group)
        
        # 타겟 언어
        self.target_group = QGroupBox(LanguageResources.get(self.ui_language, "target_language"))
        target_form = QFormLayout()
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(["한국어", "영어", "일본어", "중국어", "프랑스어", "독일어", "스페인어"])
        target_form.addRow(LanguageResources.get(self.ui_language, "target_lang_selection"), self.target_lang_combo)
        self.target_group.setLayout(target_form)
        lang_layout.addWidget(self.target_group)
        
        settings_layout.addLayout(lang_layout)
        
        # 파일 설정
        file_layout = QHBoxLayout()
        
        # 입력 파일
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
        
        # 출력 파일
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
        
        # 컨트롤 버튼 영역
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
        
        # 프로그레스 바
        progress_layout = QVBoxLayout()
        self.progress_label = QLabel(LanguageResources.get(self.ui_language, "waiting"))
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(progress_layout)
        
        # 탭 위젯 (번역 샘플 및 로그)
        self.tab_widget = QTabWidget()
        
        # 번역 샘플 탭
        sample_widget = QWidget()
        sample_layout = QHBoxLayout(sample_widget)
        
        # 원문 예시
        self.source_sample = QTextEdit()
        self.source_sample.setReadOnly(True)
        self.source_sample.setPlaceholderText(LanguageResources.get(self.ui_language, "source_placeholder"))
        sample_layout.addWidget(self.source_sample)
        
        # 번역문 예시
        self.target_sample = QTextEdit()
        self.target_sample.setReadOnly(True)
        self.target_sample.setPlaceholderText(LanguageResources.get(self.ui_language, "target_placeholder"))
        sample_layout.addWidget(self.target_sample)
        
        self.tab_widget.addTab(sample_widget, LanguageResources.get(self.ui_language, "translation_sample"))
        
        # 로그 탭
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        self.tab_widget.addTab(log_widget, LanguageResources.get(self.ui_language, "log_tab"))
        
        main_layout.addWidget(self.tab_widget)
        
        # 상태 표시줄
        self.statusBar().showMessage(LanguageResources.get(self.ui_language, "waiting"))
        
        # 초기 로그 메시지
        self.log(LanguageResources.get(self.ui_language, "app_started"))
        self.log(LanguageResources.get(self.ui_language, "ollama_required"))
        self.log(LanguageResources.get(self.ui_language, "download_model"))
        
    def browse_input_file(self):
        """입력 파일 선택 다이얼로그"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            LanguageResources.get(self.ui_language, "input_file_selection"), 
            "", 
            LanguageResources.get(self.ui_language, "ebook_files")
        )
        if file_path:
            self.input_file_path.setText(file_path)
            # 기본 출력 파일명 생성
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_dir = os.path.dirname(file_path)
            self.output_file_path.setText(os.path.join(output_dir, f"{base_name}_translated.txt"))
            self.log(f"{LanguageResources.get(self.ui_language, 'file_selected')}: {file_path}")
            
    def browse_output_file(self):
        """출력 파일 선택 다이얼로그"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            LanguageResources.get(self.ui_language, "output_file_selection"), 
            "", 
            LanguageResources.get(self.ui_language, "text_files")
        )
        if file_path:
            self.output_file_path.setText(file_path)
            self.log(f"{LanguageResources.get(self.ui_language, 'output_selected')}: {file_path}")
            
    def start_translation(self):
        """번역 시작"""
        # 입력 검증
        if not self.input_file_path.text():
            QMessageBox.warning(self, LanguageResources.get(self.ui_language, "warning"), 
                              LanguageResources.get(self.ui_language, "select_file"))
            return
            
        if not self.output_file_path.text():
            QMessageBox.warning(self, LanguageResources.get(self.ui_language, "warning"), 
                              LanguageResources.get(self.ui_language, "specify_output"))
            return
            
        # UI 업데이트
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText(LanguageResources.get(self.ui_language, "loading"))
        
        # 로그 초기화
        self.log(LanguageResources.get(self.ui_language, "translation_started"))
        
        # 번역 작업 스레드 생성 및 시작
        self.translation_worker = TranslationWorker(
            self.input_file_path.text(),
            self.model_combo.currentText(),
            self.source_lang_combo.currentText(),
            self.target_lang_combo.currentText(),
            self.server_url.text() if self.server_url.text() else None,
            self.ui_language
        )
        
        # 시그널 연결
        self.translation_worker.progress_updated.connect(self.update_progress)
        self.translation_worker.status_updated.connect(self.update_status)
        self.translation_worker.translation_done.connect(self.handle_translation_done)
        self.translation_worker.error_occurred.connect(self.handle_error)
        self.translation_worker.sample_updated.connect(self.update_sample)
        
        # 작업 시작
        self.translation_worker.start()
        
    def stop_translation(self):
        """번역 중지"""
        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.stop()
            self.log(LanguageResources.get(self.ui_language, "stop_requested"))
            self.stop_btn.setEnabled(False)
            
    def save_translation(self):
        """번역 결과 저장"""
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
        """진행 상황 업데이트"""
        progress_percent = int((current / total) * 100)
        self.progress_bar.setValue(progress_percent)
        self.progress_label.setText(f"{LanguageResources.get(self.ui_language, 'translation_progress')} {current}/{total} ({progress_percent}%)")
        
    @pyqtSlot(str)
    def update_status(self, status):
        """상태 메시지 업데이트"""
        self.statusBar().showMessage(status)
        self.log(status)
        
    @pyqtSlot(dict)
    def handle_translation_done(self, translated_chapters):
        """번역 완료 처리"""
        self.translated_result = translated_chapters
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.log(LanguageResources.get(self.ui_language, "translation_completed"))
        
    @pyqtSlot(str)
    def handle_error(self, error_msg):
        """오류 처리"""
        self.log(f"{LanguageResources.get(self.ui_language, 'error')}: {error_msg}")
        self.statusBar().showMessage(f"{LanguageResources.get(self.ui_language, 'error_occurred')}: {error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, LanguageResources.get(self.ui_language, "error"), error_msg)
        
    @pyqtSlot(str, str)
    def update_sample(self, source, target):
        """번역 샘플 업데이트"""
        self.source_sample.setText(source)
        self.target_sample.setText(target)
        
    def create_menu_bar(self):
        """메뉴바 생성"""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu(LanguageResources.get(self.ui_language, "file_menu"))
        
        # 설정 메뉴
        settings_menu = menubar.addMenu(LanguageResources.get(self.ui_language, "settings_menu"))
        
        # 언어 메뉴
        language_menu = settings_menu.addMenu(LanguageResources.get(self.ui_language, "language_menu"))
        
        # 한국어 액션
        korean_action = QAction(LanguageResources.get(self.ui_language, "korean"), self)
        korean_action.setCheckable(True)
        korean_action.setChecked(self.ui_language == "ko")
        korean_action.triggered.connect(lambda: self.change_language("ko"))
        language_menu.addAction(korean_action)
        
        # 영어 액션
        english_action = QAction(LanguageResources.get(self.ui_language, "english"), self)
        english_action.setCheckable(True)
        english_action.setChecked(self.ui_language == "en")
        english_action.triggered.connect(lambda: self.change_language("en"))
        language_menu.addAction(english_action)
        
        # 도움말 메뉴
        help_menu = menubar.addMenu(LanguageResources.get(self.ui_language, "help_menu"))
    
    def change_language(self, lang_code):
        """UI 언어 변경"""
        if lang_code != self.ui_language:
            self.ui_language = lang_code
            self.settings.setValue("language", lang_code)
            self.update_ui_language(lang_code)
    
    def update_ui_language(self, lang_code):
        """UI 언어 업데이트"""
        # 윈도우 타이틀 및 메뉴바 업데이트
        self.setWindowTitle(LanguageResources.get(lang_code, "app_title"))
        
        # 메뉴바 재생성
        self.menuBar().clear()
        self.create_menu_bar()
        
        # 그룹박스 타이틀 업데이트
        self.settings_group.setTitle(LanguageResources.get(lang_code, "translation_settings"))
        self.server_group.setTitle(LanguageResources.get(lang_code, "server_settings"))
        self.model_group.setTitle(LanguageResources.get(lang_code, "model_settings"))
        self.source_group.setTitle(LanguageResources.get(lang_code, "source_language"))
        self.target_group.setTitle(LanguageResources.get(lang_code, "target_language"))
        self.input_group.setTitle(LanguageResources.get(lang_code, "input_file"))
        self.output_group.setTitle(LanguageResources.get(lang_code, "output_file"))
        
        # 버튼 텍스트 업데이트
        self.browse_btn.setText(LanguageResources.get(lang_code, "browse"))
        self.output_browse_btn.setText(LanguageResources.get(lang_code, "browse"))
        self.start_btn.setText(LanguageResources.get(lang_code, "start_translation"))
        self.stop_btn.setText(LanguageResources.get(lang_code, "stop_translation"))
        self.save_btn.setText(LanguageResources.get(lang_code, "save_translation"))
        
        # 탭 이름 업데이트
        self.tab_widget.setTabText(0, LanguageResources.get(lang_code, "translation_sample"))
        self.tab_widget.setTabText(1, LanguageResources.get(lang_code, "log_tab"))
        
        # 프로그레스 라벨 업데이트
        self.progress_label.setText(LanguageResources.get(lang_code, "waiting"))
        
        # 플레이스홀더 텍스트 업데이트
        self.source_sample.setPlaceholderText(LanguageResources.get(lang_code, "source_placeholder"))
        self.target_sample.setPlaceholderText(LanguageResources.get(lang_code, "target_placeholder"))
        
        # 상태바 업데이트
        self.statusBar().showMessage(LanguageResources.get(lang_code, "waiting"))
        
        # 로그 메시지 추가
        self.log(f"{LanguageResources.get(lang_code, 'language_menu')}: {LanguageResources.get_language_names()[lang_code]}")
        
    def log(self, message):
        """로그 메시지 추가"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
    def closeEvent(self, event):
        """앱 종료 시 처리"""
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
                self.translation_worker.wait(2000)  # 최대 2초 대기
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
