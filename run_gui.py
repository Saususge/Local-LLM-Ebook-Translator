#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ebook Translator GUI Execution Script
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo
from gui_app import EbookTranslatorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Apply consistent UI style
    
    # Set up system Qt translator
    translator = QTranslator()
    translator.load(QLocale.system(), "qtbase", "_", 
                   QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    
    # Run application
    translator_app = EbookTranslatorApp()
    translator_app.show()
    
    sys.exit(app.exec_())
