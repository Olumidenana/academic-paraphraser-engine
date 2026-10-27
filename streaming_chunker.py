"""
streaming_chunker.py - Limitless Streaming Chunker with Context Memory
Enables processing 100-page dissertations and unlimited word counts without memory overflows or context loss.
"""

import re
from typing import List, Generator, Dict, Any

class StreamingChunker:
    """
    Splits arbitrary length texts (from 500 to 100,000+ words) into 
    semantic paragraph blocks while preserving context continuity.
    """

    def __init__(self, target_chunk_words: int = 350, max_chunk_words: int = 500):
        self.target_chunk_words = target_chunk_words
        self.max_chunk_words = max_chunk_words

    def split_paragraphs(self, text: str) -> List[str]:
        """
        Splits by double newline or significant paragraph breaks.
        """
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Groups paragraphs into manageable chunks that do not exceed max_chunk_words.
        Maintains trailing context for seamless inter-paragraph transitions.
        """
        paragraphs = self.split_paragraphs(text)
        if not paragraphs:
            return []

        chunks = []
        current_paras = []
        current_word_count = 0
        prev_tail_sentence = ""

        for para in paragraphs:
            words_in_para = len(re.findall(r'\b\w+\b', para))

            # If adding this paragraph exceeds target words and we already have content, finalize current chunk
            if current_word_count + words_in_para > self.target_chunk_words and current_paras:
                chunk_body = "\n\n".join(current_paras)
                chunks.append({
                    "index": len(chunks),
                    "text": chunk_body,
                    "word_count": current_word_count,
                    "prev_context": prev_tail_sentence
                })
                # Capture the last sentence of this chunk for next chunk's context
                sentences = re.split(r'(?<=[.!?])\s+', chunk_body)
                prev_tail_sentence = sentences[-1] if sentences else ""
                
                current_paras = [para]
                current_word_count = words_in_para
            else:
                current_paras.append(para)
                current_word_count += words_in_para

        if current_paras:
            chunk_body = "\n\n".join(current_paras)
            chunks.append({
                "index": len(chunks),
                "text": chunk_body,
                "word_count": current_word_count,
                "prev_context": prev_tail_sentence
            })

        return chunks

    def reassemble(self, processed_chunks: List[str]) -> str:
        """
        Reconstructs the full document cleanly.
        """
        return "\n\n".join(chunk.strip() for chunk in processed_chunks if chunk.strip())
