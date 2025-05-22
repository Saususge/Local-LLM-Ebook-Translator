from PyQt5.QtWidgets import (QMainWindow, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QComboBox, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QWidget, QMessageBox, QProgressBar,
                             QStatusBar, QTabWidget, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
import os
import sys
from language import LanguageResources
from ebook_parser import EbookParser
from translator import EbookTranslator

class TranslationWorker(QThread):
    """번역 작업을 위한 워커 스레드"""
    progress_updated = pyqtSignal(int, int)
    translation_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, input_file, model_name, source_lang, target_lang, server_url):
        super().__init__()
        self.input_file = input_file
        self.model_name = model_name
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.server_url = server_url
        self.is_running = True
    
    def stop(self):
        self.is_running = False
    
    def run(self):
        try:
            # Ebook 파서 초기화
            parser = EbookParser()
            
            # 파일 파싱
            chapters = parser.parse_ebook(self.input_file)
            
            if not self.is_running:
                return
            
            # 번역기 초기화
            translator = EbookTranslator(
                model_name=self.model_name,
                target_language=self.target_lang,
                source_language=self.source_lang,
                base_url=self.server_url
            )
            
            # 번역 콜백 함수
            def update_progress(current, total):
                if not self.is_running:
                    return False  # 중지 신호
                self.progress_updated.emit(current, total)
                return True  # 계속 진행
            
            # 번역 실행
            translated_chapters = translator.translate_chapters(chapters, callback=update_progress)
            
            if self.is_running:
                self.translation_complete.emit(translated_chapters)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class EbookTranslatorApp(QMainWindow):
    """이북 번역기 메인 애플리케이션 창"""
    
    def __init__(self):
        super().__init__()
        self.ui_language = "ko"  # 기본 UI 언어
        self.translated_content = None
        self.worker = None
        
        self.init_ui()
        self.setup_connections()
        self.log(LanguageResources.get(self.ui_language, "app_started"))
        self.log(LanguageResources.get(self.ui_language, "ollama_required"))
        self.log(LanguageResources.get(self.ui_language, "download_model"))
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(LanguageResources.get(self.ui_language, "app_title"))
        self.setGeometry(100, 100, 900, 700)
        
        # 메인 위젯과 레이아웃
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 서버 설정 그룹
        server_group = QGroupBox(LanguageResources.get(self.ui_language, "server_settings"))
        server_layout = QHBoxLayout()
        
        self.server_label = QLabel(LanguageResources.get(self.ui_language, "server_address"))
        self.server_input = QLineEdit("http://localhost:11434")
        
        server_layout.addWidget(self.server_label)
        server_layout.addWidget(self.server_input)
        server_group.setLayout(server_layout)
        main_layout.addWidget(server_group)
        
        # 모델 설정 그룹
        model_group = QGroupBox(LanguageResources.get(self.ui_language, "model_settings"))
        model_layout = QGridLayout()
        
        self.model_label = QLabel(LanguageResources.get(self.ui_language, "model_selection"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["llama3", "llama3:70b", "gemma:7b", "mistral", "phi3:14b"])
        
        self.src_lang_label = QLabel(LanguageResources.get(self.ui_language, "source_lang_selection"))
        self.src_lang_combo = QComboBox()
        self.src_lang_combo.addItems(["영어", "한국어", "일본어", "중국어", "프랑스어", "독일어", "스페인어"])
        
        self.tgt_lang_label = QLabel(LanguageResources.get(self.ui_language, "target_lang_selection"))
        self.tgt_lang_combo = QComboBox()
        self.tgt_lang_combo.addItems(["한국어", "영어", "일본어", "중국어", "프랑스어", "독일어", "스페인어"])
        
        model_layout.addWidget(self.model_label, 0, 0)
        model_layout.addWidget(self.model_combo, 0, 1)
        model_layout.addWidget(self.src_lang_label, 1, 0)
        model_layout.addWidget(self.src_lang_combo, 1, 1)
        model_layout.addWidget(self.tgt_lang_label, 2, 0)
        model_layout.addWidget(self.tgt_lang_combo, 2, 1)
        
        model_group.setLayout(model_layout)
        main_layout.addWidget(model_group)
        
        # 파일 선택 그룹
        file_group = QGroupBox(LanguageResources.get(self.ui_language, "input_file"))
        file_layout = QHBoxLayout()
        
        self.input_file_edit = QLineEdit()
        self.input_file_btn = QPushButton(LanguageResources.get(self.ui_language, "browse"))
        
        file_layout.addWidget(self.input_file_edit)
        file_layout.addWidget(self.input_file_btn)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # 출력 파일 그룹
        output_group = QGroupBox(LanguageResources.get(self.ui_language, "output_file"))
        output_layout = QHBoxLayout()
        
        self.output_file_edit = QLineEdit()
        self.output_file_btn = QPushButton(LanguageResources.get(self.ui_language, "browse"))
        
        output_layout.addWidget(self.output_file_edit)
        output_layout.addWidget(self.output_file_btn)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # 번역 제어 버튼
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton(LanguageResources.get(self.ui_language, "start_translation"))
        self.stop_btn = QPushButton(LanguageResources.get(self.ui_language, "stop_translation"))
        self.save_btn = QPushButton(LanguageResources.get(self.ui_language, "save_translation"))
        
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(btn_layout)
        
        # 진행 상황 표시줄
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # 탭 위젯 (로그 및 번역 샘플)
        self.tab_widget = QTabWidget()
        
        # 로그 탭
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.tab_widget.addTab(self.log_edit, LanguageResources.get(self.ui_language, "log_tab"))
        
        # 번역 샘플 탭
        translation_widget = QWidget()
        translation_layout = QVBoxLayout(translation_widget)
        
        self.source_sample_label = QLabel(LanguageResources.get(self.ui_language, "source_sample"))
        self.source_sample_edit = QTextEdit()
        self.source_sample_edit.setReadOnly(True)
        self.source_sample_edit.setPlaceholderText(LanguageResources.get(self.ui_language, "source_placeholder"))
        
        self.target_sample_label = QLabel(LanguageResources.get(self.ui_language, "target_sample"))
        self.target_sample_edit = QTextEdit()
        self.target_sample_edit.setReadOnly(True)
        self.target_sample_edit.setPlaceholderText(LanguageResources.get(self.ui_language, "target_placeholder"))
        
        translation_layout.addWidget(self.source_sample_label)
        translation_layout.addWidget(self.source_sample_edit)
        translation_layout.addWidget(self.target_sample_label)
        translation_layout.addWidget(self.target_sample_edit)
        
        self.tab_widget.addTab(translation_widget, LanguageResources.get(self.ui_language, "translation_sample"))
        
        main_layout.addWidget(self.tab_widget)
        
        # 상태 표시줄
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(LanguageResources.get(self.ui_language, "waiting"))
    
    def setup_connections(self):
        """이벤트 연결 설정"""
        self.input_file_btn.clicked.connect(self.select_input_file)
        self.output_file_btn.clicked.connect(self.select_output_file)
        self.start_btn.clicked.connect(self.start_translation)
        self.stop_btn.clicked.connect(self.stop_translation)
        self.save_btn.clicked.connect(self.save_translation)
    
    def select_input_file(self):
        """입력 파일 선택"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            LanguageResources.get(self.ui_language, "input_file_selection"),
            "",
            LanguageResources.get(self.ui_language, "ebook_files")
        )
        
        if file_path:
            self.input_file_edit.setText(file_path)
            self.log(f"{LanguageResources.get(self.ui_language, 'file_selected')}: {file_path}")
            
            # 기본 출력 파일 이름 설정
            base_name = os.path.splitext(file_path)[0]
            self.output_file_edit.setText(f"{base_name}_translated.txt")
    
    def select_output_file(self):
        """출력 파일 선택"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            LanguageResources.get(self.ui_language, "output_file_selection"),
            "",
            LanguageResources.get(self.ui_language, "text_files")
        )
        
        if file_path:
            self.output_file_edit.setText(file_path)
            self.log(f"{LanguageResources.get(self.ui_language, 'output_selected')}: {file_path}")
    
    def start_translation(self):
        """번역 시작"""
        input_file = self.input_file_edit.text()
        if not input_file:
            QMessageBox.warning(
                self,
                LanguageResources.get(self.ui_language, "warning"),
                LanguageResources.get(self.ui_language, "select_file")
            )
            return
        
        model_name = self.model_combo.currentText()
        source_lang = self.src_lang_combo.currentText()
        target_lang = self.tgt_lang_combo.currentText()
        server_url = self.server_input.text()
        
        self.log(f"{LanguageResources.get(self.ui_language, 'translation_started')}")
        self.log(f"{LanguageResources.get(self.ui_language, 'parsing_file')}")
        
        # 워커 스레드 생성
        self.worker = TranslationWorker(
            input_file, model_name, source_lang, target_lang, server_url
        )
        
        # 시그널 연결
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.translation_complete.connect(self.translation_completed)
        self.worker.error_occurred.connect(self.handle_error)
        
        # UI 업데이트
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage(LanguageResources.get(self.ui_language, "translating_with").format(model_name))
        
        # 워커 시작
        self.worker.start()
    
    def stop_translation(self):
        """번역 중지"""
        if self.worker and self.worker.isRunning():
            self.log(LanguageResources.get(self.ui_language, "stop_requested"))
            self.statusBar().showMessage(LanguageResources.get(self.ui_language, "stop_requested"))
            self.worker.stop()
            self.worker.wait()
            self.log(LanguageResources.get(self.ui_language, "translation_stopped"))
            self.statusBar().showMessage(LanguageResources.get(self.ui_language, "translation_stopped"))
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    @pyqtSlot(int, int)
    def update_progress(self, current, total):
        """번역 진행 상황 업데이트"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.statusBar().showMessage(f"{LanguageResources.get(self.ui_language, 'translating_chunk')} {current}/{total}")
    
    @pyqtSlot(dict)
    def translation_completed(self, translated_chapters):
        """번역 완료 처리"""
        self.translated_content = translated_chapters
        self.log(LanguageResources.get(self.ui_language, "translation_completed"))
        self.statusBar().showMessage(LanguageResources.get(self.ui_language, "translation_completed"))
        
        # UI 업데이트
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        
        # 샘플 업데이트
        if translated_chapters:
            chapter_id = next(iter(translated_chapters))
            original_text = ""
            for chapter in self.worker.chapters:
                if chapter[0] == chapter_id:
                    original_text = chapter[1]
                    break
            
            translated_text = translated_chapters[chapter_id]
            self.source_sample_edit.setText(original_text)
            self.target_sample_edit.setText(translated_text)
    
    @pyqtSlot(str)
    def handle_error(self, error_msg):
        """오류 처리"""
        self.log(f"{LanguageResources.get(self.ui_language, 'error')}: {error_msg}")
        self.statusBar().showMessage(f"{LanguageResources.get(self.ui_language, 'error_occurred')}: {error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, LanguageResources.get(self.ui_language, "error"), error_msg)
    
    def save_translation(self):
        """번역 결과 저장"""
        if not self.translated_content:
            QMessageBox.warning(
                self,
                LanguageResources.get(self.ui_language, "warning"),
                LanguageResources.get(self.ui_language, "no_translation")
            )
            return
        
        output_file = self.output_file_edit.text()
        if not output_file:
            QMessageBox.warning(
                self,
                LanguageResources.get(self.ui_language, "warning"),
                LanguageResources.get(self.ui_language, "specify_output")
            )
            return
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for chapter_id, translated_text in self.translated_content.items():
                    f.write(f"--- 챕터 ID: {chapter_id} ---\n\n")
                    f.write(translated_text)
                    f.write("\n\n")
            
            self.log(f"{LanguageResources.get(self.ui_language, 'saved_to')}: {output_file}")
            QMessageBox.information(
                self,
                LanguageResources.get(self.ui_language, "success"),
                LanguageResources.get(self.ui_language, "save_success")
            )
        except Exception as e:
            error_msg = f"{LanguageResources.get(self.ui_language, 'save_error_msg')}: {str(e)}"
            self.log(error_msg)
            QMessageBox.critical(
                self,
                LanguageResources.get(self.ui_language, "save_error"),
                error_msg
            )
    
    def log(self, message):
        """로그 메시지 추가"""
        self.log_edit.append(message)
    
    def closeEvent(self, event):
        """창 닫기 이벤트 핸들러"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                LanguageResources.get(self.ui_language, "exit_confirmation"),
                LanguageResources.get(self.ui_language, "exit_message"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
