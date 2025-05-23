from typing import List, Tuple, Dict, Optional
from langchain_ollama.chat_models import ChatOllama
from langchain_ollama import OllamaEmbeddings

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import shutil

class EbookTranslator:
    """Class for translating ebook content"""
    
    def __init__(self, model_name="gemma3:12b-it-qat", target_language="한국어", source_language=None, base_url=None):
        """
        Initialization
        Args:
            model_name: Ollama model name
            target_language: Target language for translation
            source_language: Source language (optional)
            base_url: Ollama server URL (default: http://localhost:11434)
        """
        self.target_language = target_language
        self.source_language = source_language
        
        # Initialize Ollama LLM (server URL can be configured)
        ollama_kwargs = {"model": model_name}
        if base_url:
            ollama_kwargs["base_url"] = base_url
            
        self.llm = ChatOllama(**ollama_kwargs)
        
        # Prompt template for translation
        source_lang_prompt = f"from {source_language}" if source_language else ""
        self.translate_prompt = PromptTemplate(
            input_variables=["text", "target_language", "source_language"],
            template="""You are a professional translator. Please translate the following text {source_language}to {target_language}.
            Maintain the exact meaning of the original text while translating it into natural {target_language}.
            
            Original text:
            {text}
            
            {target_language} translation:"""
        )
        
        # Set up LLM chain
        self.translate_chain = LLMChain(
            llm=self.llm,
            prompt=self.translate_prompt
        )
    
    def translate_text(self, text: str) -> str:
        """Function to translate text"""
        if not text.strip():
            return ""
        
        result = self.translate_chain.invoke({
            "text": text,
            "target_language": self.target_language,
            "source_language": f"from {self.source_language} " if self.source_language else ""
        })
        
        return result["text"].strip()
    
    def translate_chapters(self, chapters: List[Tuple[str, str]], callback=None) -> Dict[str, str]:
        """
        Translate list of chapters
        Args:
            chapters: List of chapters to translate (ID, content)
            callback: Callback function for progress updates (optional)
        """
        translated_chapters = {}
        
        total = len(chapters)
        for idx, (chapter_id, content) in enumerate(chapters):
            print(f"Translating... {idx+1}/{total}")
            if callback:
                callback(idx+1, total)
                
            translated_text = self.translate_text(content)
            translated_chapters[chapter_id] = translated_text
        
        return translated_chapters
    
    def save_translation(self, translated_chapters: Dict[str, str], output_path: str):
        """Save translation results to file"""
        _, ext = os.path.splitext(output_path)
        
        if ext.lower() == '.epub':
            self._save_as_epub(translated_chapters, output_path)
        else:
            self._save_as_text(translated_chapters, output_path)
    
    def _save_as_text(self, translated_chapters: Dict[str, str], output_path: str):
        """Save translation results to text file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for chapter_id, translated_text in translated_chapters.items():
                f.write(f"--- Chapter ID: {chapter_id} ---\n\n")
                f.write(translated_text)
                f.write("\n\n")
        
        print(f"Translation results saved to {output_path}.")
    
    def _save_as_epub(self, translated_chapters: Dict[str, str], output_path: str):
        """Save translation results to EPUB file, preserving original structure"""
        # 입력 파일 경로를 알아내기 위한 임시 변수
        input_path = None
        
        # 입력 파일을 추적하기 위해 클래스 속성을 확인
        try:
            from ebook_parser import EbookParser
            parser = EbookParser()
            input_path = parser.last_parsed_file
        except (ImportError, AttributeError):
            # 입력 파일을 알 수 없는 경우 예외 처리
            raise ValueError("원본 EPUB 파일 정보를 찾을 수 없습니다. 텍스트 파일로 저장합니다.")
        
        if not input_path or not os.path.exists(input_path):
            # 대체 방법: 번역 결과를 일반 텍스트로 저장
            self._save_as_text(translated_chapters, output_path)
            return
            
        # 원본 EPUB 파일을 읽어서 복사
        book = epub.read_epub(input_path)
        
        # 책의 내용을 번역된 내용으로 대체
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if item.get_id() in translated_chapters:
                    # HTML 콘텐츠를 읽어옴
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 본문 내용 찾기 (보통 body 태그 내용)
                    body = soup.body
                    
                    if body:
                        # 번역된 텍스트로 HTML 생성
                        translated_text = translated_chapters[item.get_id()]
                        
                        # HTML 구조 유지하면서 내용만 교체
                        # 단락 분리하여 p 태그로 변환
                        paragraphs = translated_text.split('\n\n')
                        
                        # body 내용 지우기
                        body.clear()
                        
                        # 단락 추가
                        for para in paragraphs:
                            if para.strip():
                                p = soup.new_tag('p')
                                p.string = para.strip()
                                body.append(p)
                        
                        # 수정된 HTML 다시 저장
                        item.set_content(str(soup).encode('utf-8'))
        
        # 번역된 EPUB 저장
        epub.write_epub(output_path, book)
        print(f"번역된 EPUB 파일이 저장되었습니다: {output_path}")
    
    def _save_as_epub(self, translated_chapters: Dict[str, str], output_path: str):
        """Save translation results to EPUB file, preserving original structure"""
        # 입력 파일 경로를 알아내기 위한 임시 변수
        input_path = None
        
        # 입력 파일을 추적하기 위해 클래스 속성을 확인
        try:
            from ebook_parser import EbookParser
            parser = EbookParser()
            input_path = parser.last_parsed_file
        except (ImportError, AttributeError):
            # 입력 파일을 알 수 없는 경우 예외 처리
            raise ValueError("원본 EPUB 파일 정보를 찾을 수 없습니다. 텍스트 파일로 저장합니다.")
        
        if not input_path or not os.path.exists(input_path):
            # 대체 방법: 번역 결과를 일반 텍스트로 저장
            self._save_as_text(translated_chapters, output_path)
            return
            
        # 원본 EPUB 파일을 읽어서 복사
        book = epub.read_epub(input_path)
        
        # 책의 내용을 번역된 내용으로 대체
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if item.get_id() in translated_chapters:
                    # HTML 콘텐츠를 읽어옴
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 본문 내용 찾기 (보통 body 태그 내용)
                    body = soup.body
                    
                    if body:
                        # 번역된 텍스트로 HTML 생성
                        translated_text = translated_chapters[item.get_id()]
                        
                        # HTML 구조 유지하면서 내용만 교체
                        # 단락 분리하여 p 태그로 변환
                        paragraphs = translated_text.split('\n\n')
                        
                        # body 내용 지우기
                        body.clear()
                        
                        # 단락 추가
                        for para in paragraphs:
                            if para.strip():
                                p = soup.new_tag('p')
                                p.string = para.strip()
                                body.append(p)
                        
                        # 수정된 HTML 다시 저장
                        item.set_content(str(soup).encode('utf-8'))
        
        # 번역된 EPUB 저장
        epub.write_epub(output_path, book)
        print(f"번역된 EPUB 파일이 저장되었습니다: {output_path}")
