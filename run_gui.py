#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ebook 번역기 GUI 실행 스크립트
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo
from gui_app import EbookTranslatorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 일관된 UI 스타일 적용
    
    # 시스템 Qt 번역기 설정
    translator = QTranslator()
    translator.load(QLocale.system(), "qtbase", "_", 
                   QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    
    # 애플리케이션 실행
    translator_app = EbookTranslatorApp()
    translator_app.show()
    
    sys.exit(app.exec_())
