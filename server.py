"""
server.py - Web Interface and REST API for the Academic Paraphraser Engine
"""

import os
import json
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from paraphraser_core import AcademicParaphraser
from burstiness_analyzer import BurstinessAnalyzer
from document_io import DocumentIO

app = FastAPI(title="Limitless Academic Paraphraser & Anti-AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

paraphraser = AcademicParaphraser()
analyzer = BurstinessAnalyzer()

class ParaphraseRequest(BaseModel):
    text: str
    tone: Optional[str] = "phd"
    api_key: Optional[str] = None

class AnalyzeRequest(BaseModel):
    text: str

class ExportDocxRequest(BaseModel):
    text: str
    title: Optional[str] = "Academic Research Document"

@app.post("/api/analyze")
async def analyze_text(req: AnalyzeRequest):
    metrics = analyzer.analyze(req.text)
    return JSONResponse(content=metrics)

@app.post("/api/paraphrase-stream")
async def paraphrase_stream(req: ParaphraseRequest):
    if not req.text.strip():
        return JSONResponse(status_code=400, content={"error": "Text cannot be empty"})

    async def event_generator():
        async for msg in paraphraser.process_document_stream(
            full_text=req.text,
            tone=req.tone or "phd",
            user_api_key=req.api_key,
            concurrency=6
        ):
            yield f"data: {json.dumps(msg)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    extracted_text = DocumentIO.extract_text_from_bytes(contents, file.filename)
    return JSONResponse(content={"text": extracted_text, "filename": file.filename})

@app.post("/api/export-docx")
async def export_docx(req: ExportDocxRequest):
    docx_bytes = DocumentIO.create_academic_docx(req.text, req.title or "Paraphrased Academic Document")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=paraphrased_academic_paper.docx"}
    )

HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Paraphraser & Humanizer Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #182234;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --border: #334155;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background-color: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .brand-badge {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
        }

        .brand h1 {
            font-size: 1.25rem;
            font-weight: 700;
        }

        .header-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }

        select, input[type="text"], input[type="password"] {
            background-color: var(--bg-primary);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.5rem 0.85rem;
            border-radius: 6px;
            font-size: 0.875rem;
            outline: none;
            transition: border-color 0.2s;
        }

        select:focus, input:focus {
            border-color: var(--accent);
        }

        .mode-badge {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid var(--border);
            background-color: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
        }

        .citation-shield-badge {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            background-color: rgba(16, 185, 129, 0.15);
            color: var(--success);
            padding: 0.4rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        /* Progress Bar Strip */
        .progress-bar-container {
            display: none;
            width: 100%;
            background-color: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 0.6rem 2rem;
            align-items: center;
            gap: 1rem;
        }

        .progress-track {
            flex: 1;
            height: 8px;
            background-color: var(--bg-primary);
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid var(--border);
        }

        .progress-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #3b82f6, #10b981);
            transition: width 0.3s ease;
        }

        .progress-text {
            font-size: 0.8rem;
            color: var(--text-secondary);
            min-width: 260px;
        }

        main {
            flex: 1;
            padding: 1.5rem 2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-width: 1700px;
            margin: 0 auto;
            width: 100%;
        }

        .metrics-banner {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
        }

        .metric-card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border);
            padding: 1rem 1.25rem;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .metric-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }

        .metric-value {
            font-size: 1.4rem;
            font-weight: 700;
        }

        .metric-sub {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }

        .editor-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            flex: 1;
            min-height: 520px;
        }

        .editor-pane {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .pane-header {
            padding: 0.75rem 1.25rem;
            border-bottom: 1px solid var(--border);
            background-color: rgba(0, 0, 0, 0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .pane-title {
            font-size: 0.875rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .pane-actions {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }

        .btn {
            background-color: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border);
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        .btn:hover {
            background-color: var(--border);
        }

        .btn-primary {
            background-color: var(--accent);
            border-color: var(--accent);
            color: white;
            font-weight: 600;
            padding: 0.5rem 1.25rem;
        }

        .btn-primary:hover {
            background-color: var(--accent-hover);
        }

        .editor-textarea {
            flex: 1;
            width: 100%;
            background-color: transparent;
            color: var(--text-primary);
            border: none;
            padding: 1.25rem;
            font-family: 'Merriweather', serif;
            font-size: 1rem;
            line-height: 1.8;
            resize: none;
            outline: none;
        }

        .dropzone {
            border: 2px dashed var(--border);
            border-radius: 6px;
            padding: 0.5rem 1rem;
            text-align: center;
            cursor: pointer;
            font-size: 0.75rem;
            color: var(--text-secondary);
            transition: border-color 0.2s;
        }

        .dropzone:hover {
            border-color: var(--accent);
            color: var(--text-primary);
        }

        .status-spinner {
            display: none;
            border: 3px solid rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            border-top: 3px solid var(--accent);
            width: 16px;
            height: 16px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        footer {
            padding: 0.75rem 2rem;
            border-top: 1px solid var(--border);
            font-size: 0.75rem;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
        }

        @media (max-width: 900px) {
            .editor-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <span class="brand-badge">ACADEMIC ENGINE</span>
            <h1>Limitless Paraphraser & Citation Vault</h1>
        </div>

        <div class="header-controls">
            <div id="modeBadge" class="mode-badge">
                Mode: Fast Local Fallback
            </div>

            <div class="citation-shield-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                Citation Shield: ACTIVE
            </div>

            <select id="toneSelect" title="Academic Register">
                <option value="phd">PhD / Journal Peer-Reviewed (Strict)</option>
                <option value="masters">Master's (Analytical & Critical)</option>
                <option value="undergrad">Undergraduate (Articulate Expository)</option>
            </select>

            <input type="password" id="apiKeyInput" placeholder="Gemini API Key (Optional)" style="width: 220px;" title="Enter key for Deep LLM Semantic Mode" oninput="updateModeBadge()">

            <button class="btn btn-primary" id="paraphraseBtn" onclick="runStreamingParaphrase()">
                <div class="status-spinner" id="spinner"></div>
                <span id="btnText">Paraphrase Document</span>
            </button>
        </div>
    </header>

    <!-- Real-time Progress Bar Strip -->
    <div id="progressContainer" class="progress-bar-container">
        <div class="progress-track">
            <div id="progressFill" class="progress-fill"></div>
        </div>
        <div id="progressText" class="progress-text">Initializing parallel chunks...</div>
    </div>

    <main>
        <div class="metrics-banner">
            <div class="metric-card">
                <div class="metric-label">Turnitin / AI Risk</div>
                <div class="metric-value" id="riskVal" style="color: var(--success);">Turnitin-Safe</div>
                <div class="metric-sub" id="riskSub">Natural human cadence</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Sentence Burstiness</div>
                <div class="metric-value" id="burstinessVal">--</div>
                <div class="metric-sub">Std Dev of sentence lengths (&gt;6.0 is human)</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Citations Protected</div>
                <div class="metric-value" id="citationsVal" style="color: var(--accent);">-- / --</div>
                <div class="metric-sub" id="citationsSub">100% integrity guaranteed</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">AI Clichés Removed</div>
                <div class="metric-value" id="clichesVal">--</div>
                <div class="metric-sub">Delve, tapestry, pivotal, etc.</div>
            </div>
        </div>

        <div class="editor-container">
            <!-- Left Pane: Input -->
            <div class="editor-pane">
                <div class="pane-header">
                    <div class="pane-title">
                        <span>Original Source Text</span>
                        <span id="inputWordCount" style="color: var(--text-secondary); font-weight: normal; font-size: 0.75rem;">(0 words)</span>
                    </div>
                    <div class="pane-actions">
                        <label class="dropzone" title="Upload DOCX, PDF, or TXT">
                            <span>📄 Upload File</span>
                            <input type="file" id="fileUpload" style="display: none;" accept=".docx,.pdf,.txt,.md" onchange="handleFileUpload(event)">
                        </label>
                        <button class="btn" onclick="clearInput()">Clear</button>
                    </div>
                </div>
                <textarea id="inputText" class="editor-textarea" placeholder="Paste your essay, thesis draft, or academic chapters here (no word count limit)..." oninput="updateInputStats()"></textarea>
            </div>

            <!-- Right Pane: Output -->
            <div class="editor-pane">
                <div class="pane-header">
                    <div class="pane-title">
                        <span>Paraphrased & Humanized Output</span>
                        <span id="outputWordCount" style="color: var(--text-secondary); font-weight: normal; font-size: 0.75rem;">(0 words)</span>
                    </div>
                    <div class="pane-actions">
                        <button class="btn" onclick="copyOutput()">📋 Copy Text</button>
                        <button class="btn" onclick="downloadDocx()">💾 Download .DOCX</button>
                    </div>
                </div>
                <textarea id="outputText" class="editor-textarea" placeholder="Paraphrased content with verified citations and high burstiness will appear here..." readonly></textarea>
            </div>
        </div>
    </main>

    <footer>
        <span>Project 1: Limitless Academic Paraphrasing Engine</span>
        <span>Parallel Batching &amp; Anti-AI Burstiness Transformer</span>
    </footer>

    <script>
        function updateModeBadge() {
            const key = document.getElementById('apiKeyInput').value.trim();
            const badge = document.getElementById('modeBadge');
            if (key) {
                badge.innerText = 'Mode: Deep Semantic LLM (Active)';
                badge.style.backgroundColor = 'rgba(16, 185, 129, 0.2)';
                badge.style.color = '#34d399';
                badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
            } else {
                badge.innerText = 'Mode: Fast Local Fallback';
                badge.style.backgroundColor = 'rgba(59, 130, 246, 0.15)';
                badge.style.color = '#60a5fa';
                badge.style.borderColor = 'var(--border)';
            }
        }

        function updateInputStats() {
            const text = document.getElementById('inputText').value;
            const words = text.trim() ? text.trim().split(/\\s+/).length : 0;
            document.getElementById('inputWordCount').innerText = `(${words.toLocaleString()} words)`;
        }

        async function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.text) {
                    document.getElementById('inputText').value = data.text;
                    updateInputStats();
                }
            } catch (err) {
                alert('Failed to parse uploaded document: ' + err.message);
            }
        }

        async function runStreamingParaphrase() {
            const text = document.getElementById('inputText').value;
            if (!text.trim()) {
                alert('Please enter or upload text to paraphrase.');
                return;
            }

            const tone = document.getElementById('toneSelect').value;
            const apiKey = document.getElementById('apiKeyInput').value;

            const btn = document.getElementById('paraphraseBtn');
            const spinner = document.getElementById('spinner');
            const btnText = document.getElementById('btnText');
            const progressContainer = document.getElementById('progressContainer');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');

            btn.disabled = true;
            spinner.style.display = 'inline-block';
            btnText.innerText = 'Processing...';
            progressContainer.style.display = 'flex';
            progressFill.style.width = '0%';
            progressText.innerText = 'Initializing parallel batch workers...';

            try {
                const response = await fetch('/api/paraphrase-stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, tone, api_key: apiKey || null })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n\\n');
                    buffer = lines.pop(); // keep remainder

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const eventData = JSON.parse(line.substring(6));

                            if (eventData.type === 'start') {
                                progressText.innerText = `${eventData.mode} - Split into ${eventData.total_chunks} semantic chunks (${eventData.total_citations} citations locked)...`;
                            } else if (eventData.type === 'progress') {
                                progressFill.style.width = eventData.percent + '%';
                                progressText.innerText = `Processing chunks: ${eventData.completed_chunks} / ${eventData.total_chunks} (${eventData.percent}% completed)`;
                            } else if (eventData.type === 'complete') {
                                progressFill.style.width = '100%';
                                progressText.innerText = `Finished! 100% of chunks completed and citations re-anchored.`;

                                document.getElementById('outputText').value = eventData.paraphrased_text;
                                const words = eventData.paraphrased_text.trim().split(/\\s+/).length;
                                document.getElementById('outputWordCount').innerText = `(${words.toLocaleString()} words)`;

                                // Update Metrics
                                const m = eventData.metrics.paraphrased;
                                document.getElementById('burstinessVal').innerText = m.burstiness_stdev.toFixed(2);
                                document.getElementById('riskVal').innerText = m.risk_level.split(' ')[0];
                                document.getElementById('riskSub').innerText = m.risk_level;
                                
                                const citStats = eventData.citation_stats;
                                document.getElementById('citationsVal').innerText = `${citStats.restored} / ${citStats.detected}`;
                                document.getElementById('citationsSub').innerText = `${citStats.integrity_rate} integrity preserved`;

                                document.getElementById('clichesVal').innerText = eventData.metrics.ai_buzzwords_removed;
                            }
                        }
                    }
                }
            } catch (err) {
                alert('Paraphrasing failed: ' + err.message);
            } finally {
                btn.disabled = false;
                spinner.style.display = 'none';
                btnText.innerText = 'Paraphrase Document';
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                }, 4000);
            }
        }

        function copyOutput() {
            const output = document.getElementById('outputText').value;
            if (!output) return;
            navigator.clipboard.writeText(output);
            alert('Copied to clipboard!');
        }

        async function downloadDocx() {
            const text = document.getElementById('outputText').value;
            if (!text.trim()) {
                alert('No paraphrased text to export.');
                return;
            }

            try {
                const res = await fetch('/api/export-docx', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, title: "Academic Research Document" })
                });

                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'paraphrased_academic_paper.docx';
                document.body.appendChild(a);
                a.click();
                a.remove();
            } catch (err) {
                alert('Export failed: ' + err.message);
            }
        }

        function clearInput() {
            document.getElementById('inputText').value = '';
            document.getElementById('outputText').value = '';
            updateInputStats();
        }

        // Initialize mode on load
        updateModeBadge();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return HTMLResponse(content=HTML_UI)

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
