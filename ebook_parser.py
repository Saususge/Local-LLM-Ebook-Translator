import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import pdfplumber
import nltk
from typing import List, Tuple

# Download NLTK data (needed for first run)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def extract_text_from_html(html_content):
    """Extract text from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def split_text_into_chunks(text, max_chunk_size=1000):
    """Split text into manageable chunks for processing"""
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
    """Class for parsing ebook files"""
    
    def __init__(self):
        pass
    
    def parse_epub(self, file_path) -> List[Tuple[str, str]]:
        """Parse EPUB file"""
        book = epub.read_epub(file_path)
        chapters = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode('utf-8')
                text = extract_text_from_html(content)
                if text.strip():  # Ignore empty content
                    text_chunks = split_text_into_chunks(text)
                    for chunk in text_chunks:
                        # Store chapter ID and content
                        chapters.append((item.get_id(), chunk))
        
        return chapters
    
    def parse_pdf(self, file_path) -> List[Tuple[int, str]]:
        """Parse PDF file"""
        chapters = []
        
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_chunks = split_text_into_chunks(text)
                    for chunk in text_chunks:
                        # Store page number and content
                        chapters.append((i + 1, chunk))
        
        return chapters
    
    def parse_ebook(self, file_path) -> List[Tuple[str, str]]:
        """Select appropriate parser based on ebook file format"""
        ext = os.path.splitext(file_path)[1].lower()
        
        # 마지막으로 파싱한 파일 경로 저장
        self.last_parsed_file = file_path
            
        if ext == '.epub':
            return self.parse_epub(file_path)
        elif ext == '.pdf':
            return self.parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
