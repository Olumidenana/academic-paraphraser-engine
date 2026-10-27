"""
burstiness_analyzer.py - AI Detection & Human Cadence Diagnostics
Measures sentence burstiness, perplexity proxies, and banned AI cliché patterns.
"""

import re
import math
from typing import List, Dict, Any

class BurstinessAnalyzer:
    """
    Evaluates text for the hallmarks of artificial generation:
    1. Uniform sentence length (low burstiness)
    2. Over-reliance on synthetic AI transition vocabulary
    3. Monotonous structural patterns
    """

    # Academic & AI-tell buzzwords heavily flagged by Turnitin / GPTZero
    AI_BUZZWORDS = [
        "delve", "delves", "delving",
        "tapestry", "rich tapestry",
        "pivotal", "pivotal role",
        "testament", "stands as a testament",
        "multifaceted", "multifaceted nature",
        "furthermore", "moreover", "notably",
        "paramount", "of paramount importance",
        "beacon", "beacon of hope",
        "underscores", "underscoring",
        "foster", "fostering",
        "interplay", "complex interplay",
        "in conclusion", "it is worth noting",
        "it is important to remember", "it should be noted",
        "crucial", "vital", "imperative",
        "landscape", "evolving landscape", "technological landscape",
        "embark", "embark on a journey",
        "seamlessly", "holistic", "holistic approach",
    ]

    def split_sentences(self, text: str) -> List[str]:
        """
        Splits text into sentences, protecting common abbreviations.
        """
        # Protect abbreviations like e.g., i.e., et al., Dr., etc.
        clean = re.sub(r'\b(e\.g\.|i\.e\.|et al\.|Dr\.|Prof\.|vs\.|Fig\.|Vol\.)', lambda m: m.group(0).replace('.', '§'), text)
        sentences = re.split(r'(?<=[.!?])\s+', clean)
        # Restore dots
        return [s.replace('§', '.').strip() for s in sentences if s.strip()]

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the text and returns a comprehensive Turnitin / AI vulnerability report.
        """
        if not text.strip():
            return {
                "word_count": 0,
                "sentence_count": 0,
                "burstiness_stdev": 0.0,
                "mean_sentence_length": 0.0,
                "ai_buzzword_count": 0,
                "flagged_buzzwords": [],
                "authenticity_score": 100,
                "risk_level": "Safe",
                "verdict": "Empty text"
            }

        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)
        sentences = self.split_sentences(text)
        total_sentences = len(sentences)

        if total_sentences == 0 or total_words == 0:
            return {"word_count": total_words, "sentence_count": 0, "authenticity_score": 100}

        # Sentence lengths (word count per sentence)
        lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        mean_len = sum(lengths) / total_sentences

        # Standard deviation of sentence length (Burstiness)
        if total_sentences > 1:
            variance = sum((l - mean_len) ** 2 for l in lengths) / (total_sentences - 1)
            stdev = math.sqrt(variance)
        else:
            stdev = 0.0

        # Detect AI buzzwords
        lower_text = text.lower()
        found_buzzwords = []
        for bw in self.AI_BUZZWORDS:
            occurrences = len(re.findall(r'\b' + re.escape(bw) + r'\b', lower_text))
            if occurrences > 0:
                found_buzzwords.append({"word": bw, "count": occurrences})

        total_buzzwords = sum(item["count"] for item in found_buzzwords)

        # Authenticity Scoring Calculation (0-100)
        # 1. Burstiness penalty/bonus: Humans have stdev > 7.0, AI often sits between 2.0 - 4.5
        burstiness_score = min(100, max(10, (stdev / 8.0) * 85))
        
        # 2. Buzzword penalty: each AI buzzword heavily docks points
        buzzword_penalty = min(50, total_buzzwords * 12)

        authenticity_score = max(5, int(burstiness_score - buzzword_penalty))

        # Risk level determination
        if authenticity_score >= 75 and total_buzzwords <= 1 and stdev >= 6.0:
            risk_level = "Low (Turnitin-Safe / Human Rhythm)"
        elif authenticity_score >= 50:
            risk_level = "Moderate (Mild Uniformity / Edit Advised)"
        else:
            risk_level = "High (AI Signature Detected / Low Burstiness)"

        return {
            "word_count": total_words,
            "sentence_count": total_sentences,
            "mean_sentence_length": round(mean_len, 1),
            "burstiness_stdev": round(stdev, 2),
            "shortest_sentence": min(lengths) if lengths else 0,
            "longest_sentence": max(lengths) if lengths else 0,
            "ai_buzzword_count": total_buzzwords,
            "flagged_buzzwords": found_buzzwords,
            "authenticity_score": authenticity_score,
            "risk_level": risk_level,
            "sentence_lengths": lengths
        }
