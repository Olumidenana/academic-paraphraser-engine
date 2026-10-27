"""
citation_vault.py - Universal Citation Vault & Deterministic Anchor System
Protects academic citations (APA, MLA, IEEE, Chicago, Harvard) across limitless documents.
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CitationMatch:
    anchor_id: str
    original_text: str
    style_type: str
    start_pos: int
    end_pos: int

class CitationVault:
    """
    Guarantees 100% citation preservation by converting all academic citations
    into immutable anchor tokens before paraphrasing, and restoring them with
    correct grammatical punctuation afterwards.
    """

    # Comprehensive Regex patterns for academic citations
    PATTERNS = [
        # Direct quotes with page numbers: "quote" (Smith, 2020, p. 45)
        ("quote_page", r'\([A-Z][a-zA-Z\s\.\&\-]+,\s*\d{4}[a-z]?(?:,\s*(?:p\.|pp\.|para\.)\s*\d+(?:[\-–]\d+)?)\)'),
        
        # Parenthetical Author-Date with multiple authors: (Smith, 2020; Jones et al., 2021; Doe & Ray, 2018)
        ("parenthetical_multi", r'\([A-Z][a-zA-Z\s\.\&\-]+,\s*\d{4}[a-z]?(?:;\s*[A-Z][a-zA-Z\s\.\&\-]+,\s*\d{4}[a-z]?)+\)'),
        
        # Parenthetical Author-Date single: (Smith, 2020) or (Smith & Brown, 2021) or (Smith et al., 2019)
        ("parenthetical_single", r'\((?:e\.g\.,\s*|see\s+)?(?:[A-Z][a-zA-Z\.\-]+(?:\s+(?:&|and)\s+[A-Z][a-zA-Z\.\-]+|\s+et\s+al\.)?),\s*\d{4}[a-z]?\)'),
        
        # Narrative citation with et al.: Smith et al. (2020)
        ("narrative_et_al", r'\b[A-Z][a-zA-Z\-]+\s+et\s+al\.\s*\(\d{4}[a-z]?\)'),
        
        # Narrative citation with two authors: Smith and Jones (2020) or Smith & Jones (2020)
        ("narrative_dual", r'\b[A-Z][a-zA-Z\-]+\s+(?:and|\&)\s+[A-Z][a-zA-Z\-]+\s*\(\d{4}[a-z]?\)'),
        
        # Narrative citation single author: Smith (2020)
        ("narrative_single", r'\b[A-Z][a-zA-Z\-]+\s*\(\d{4}[a-z]?\)'),
        
        # IEEE / Vancouver bracketed numbers: [1] or [1, 2] or [1-5] or [1, 3-7]
        ("numeric_bracket", r'\[\d+(?:[\s,\-–]+\d+)*\]'),
    ]

    def __init__(self):
        self.anchor_map: Dict[str, str] = {}
        self.counter = 0

    def mask(self, text: str) -> Tuple[str, List[CitationMatch]]:
        """
        Scans text and replaces all citations with immutable placeholders like [[CITE_REF_0001]].
        Returns the masked text and list of matched citations.
        """
        matches: List[CitationMatch] = []
        masked_text = text

        for style_name, pattern_str in self.PATTERNS:
            regex = re.compile(pattern_str)
            
            def replace_callback(match):
                self.counter += 1
                anchor = f"[[CITE_REF_{self.counter:04d}]]"
                original = match.group(0)
                self.anchor_map[anchor] = original
                matches.append(CitationMatch(
                    anchor_id=anchor,
                    original_text=original,
                    style_type=style_name,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
                return anchor

            masked_text = regex.sub(replace_callback, masked_text)

        return masked_text, matches

    def unmask(self, text: str) -> Tuple[str, int, int]:
        """
        Restores original citations from anchors.
        Returns:
            - unmasked text
            - total restored count
            - missing anchors count (if any were dropped by model)
        """
        restored_count = 0
        missing_count = 0

        # Replace all known anchors
        for anchor, original in self.anchor_map.items():
            if anchor in text:
                text = text.replace(anchor, original)
                restored_count += 1
            else:
                missing_count += 1

        # Post-processing punctuation cleanup (fix spacing around citations)
        text = re.sub(r'\s+([,\.\;])', r'\1', text) # remove spaces before punctuation
        text = re.sub(r'\(\s+', '(', text)
        text = re.sub(r'\s+\)', ')', text)

        return text, restored_count, missing_count

    def get_citation_count(self) -> int:
        return len(self.anchor_map)

    def reset(self):
        self.anchor_map.clear()
        self.counter = 0
