"""
Async Ebook Translator v2 - 최적화된 고성능 번역 엔진
- 커넥션 풀 재활용
- 단일 이벤트 루프
- as_completed()로 빠른 결과 수집
"""

import asyncio
import httpx
import os
from typing import List, Tuple, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import threading


@dataclass
class TranslationConfig:
    """번역 설정"""
    model_name: str = "gemma3:4b-it-qat"
    target_language: str = "한국어"
    source_language: Optional[str] = None
    base_url: str = "http://localhost:11434"
    max_concurrent: int = 5  # 동시 요청 수
    timeout: float = 120.0  # 요청 타임아웃 (초)
    max_retries: int = 3  # 재시도 횟수
    connection_pool_size: int = 10  # 커넥션 풀 크기


class AsyncEbookTranslator:
    """비동기 병렬 처리 기반 Ebook 번역기 (최적화 버전)"""
    
    def __init__(self, config: Optional[TranslationConfig] = None):
        self.config = config or TranslationConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self.last_parsed_file: Optional[str] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """커넥션 풀을 재활용하는 HTTP 클라이언트 (싱글톤)"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=httpx.Timeout(self.config.timeout),
                limits=httpx.Limits(
                    max_connections=self.config.connection_pool_size,
                    max_keepalive_connections=self.config.connection_pool_size
                ),
                http2=True  # HTTP/2 멀티플렉싱 활성화
            )
        return self._client
    
    async def close(self):
        """클라이언트 정리"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    def _build_prompt(self, text: str) -> str:
        """번역 프롬프트 생성"""
        source_lang = f"from {self.config.source_language} " if self.config.source_language else ""
        return f"""You are a professional translator. Translate the following text {source_lang}to {self.config.target_language}.
Keep the meaning while making it natural in {self.config.target_language}. Output ONLY the translation, nothing else.

Text:
{text}

Translation:"""

    async def translate_text(self, text: str) -> str:
        """단일 텍스트 번역 (비동기)"""
        if not text.strip():
            return ""
        
        prompt = self._build_prompt(text)
        client = await self._get_client()
        
        for attempt in range(self.config.max_retries):
            try:
                response = await client.post(
                    "/api/generate",
                    json={
                        "model": self.config.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": 2048,  # 최대 토큰 수 제한
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "").strip()
                    
            except httpx.TimeoutException:
                if attempt == self.config.max_retries - 1:
                    raise RuntimeError(f"번역 타임아웃 ({self.config.timeout}초 초과)")
                await asyncio.sleep(0.5 * (attempt + 1))
                
            except httpx.HTTPStatusError as e:
                if attempt == self.config.max_retries - 1:
                    raise RuntimeError(f"HTTP 오류: {e.response.status_code}")
                await asyncio.sleep(0.5 * (attempt + 1))
                
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise RuntimeError(f"번역 실패: {e}")
                await asyncio.sleep(0.5 * (attempt + 1))
        
        return ""

    async def _translate_chunk_with_index(
        self,
        index: int,
        chunk_id: str,
        content: str,
        semaphore: asyncio.Semaphore,
        cancel_event: asyncio.Event
    ) -> Tuple[int, str, str]:
        """인덱스 포함 청크 번역 (결과 정렬용)"""
        if cancel_event.is_set():
            return index, chunk_id, ""
        
        async with semaphore:
            if cancel_event.is_set():
                return index, chunk_id, ""
            
            translated = await self.translate_text(content)
            return index, chunk_id, translated

    async def translate_chapters(
        self,
        chapters: List[Tuple[str, str]],
        progress_callback: Optional[Callable[[int, int, str, str], Any]] = None,
        cancel_event: Optional[asyncio.Event] = None
    ) -> Dict[str, str]:
        """
        챕터 목록 병렬 번역 (최적화 버전)
        - as_completed()로 먼저 끝난 것부터 처리
        """
        if cancel_event is None:
            cancel_event = asyncio.Event()
        
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        translated_chapters: Dict[str, str] = {}
        total = len(chapters)
        completed = 0
        
        # 모든 번역 태스크 생성
        tasks = [
            asyncio.create_task(
                self._translate_chunk_with_index(i, chapter_id, content, semaphore, cancel_event)
            )
            for i, (chapter_id, content) in enumerate(chapters)
        ]
        
        # as_completed()로 먼저 끝난 것부터 처리 (더 빠른 진행률 업데이트)
        try:
            for coro in asyncio.as_completed(tasks):
                if cancel_event.is_set():
                    # 남은 태스크 취소
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    break
                
                try:
                    index, chunk_id, translated = await coro
                    translated_chapters[chunk_id] = translated
                    completed += 1
                    
                    if progress_callback:
                        original = chapters[index][1][:100] if index < len(chapters) else ""
                        progress_callback(completed, total, original, translated[:100])
                        
                except asyncio.CancelledError:
                    continue
                except Exception as e:
                    print(f"번역 오류: {e}")
                    completed += 1
                    
        finally:
            # 클라이언트 정리
            await self.close()
        
        return translated_chapters

    def save_translation(self, translated_chapters: Dict[str, str], output_path: str):
        """번역 결과 저장"""
        _, ext = os.path.splitext(output_path)
        
        if ext.lower() == '.epub':
            self._save_as_epub(translated_chapters, output_path)
        else:
            self._save_as_text(translated_chapters, output_path)

    def _save_as_text(self, translated_chapters: Dict[str, str], output_path: str):
        """텍스트 파일로 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for chapter_id, translated_text in translated_chapters.items():
                f.write(f"--- Chapter ID: {chapter_id} ---\n\n")
                f.write(translated_text)
                f.write("\n\n")
        
        print(f"번역 결과 저장 완료: {output_path}")

    def _save_as_epub(self, translated_chapters: Dict[str, str], output_path: str):
        """EPUB 파일로 저장 (원본 구조 유지)"""
        if not self.last_parsed_file or not os.path.exists(self.last_parsed_file):
            text_path = output_path.replace('.epub', '.txt')
            self._save_as_text(translated_chapters, text_path)
            return
        
        book = epub.read_epub(self.last_parsed_file)
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if item.get_id() in translated_chapters:
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'html.parser')
                    body = soup.body
                    
                    if body:
                        translated_text = translated_chapters[item.get_id()]
                        paragraphs = translated_text.split('\n\n')
                        body.clear()
                        
                        for para in paragraphs:
                            if para.strip():
                                p = soup.new_tag('p')
                                p.string = para.strip()
                                body.append(p)
                        
                        item.set_content(str(soup).encode('utf-8'))
        
        epub.write_epub(output_path, book)
        print(f"번역된 EPUB 저장 완료: {output_path}")


class SyncTranslatorWrapper:
    """기존 GUI와 호환을 위한 동기 래퍼 (최적화 버전)"""
    
    def __init__(
        self,
        model_name: str = "gemma3:4b-it-qat",
        target_language: str = "한국어",
        source_language: Optional[str] = None,
        base_url: Optional[str] = None,
        max_concurrent: int = 5
    ):
        self.config = TranslationConfig(
            model_name=model_name,
            target_language=target_language,
            source_language=source_language,
            base_url=base_url or "http://localhost:11434",
            max_concurrent=max_concurrent
        )
        self._translator = AsyncEbookTranslator(self.config)
        self._cancel_event: Optional[asyncio.Event] = None
        # 단일 이벤트 루프를 별도 스레드에서 유지
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None
        self._start_event_loop()
    
    def _start_event_loop(self):
        """별도 스레드에서 이벤트 루프 시작 (재사용)"""
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()
        
        self._loop_thread = threading.Thread(target=run_loop, daemon=True)
        self._loop_thread.start()
        
        # 루프가 시작될 때까지 대기
        import time
        while self._loop is None:
            time.sleep(0.01)
    
    def _run_async(self, coro):
        """비동기 코루틴을 동기적으로 실행 (기존 루프 재활용)"""
        if self._loop is None:
            self._start_event_loop()
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()
    
    @property
    def last_parsed_file(self) -> Optional[str]:
        return self._translator.last_parsed_file
    
    @last_parsed_file.setter
    def last_parsed_file(self, value: str):
        self._translator.last_parsed_file = value
    
    def translate_text(self, text: str) -> str:
        """단일 텍스트 번역 (동기)"""
        return self._run_async(self._translator.translate_text(text))
    
    def translate_chapters(
        self,
        chapters: List[Tuple[str, str]],
        callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, str]:
        """챕터 목록 번역 (동기)"""
        def progress_wrapper(current: int, total: int, source: str, translated: str):
            if callback:
                callback(current, total)
        
        self._cancel_event = asyncio.Event()
        return self._run_async(
            self._translator.translate_chapters(
                chapters,
                progress_callback=progress_wrapper,
                cancel_event=self._cancel_event
            )
        )
    
    def request_cancel(self):
        """번역 취소 요청"""
        if self._cancel_event and self._loop:
            self._loop.call_soon_threadsafe(self._cancel_event.set)
    
    def save_translation(self, translated_chapters: Dict[str, str], output_path: str):
        """번역 결과 저장"""
        self._translator.save_translation(translated_chapters, output_path)
    
    def cleanup(self):
        """리소스 정리"""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._loop_thread:
            self._loop_thread.join(timeout=2.0)
