# Limitless Academic Paraphraser & Anti-AI Engine (Project 1)

A dedicated, citation-safe academic re-architecting and humanizing engine designed to pass rigorous academic scrutiny (Turnitin, GPTZero, CopyLeaks) without mangling citations or truncating large documents.

---

## Key Capabilities

1. **Deterministic Citation Shield (`citation_vault.py`)**:
   - Scans text for academic in-text citations across multiple conventions:
     - **APA / Harvard / Chicago**: `(Smith, 2020)`, `(Smith & Jones, 2021)`, `(Smith et al., 2019)`
     - **Narrative Citations**: `Smith (2020)`, `Smith and Jones (2021)`, `Smith et al. (2019)`
     - **Numeric Bracket (IEEE / Vancouver)**: `[1]`, `[1, 2]`, `[3-5]`
     - **Direct Quotation References**: `(Smith, 2020, p. 45)`
   - Converts each reference into an immutable anchor token (`[[CITE_REF_0001]]`) prior to paraphrasing, then re-anchors them back with flawless grammatical placement.
   - **Guarantees 100% citation retention** with a built-in verification counter.

2. **Burstiness & Human Cadence Diagnostics (`burstiness_analyzer.py`)**:
   - AI detectors look for statistical uniformity (flat standard deviation of sentence lengths).
   - This engine computes real-time standard deviation of sentence lengths (`stdev >= 6.5` indicates natural human variance).
   - Scans and strips classic AI tell-words (`delve`, `tapestry`, `pivotal`, `testament`, `furthermore`, `moreover`, `multifaceted`, `beacon`, `underscores`, `in conclusion`).

3. **Limitless Streaming Chunker (`streaming_chunker.py`)**:
   - Handles entire dissertations and books (50,000 to 100,000+ words).
   - Groups text into semantic paragraph blocks with overlapping transitional context buffers.
   - Eliminates model token limits, memory overflow, and context drift.

4. **Document Ingestion & Export (`document_io.py`)**:
   - Ingests `.docx`, `.pdf`, `.txt`, `.md`.
   - Exports formatted, publication-ready Word documents (`.docx`) styled with 1-inch margins, Times New Roman, and 1.5 line spacing.

5. **Interactive Web Workspace (`server.py`)**:
   - Dual-pane interface with live word count tracking, Turnitin Risk Gauge, and Citation Integrity counter.
   - One-click copy and `.docx` download.

---

## Quick Start

### 1. Launch the Web Interface
```bash
python server.py
```
Open your browser to:
```
http://127.0.0.1:8000
```

### 2. Run Verification Tests
```bash
python test_engine.py
```
