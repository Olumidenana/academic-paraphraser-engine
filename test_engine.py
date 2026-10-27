"""
test_engine.py - Verification suite for the Academic Paraphraser Engine
"""

from citation_vault import CitationVault
from burstiness_analyzer import BurstinessAnalyzer
from streaming_chunker import StreamingChunker
from paraphraser_core import AcademicParaphraser

def test_citation_vault():
    vault = CitationVault()
    sample = (
        "Recent investigations (Smith, 2020) demonstrated significant variation. "
        "Furthermore, according to Johnson et al. (2021), this aligns with prior findings [1, 2]. "
        "Other studies have questioned this premise (see Brown & Miller, 2019; Taylor, 2022)."
    )
    
    masked, matches = vault.mask(sample)
    print(f"[TEST 1] Masked text:\n{masked}\n")
    assert len(matches) >= 3, f"Expected at least 3 citations, found {len(matches)}"
    for m in matches:
        assert m.anchor_id in masked

    unmasked, restored, missing = vault.unmask(masked)
    print(f"[TEST 1] Restored: {restored}, Missing: {missing}")
    assert missing == 0, "No citations should be missing"
    assert "Smith, 2020" in unmasked
    assert "Johnson et al. (2021)" in unmasked
    assert "[1, 2]" in unmasked
    print("[TEST 1 PASSED] Citation Vault functions with 100% fidelity.\n")

def test_burstiness_analyzer():
    analyzer = BurstinessAnalyzer()
    ai_like_text = (
        "This study delves into the rich tapestry of modern economics. "
        "Furthermore, it stands as a testament to the multifaceted nature of market forces. "
        "Moreover, it is crucial to note that these factors play a pivotal role in shaping policy."
    )
    report = analyzer.analyze(ai_like_text)
    print(f"[TEST 2] AI-like Text Analysis:\n{report}")
    assert report["ai_buzzword_count"] >= 3, "Should detect multiple AI buzzwords"
    assert report["risk_level"].startswith("High") or report["risk_level"].startswith("Moderate")
    print("[TEST 2 PASSED] AI buzzword and risk detector verified.\n")

def test_full_pipeline():
    paraphraser = AcademicParaphraser()
    sample_academic = (
        "The economic landscape has witnessed substantial transformation (Reynolds, 2018). "
        "This study delves into the multifaceted mechanisms of institutional credit allocation, "
        "as highlighted by Williams and Vance (2020). Furthermore, contemporary econometric models "
        "stand as a testament to the pivotal role of regulatory liquidity reserves [3-5]. "
        "Consequently, central banks must foster structural resilience (see Anderson et al., 2021)."
    )
    result = paraphraser.process_document(sample_academic, tone="phd")
    print("[TEST 3] Paraphrasing Pipeline Result:")
    print("Original:", result["original_text"])
    print("---")
    print("Paraphrased:", result["paraphrased_text"])
    print("---")
    print("Citation Integrity:", result["citation_stats"])
    print("Burstiness improvement:", result["metrics"]["burstiness_improvement"])
    print("AI buzzwords removed:", result["metrics"]["ai_buzzwords_removed"])
    
    assert result["citation_stats"]["missing"] == 0, "Zero citations should be dropped"
    assert result["citation_stats"]["restored"] >= 3, "All citations must be restored"
    print("\n[TEST 3 PASSED] Full round-trip pipeline succeeded!")

if __name__ == "__main__":
    test_citation_vault()
    test_burstiness_analyzer()
    test_full_pipeline()
