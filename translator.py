from typing import List, Tuple, Dict, Optional
from langchain_ollama.chat_models import ChatOllama
from langchain_ollama import OllamaEmbeddings

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

class EbookTranslator:
    """Ebook 콘텐츠를 번역하는 클래스"""
    
    def __init__(self, model_name="gemma3:12b-it-qat", target_language="한국어", source_language=None, base_url=None):
        """
        초기화
        Args:
            model_name: Ollama 모델 이름
            target_language: 번역할 대상 언어
            source_language: 원본 언어 (선택 사항)
            base_url: Ollama 서버 URL (기본값: http://localhost:11434)
        """
        self.target_language = target_language
        self.source_language = source_language
        
        # Ollama LLM 초기화 (서버 URL 설정 가능)
        ollama_kwargs = {"model": model_name}
        if base_url:
            ollama_kwargs["base_url"] = base_url
            
        self.llm = Ollama(**ollama_kwargs)
        
        # 번역을 위한 프롬프트 템플릿
        source_lang_prompt = f"{source_language}에서" if source_language else ""
        self.translate_prompt = PromptTemplate(
            input_variables=["text", "target_language", "source_language"],
            template="""당신은 전문 번역가입니다. 다음 텍스트를 {source_language}{target_language}로 번역해주세요.
            원문의 의미를 정확하게 유지하면서 자연스러운 {target_language}로 번역하세요.
            
            원문:
            {text}
            
            {target_language} 번역:"""
        )
        
        # LLM 체인 설정
        self.translate_chain = LLMChain(
            llm=self.llm,
            prompt=self.translate_prompt
        )
    
    def translate_text(self, text: str) -> str:
        """텍스트 번역 함수"""
        if not text.strip():
            return ""
        
        result = self.translate_chain.invoke({
            "text": text,
            "target_language": self.target_language,
            "source_language": f"{self.source_language}에서 " if self.source_language else ""
        })
        
        return result["text"].strip()
    
    def translate_chapters(self, chapters: List[Tuple[str, str]], callback=None) -> Dict[str, str]:
        """
        챕터 목록 번역
        Args:
            chapters: 번역할 챕터 목록 (ID, 내용)
            callback: 진행 상황 업데이트를 위한 콜백 함수 (선택 사항)
        """
        translated_chapters = {}
        
        total = len(chapters)
        for idx, (chapter_id, content) in enumerate(chapters):
            print(f"번역 중... {idx+1}/{total}")
            if callback:
                callback(idx+1, total)
                
            translated_text = self.translate_text(content)
            translated_chapters[chapter_id] = translated_text
        
        return translated_chapters
    
    def save_translation(self, translated_chapters: Dict[str, str], output_path: str):
        """번역 결과를 파일로 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for chapter_id, translated_text in translated_chapters.items():
                f.write(f"--- 챕터 ID: {chapter_id} ---\n\n")
                f.write(translated_text)
                f.write("\n\n")
        
        print(f"번역 결과가 {output_path}에 저장되었습니다.")
