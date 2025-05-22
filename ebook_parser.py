import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import pdfplumber
import nltk
from typing import List, Tuple

# NLTK 데이터 다운로드 (첫 실행시 필요)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def extract_text_from_html(html_content):
    """HTML 콘텐츠에서 텍스트 추출"""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def split_text_into_chunks(text, max_chunk_size=1000):
    """텍스트를 처리 가능한 크기의 청크로 분할"""
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

class EbookParser:
    """Ebook 파일을 파싱하는 클래스"""
    
    def __init__(self):
        pass
    
    def parse_epub(self, file_path) -> List[Tuple[str, str]]:
        """EPUB 파일 파싱"""
        book = epub.read_epub(file_path)
        chapters = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode('utf-8')
                text = extract_text_from_html(content)
                if text.strip():  # 빈 내용 무시
                    text_chunks = split_text_into_chunks(text)
                    for chunk in text_chunks:
                        # 챕터 ID와 내용 저장
                        chapters.append((item.get_id(), chunk))
        
        return chapters
    
    def parse_pdf(self, file_path) -> List[Tuple[int, str]]:
        """PDF 파일 파싱"""
        chapters = []
        
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_chunks = split_text_into_chunks(text)
                    for chunk in text_chunks:
                        # 페이지 번호와 내용 저장
                        chapters.append((i + 1, chunk))
        
        return chapters
    
    def parse_ebook(self, file_path) -> List[Tuple[str, str]]:
        """Ebook 파일 형식에 따라 적절한 파서 선택"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.epub':
            return self.parse_epub(file_path)
        elif ext == '.pdf':
            return self.parse_pdf(file_path)
        else:
            raise ValueError(f"지원되지 않는 파일 형식입니다: {ext}")
