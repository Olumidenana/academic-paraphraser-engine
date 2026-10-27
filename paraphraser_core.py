"""
paraphraser_core.py - Academic Paraphrasing Engine with AI-Bypass & Citation Protection
"""

import os
import re
import json
import asyncio
from typing import Dict, Any, Optional, List, Callable, AsyncGenerator
import httpx
from citation_vault import CitationVault
from burstiness_analyzer import BurstinessAnalyzer
from streaming_chunker import StreamingChunker

class AcademicParaphraser:
    """
    Core engine combining:
    1. Citation Anchor Protection
    2. Stylistic Rhythm Perturbation (Anti-AI Detector)
    3. Negative Word Constraints
    4. Async Parallel Streaming Chunk Orchestration
    """

    PROMPT_TEMPLATES = {
        "phd": (
            "You are a peer-reviewed academic journal editor and senior scholar. "
            "Rewrite the provided scholarly text to elevate its intellectual rigor, conceptual depth, and analytical clarity.\n"
            "MANDATORY CONSTRAINTS:\n"
            "1. IMMUTABLE CITATION ANCHORS: You will see tokens like `[[CITE_REF_0001]]`. These represent real citations. "
            "You MUST preserve every single anchor token verbatim. Never alter, remove, combine, or invent anchors.\n"
            "2. HUMAN BURSTINESS & RHYTHM: Do not use monotonous, even-length sentences. Mix short, decisive statements (5-8 words) "
            "with longer, nuanced clauses (25-35 words). Avoid predictable Subject-Verb-Object monotony.\n"
            "3. BANNED VOCABULARY (AI SIGNATURES): Under no circumstances use: 'delve', 'tapestry', 'pivotal', 'testament', "
            "'multifaceted', 'furthermore', 'moreover', 'beacon', 'underscores', 'fosters', 'interplay', 'crucial', 'in conclusion'. "
            "Instead, use measured, direct academic verbs like 'indicates', 'demonstrates', 'suggests', 'highlights', 'challenges'.\n"
            "4. EPISTEMIC HEDGING: Use natural academic qualification ('appears consistent with', 'points toward', 'warrants caution').\n"
            "5. OUTPUT ONLY the rewritten text with the anchors intact. Do not add introductory or explanatory chatter."
        ),
        "masters": (
            "You are a graduate academic editor. Paraphrase the following academic passage with rigorous analytical precision.\n"
            "RULES:\n"
            "1. CITATIONS: Retain all `[[CITE_REF_XXXX]]` anchors in their exact positions next to the relevant assertions.\n"
            "2. HUMAN CADENCE: Radically vary sentence length. Pair short punchy arguments with complex compound evaluations.\n"
            "3. FORBIDDEN WORDS: Do NOT use: 'delve', 'pivotal', 'tapestry', 'furthermore', 'moreover', 'testament', 'multifaceted'.\n"
            "4. CLARITY: Eliminate fluff. Focus on empirical claims, cause-and-effect relationships, and logical coherence.\n"
            "5. OUTPUT ONLY the rewritten academic text."
        ),
        "undergrad": (
            "You are a university academic writing tutor. Rephrase the following text to read clearly, persuasively, and naturally.\n"
            "RULES:\n"
            "1. CITATIONS: Never delete or alter `[[CITE_REF_XXXX]]` anchors.\n"
            "2. NATURAL FLOW: Avoid repetitive sentence structures. Make the argument flow naturally like a dedicated student writer.\n"
            "3. BAN AI WORDS: Avoid: 'delve', 'pivotal', 'furthermore', 'moreover', 'testament', 'in conclusion'.\n"
            "4. OUTPUT ONLY the rewritten text."
        ),
    }

    def __init__(self, api_key: Optional[str] = None):
        # Read from environment or local .env file
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            key = line.strip().split("=", 1)[1].strip()
                            break

        self.api_key = key
        self.citation_vault = CitationVault()
        self.analyzer = BurstinessAnalyzer()
        self.chunker = StreamingChunker()

    async def paraphrase_chunk_async(
        self,
        chunk_text: str,
        tone: str = "phd",
        user_api_key: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None
    ) -> str:
        """
        Asynchronously sends masked chunk to Gemini API with strict anti-AI constraints.
        """
        key = user_api_key or self.api_key
        if not key or not key.strip():
            return self._local_heuristic_paraphrase(chunk_text, tone)

        system_prompt = self.PROMPT_TEMPLATES.get(tone, self.PROMPT_TEMPLATES["phd"])
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": chunk_text}]}],
            "generationConfig": {
                "temperature": 0.72,
                "topP": 0.95
            }
        }

        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=45.0)
            should_close = True

        # Try gemini-flash-lite-latest first, then fallback to gemini-flash-latest
        models_to_try = ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-pro-latest"]
        try:
            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key.strip()}"
                try:
                    res = await client.post(url, json=payload, timeout=30.0)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            text_part = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            if text_part.strip():
                                return text_part.strip()
                except Exception:
                    continue
        finally:
            if should_close:
                await client.aclose()

        # Fallback to local heuristic only if all models fail
        return self._local_heuristic_paraphrase(chunk_text, tone)

    def _local_heuristic_paraphrase(self, text: str, tone: str) -> str:
        """
        Linguistic heuristic transformer when offline or without API key.
        """
        replacements = [
            (r'\bdelve into\b', 'examine'),
            (r'\bdelves into\b', 'examines'),
            (r'\bfurthermore\b', 'additionally'),
            (r'\bmoreover\b', 'in parallel'),
            (r'\bpivotal\b', 'central'),
            (r'\bstands as a testament to\b', 'reflects'),
            (r'\brich tapestry of\b', 'diverse spectrum of'),
            (r'\bmultifaceted\b', 'complex'),
            (r'\bparamount\b', 'essential'),
            (r'\bunderscores the importance of\b', 'demonstrates the value of'),
            (r'\bit is crucial to note that\b', 'notably,'),
            (r'\bit is important to remember that\b', 'we observe that'),
            (r'\bin conclusion\b', 'ultimately'),
            (r'\bfoster\b', 'cultivate'),
            (r'\binterplay between\b', 'relationship between'),
            (r'\bseamlessly\b', 'directly'),
            (r'\butilize\b', 'apply'),
            (r'\butilized\b', 'applied'),
            (r'\bin order to\b', 'to'),
            (r'\bdue to the fact that\b', 'because'),
        ]

        result = text
        for pat, repl in replacements:
            result = re.sub(pat, repl, result, flags=re.IGNORECASE)

        sentences = self.analyzer.split_sentences(result)
        perturbed_sentences = []
        for s in sentences:
            if ", and also " in s and len(s.split()) > 25:
                parts = s.split(", and also ", 1)
                perturbed_sentences.append(parts[0] + ".")
                perturbed_sentences.append("This also " + parts[1])
            else:
                perturbed_sentences.append(s)

        return " ".join(perturbed_sentences)

    async def process_document_stream(
        self,
        full_text: str,
        tone: str = "phd",
        user_api_key: Optional[str] = None,
        concurrency: int = 5
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Processes documents with parallel chunk execution and real-time progress streaming.
        Yields progress updates and finally the completed document.
        """
        self.citation_vault.reset()
        key = user_api_key or self.api_key
        has_key = bool(key and key.strip())
        mode = "Deep LLM Semantic Mode (Gemini)" if has_key else "Fast Local Heuristic Mode"

        # Step 1: Pre-process citations
        masked_text, matches = self.citation_vault.mask(full_text)
        total_citations = len(matches)

        # Step 2: Split into chunks
        chunks = self.chunker.create_chunks(masked_text)
        total_chunks = len(chunks)

        yield {
            "type": "start",
            "mode": mode,
            "total_chunks": total_chunks,
            "total_citations": total_citations
        }

        processed_chunks: List[Optional[str]] = [None] * total_chunks
        semaphore = asyncio.Semaphore(concurrency)
        completed_count = 0

        async with httpx.AsyncClient(timeout=45.0) as client:
            async def worker(index: int, chunk_text: str):
                nonlocal completed_count
                async with semaphore:
                    rewritten = await self.paraphrase_chunk_async(
                        chunk_text=chunk_text,
                        tone=tone,
                        user_api_key=key,
                        client=client
                    )
                    processed_chunks[index] = rewritten
                    completed_count += 1
                    return index, completed_count

            # Launch tasks
            tasks = [asyncio.create_task(worker(i, c["text"])) for i, c in enumerate(chunks)]

            for task in asyncio.as_completed(tasks):
                idx, count = await task
                yield {
                    "type": "progress",
                    "completed_chunks": count,
                    "total_chunks": total_chunks,
                    "percent": int((count / max(1, total_chunks)) * 100)
                }

        # Step 3: Reassemble document
        reassembled = self.chunker.reassemble([p for p in processed_chunks if p is not None])

        # Step 4: Restore citations safely
        final_text, restored_count, missing_count = self.citation_vault.unmask(reassembled)

        # Step 5: Diagnostics
        metrics_original = self.analyzer.analyze(full_text)
        metrics_paraphrased = self.analyzer.analyze(final_text)

        yield {
            "type": "complete",
            "mode": mode,
            "original_text": full_text,
            "paraphrased_text": final_text,
            "total_chunks_processed": total_chunks,
            "citation_stats": {
                "detected": total_citations,
                "restored": restored_count,
                "missing": missing_count,
                "integrity_rate": "100%" if missing_count == 0 else f"{int((restored_count / max(1, total_citations)) * 100)}%"
            },
            "metrics": {
                "original": metrics_original,
                "paraphrased": metrics_paraphrased,
                "burstiness_improvement": round(metrics_paraphrased["burstiness_stdev"] - metrics_original["burstiness_stdev"], 2),
                "ai_buzzwords_removed": max(0, metrics_original["ai_buzzword_count"] - metrics_paraphrased["ai_buzzword_count"])
            }
        }
