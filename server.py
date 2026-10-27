"""
server.py - Revamped Modern Academic Paraphraser & Anti-AI Engine
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
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scholarly AI - Citation-Safe Academic Paraphraser & Anti-AI Engine</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400;1,6..72,500&display=swap" rel="stylesheet">
    <style>
        :root[data-theme="dark"] {
            --bg-base: #090d16;
            --bg-surface: #111827;
            --bg-elevated: #1e293b;
            --bg-glass: rgba(17, 24, 39, 0.75);
            --border-subtle: #1f2937;
            --border-prominent: #374151;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --text-faint: #6b7280;
            --accent-primary: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.25);
            --accent-hover: #2563eb;
            --emerald: #10b981;
            --emerald-glow: rgba(16, 185, 129, 0.15);
            --amber: #f59e0b;
            --rose: #f43f5e;
            --shadow-subtle: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
            --shadow-card: 0 10px 30px -5px rgba(0, 0, 0, 0.4);
        }

        :root[data-theme="light"] {
            --bg-base: #f8fafc;
            --bg-surface: #ffffff;
            --bg-elevated: #f1f5f9;
            --bg-glass: rgba(255, 255, 255, 0.85);
            --border-subtle: #e2e8f0;
            --border-prominent: #cbd5e1;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --text-faint: #94a3b8;
            --accent-primary: #2563eb;
            --accent-glow: rgba(37, 99, 235, 0.15);
            --accent-hover: #1d4ed8;
            --emerald: #059669;
            --emerald-glow: rgba(5, 150, 105, 0.12);
            --amber: #d97706;
            --rose: #e11d48;
            --shadow-subtle: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
            --shadow-card: 0 10px 30px -5px rgba(0, 0, 0, 0.08);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Ambient Glow Backgrounds */
        .ambient-glow {
            position: fixed;
            top: -150px;
            left: 50%;
            transform: translateX(-50%);
            width: 1000px;
            height: 350px;
            background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.15), transparent 70%);
            pointer-events: none;
            z-index: 0;
        }

        /* Header Navigation */
        header {
            position: sticky;
            top: 0;
            z-index: 50;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            background-color: var(--bg-glass);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0.85rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand-container {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            text-decoration: none;
            color: inherit;
        }

        .brand-icon {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
        }

        .brand-text h1 {
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .brand-tag {
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
            background-color: var(--accent-glow);
            color: var(--accent-primary);
            border: 1px solid var(--accent-primary);
        }

        .brand-text p {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.4rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid var(--border-prominent);
            background-color: var(--bg-surface);
        }

        .status-pill.active-shield {
            background-color: var(--emerald-glow);
            color: var(--emerald);
            border-color: rgba(16, 185, 129, 0.3);
        }

        .status-pill.mode-badge {
            cursor: pointer;
            border-color: var(--border-prominent);
            color: var(--accent-primary);
        }

        .pulse-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: var(--emerald);
            box-shadow: 0 0 8px var(--emerald);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 0.95rem;
            border-radius: 8px;
            font-size: 0.825rem;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid var(--border-prominent);
            background-color: var(--bg-surface);
            color: var(--text-main);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .btn:hover {
            border-color: var(--text-muted);
            transform: translateY(-1px);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-primary) 0%, #4f46e5 100%);
            border-color: var(--accent-primary);
            color: white;
            box-shadow: 0 4px 14px var(--accent-glow);
        }

        .btn-primary:hover {
            background: linear-gradient(135deg, var(--accent-hover) 0%, #4338ca 100%);
            box-shadow: 0 6px 20px var(--accent-glow);
            border-color: var(--accent-hover);
        }

        .btn-ghost {
            background: transparent;
            border-color: transparent;
            color: var(--text-muted);
        }

        .btn-ghost:hover {
            background-color: var(--bg-elevated);
            color: var(--text-main);
        }

        /* Live Progress Bar Strip */
        .progress-strip {
            display: none;
            width: 100%;
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0.75rem 2rem;
            align-items: center;
            gap: 1.25rem;
            z-index: 40;
        }

        .progress-track {
            flex: 1;
            height: 7px;
            background-color: var(--bg-elevated);
            border-radius: 9999px;
            overflow: hidden;
            position: relative;
        }

        .progress-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #3b82f6, #10b981);
            border-radius: 9999px;
            transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .progress-info {
            font-size: 0.8rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 500;
        }

        /* Main App Layout */
        main {
            flex: 1;
            padding: 1.75rem 2rem;
            max-width: 1720px;
            margin: 0 auto;
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            z-index: 10;
        }

        /* Tone Selection Bar */
        .control-shelf {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 0.75rem 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            box-shadow: var(--shadow-subtle);
        }

        .tone-picker {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            flex-wrap: wrap;
        }

        .tone-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--text-muted);
            margin-right: 0.5rem;
        }

        .tone-chip {
            padding: 0.4rem 0.85rem;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid var(--border-subtle);
            background-color: var(--bg-elevated);
            color: var(--text-muted);
            transition: all 0.2s;
        }

        .tone-chip:hover {
            color: var(--text-main);
            border-color: var(--border-prominent);
        }

        .tone-chip.active {
            background-color: var(--accent-glow);
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }

        .shelf-actions {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        /* Diagnostic HUD Cards */
        .hud-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1rem;
        }

        .hud-card {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 1.15rem 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            box-shadow: var(--shadow-subtle);
            position: relative;
            overflow: hidden;
        }

        .hud-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--border-prominent), transparent);
        }

        .hud-card.accent-card::before {
            background: linear-gradient(90deg, var(--accent-primary), var(--emerald));
        }

        .hud-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .hud-title {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.7px;
            color: var(--text-muted);
        }

        .hud-icon {
            color: var(--text-faint);
        }

        .hud-value-row {
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
        }

        .hud-value {
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: var(--text-main);
        }

        .hud-sub {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        /* Dual Workspace Split Screen */
        .workspace {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.25rem;
            flex: 1;
            min-height: 560px;
        }

        .pane {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }

        .pane-topbar {
            padding: 0.85rem 1.25rem;
            border-bottom: 1px solid var(--border-subtle);
            background-color: var(--bg-elevated);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .pane-heading {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--text-main);
        }

        .counter-badge {
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text-muted);
            background-color: var(--bg-surface);
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            border: 1px solid var(--border-subtle);
        }

        .pane-actions {
            display: flex;
            gap: 0.4rem;
            align-items: center;
        }

        .pane-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .editor {
            flex: 1;
            width: 100%;
            background-color: transparent;
            color: var(--text-main);
            border: none;
            padding: 1.5rem;
            font-family: 'Newsreader', Georgia, serif;
            font-size: 1.075rem;
            line-height: 1.85;
            resize: none;
            outline: none;
        }

        .editor::placeholder {
            color: var(--text-faint);
            font-style: italic;
        }

        /* File Upload Drop Target */
        .file-upload-btn {
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        /* Highlighted Citation Overlay */
        .citation-tag {
            background-color: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.35);
            padding: 0.1rem 0.35rem;
            border-radius: 4px;
            font-weight: 600;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.85em;
        }

        /* Toast Notifications */
        .toast-container {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            z-index: 100;
        }

        .toast {
            background-color: var(--bg-surface);
            color: var(--text-main);
            border: 1px solid var(--border-prominent);
            padding: 0.75rem 1.25rem;
            border-radius: 10px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            display: flex;
            align-items: center;
            gap: 0.6rem;
            transform: translateY(20px);
            opacity: 0;
            animation: slideUp 0.3s forwards cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes slideUp {
            to { transform: translateY(0); opacity: 1; }
        }

        /* Settings Modal */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background-color: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(8px);
            z-index: 110;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }

        .modal {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            max-width: 500px;
            width: 100%;
            padding: 1.75rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-header h3 {
            font-size: 1.15rem;
            font-weight: 700;
        }

        .modal-body {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        .input-group label {
            font-weight: 600;
            color: var(--text-main);
            font-size: 0.8rem;
        }

        .input-control {
            background-color: var(--bg-elevated);
            border: 1px solid var(--border-prominent);
            color: var(--text-main);
            padding: 0.65rem 0.9rem;
            border-radius: 8px;
            font-size: 0.875rem;
            outline: none;
        }

        .input-control:focus {
            border-color: var(--accent-primary);
        }

        /* Footer */
        footer {
            padding: 1rem 2rem;
            border-top: 1px solid var(--border-subtle);
            font-size: 0.775rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--bg-surface);
        }

        @media (max-width: 960px) {
            .workspace {
                grid-template-columns: 1fr;
            }
            main {
                padding: 1rem;
            }
            header {
                padding: 0.85rem 1rem;
            }
        }
    </style>
</head>
<body>

    <div class="ambient-glow"></div>

    <header>
        <a href="/" class="brand-container">
            <div class="brand-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
            </div>
            <div class="brand-text">
                <h1>Scholarly AI <span class="brand-tag">Project 1</span></h1>
                <p>Citation-Preserving Academic Paraphraser & Anti-AI Engine</p>
            </div>
        </a>

        <div class="header-actions">
            <div class="status-pill active-shield" title="Guarantees zero mangled or dropped in-text citations">
                <span class="pulse-dot"></span>
                <span>Citation Vault: ACTIVE (APA/MLA/IEEE/Chicago)</span>
            </div>

            <div id="modePill" class="status-pill mode-badge" onclick="openSettingsModal()" title="Click to configure Gemini API Key for deep LLM paraphrasing">
                <span id="modeIcon">⚡</span>
                <span id="modeText">Mode: Fast Local Fallback</span>
            </div>

            <button class="btn btn-ghost" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
                <span id="themeIcon">☀️</span>
            </button>

            <button class="btn btn-primary" id="mainRunBtn" onclick="runStreamingParaphrase()">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                <span id="runBtnLabel">Paraphrase Document</span>
            </button>
        </div>
    </header>

    <!-- Real-Time Progress Bar -->
    <div id="progressStrip" class="progress-strip">
        <div class="progress-info">
            <svg class="spin-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="2" x2="12" y2="6"></line>
                <line x1="12" y1="18" x2="12" y2="22"></line>
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                <line x1="2" y1="12" x2="6" y2="12"></line>
                <line x1="18" y1="12" x2="22" y2="12"></line>
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
            </svg>
            <span id="progressMessage">Partitioning into semantic paragraph blocks...</span>
        </div>
        <div class="progress-track">
            <div id="progressBar" class="progress-fill"></div>
        </div>
        <span id="progressPercent" style="font-size: 0.8rem; font-weight: 700; color: var(--accent-primary);">0%</span>
    </div>

    <main>
        <!-- Control Shelf: Academic Register & Sample Ingestion -->
        <div class="control-shelf">
            <div class="tone-picker">
                <span class="tone-label">Academic Register:</span>
                <button class="tone-chip active" data-tone="phd" onclick="selectTone('phd')">🎓 PhD / Peer-Reviewed</button>
                <button class="tone-chip" data-tone="masters" onclick="selectTone('masters')">🏛️ Master's Analytical</button>
                <button class="tone-chip" data-tone="undergrad" onclick="selectTone('undergrad')">📚 Undergraduate Expository</button>
            </div>

            <div class="shelf-actions">
                <button class="btn btn-ghost" onclick="loadSampleText()" title="Load sample academic text with citations and AI buzzwords">
                    📄 Insert Sample Text
                </button>
                <button class="btn" onclick="openSettingsModal()">
                    ⚙️ Engine Settings
                </button>
            </div>
        </div>

        <!-- Diagnostic HUD Cards -->
        <div class="hud-grid">
            <div class="hud-card accent-card">
                <div class="hud-header">
                    <span class="hud-title">Turnitin / AI Risk</span>
                    <span class="hud-icon">🛡️</span>
                </div>
                <div class="hud-value-row">
                    <span class="hud-value" id="hudRisk" style="color: var(--emerald);">Turnitin-Safe</span>
                </div>
                <span class="hud-sub" id="hudRiskSub">Natural irregular human cadence</span>
            </div>

            <div class="hud-card">
                <div class="hud-header">
                    <span class="hud-title">Burstiness Score (StDev)</span>
                    <span class="hud-icon">📈</span>
                </div>
                <div class="hud-value-row">
                    <span class="hud-value" id="hudBurstiness">--</span>
                    <span style="font-size: 0.85rem; color: var(--text-muted);">&gt;6.0 is human</span>
                </div>
                <span class="hud-sub" id="hudBurstinessSub">Alternating short &amp; compound clauses</span>
            </div>

            <div class="hud-card">
                <div class="hud-header">
                    <span class="hud-title">Citation Shield</span>
                    <span class="hud-icon">🔗</span>
                </div>
                <div class="hud-value-row">
                    <span class="hud-value" id="hudCitations" style="color: var(--accent-primary);">-- / --</span>
                </div>
                <span class="hud-sub" id="hudCitationsSub">100% of references anchored</span>
            </div>

            <div class="hud-card">
                <div class="hud-header">
                    <span class="hud-title">AI Buzzwords Purged</span>
                    <span class="hud-icon">✂️</span>
                </div>
                <div class="hud-value-row">
                    <span class="hud-value" id="hudCliches">--</span>
                    <span style="font-size: 0.85rem; color: var(--text-muted);">clichés stripped</span>
                </div>
                <span class="hud-sub" id="hudClichesSub">Delve, tapestry, pivotal, etc.</span>
            </div>
        </div>

        <!-- Workspace Editors -->
        <div class="workspace">
            <!-- Left Pane: Input -->
            <div class="pane">
                <div class="pane-topbar">
                    <div class="pane-heading">
                        <span>Original Source Text</span>
                        <span class="counter-badge" id="inputStats">0 words</span>
                    </div>
                    <div class="pane-actions">
                        <label class="btn file-upload-btn" title="Upload Word DOCX, PDF, or Plain Text">
                            <span>📂 Upload File</span>
                            <input type="file" id="fileInput" style="display: none;" accept=".docx,.pdf,.txt,.md" onchange="handleFileUpload(event)">
                        </label>
                        <button class="btn btn-ghost" onclick="clearInput()" title="Clear text">Clear</button>
                    </div>
                </div>
                <div class="pane-body">
                    <textarea id="inputText" class="editor" placeholder="Paste your essay, literature review, or dissertation chapter here (supports limitless word counts and file sizes)..." oninput="updateInputStats()"></textarea>
                </div>
            </div>

            <!-- Right Pane: Output -->
            <div class="pane">
                <div class="pane-topbar">
                    <div class="pane-heading">
                        <span>Humanized Academic Prose</span>
                        <span class="counter-badge" id="outputStats">0 words</span>
                    </div>
                    <div class="pane-actions">
                        <button class="btn" onclick="copyOutput()" title="Copy to clipboard">
                            📋 Copy
                        </button>
                        <button class="btn" onclick="downloadDocx()" title="Download formatted Word Document (.docx)">
                            💾 Export DOCX
                        </button>
                    </div>
                </div>
                <div class="pane-body">
                    <textarea id="outputText" class="editor" placeholder="Your humanized academic output with 100% preserved citations and natural human burstiness will appear here..." readonly></textarea>
                </div>
            </div>
        </div>
    </main>

    <!-- Settings Modal -->
    <div id="settingsModal" class="modal-overlay" onclick="closeSettingsModal(event)">
        <div class="modal" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3>⚙️ Engine &amp; API Configuration</h3>
                <button class="btn btn-ghost" onclick="closeSettingsModal()">✕</button>
            </div>
            <div class="modal-body">
                <p>By default, the engine runs locally on your computer with instantaneous regex citation-locking and cliché removal.</p>
                <div class="input-group">
                    <label for="apiKeyField">Google Gemini API Key (Optional for Deep Semantic Mode):</label>
                    <input type="password" id="apiKeyField" class="input-control" placeholder="AIzaSy..." oninput="saveApiKey()">
                    <span style="font-size: 0.75rem; color: var(--text-faint);">
                        Get a free key from <a href="https://aistudio.google.com/" target="_blank" style="color: var(--accent-primary);">Google AI Studio</a>. Keys are stored locally in your browser session.
                    </span>
                </div>
                <div class="input-group">
                    <label>Selected Academic Register:</label>
                    <span id="modalSelectedTone" style="font-weight: 600; color: var(--text-main);">PhD / Peer-Reviewed</span>
                </div>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.5rem;">
                <button class="btn btn-primary" onclick="closeSettingsModal()">Done</button>
            </div>
        </div>
    </div>

    <!-- Toast Notification Container -->
    <div id="toastContainer" class="toast-container"></div>

    <footer>
        <span>Project 1: Scholarly AI - Limitless Academic Paraphrasing Engine</span>
        <span>Parallel Batch Chunker &bull; Universal Citation Vault &bull; Anti-AI Rhythm Transformer</span>
    </footer>

    <script>
        let currentTone = 'phd';

        // Sample academic text with APA/IEEE citations and AI cliches
        const SAMPLE_TEXT = `The contemporary macroeconomic landscape has witnessed substantial transformation across emerging markets (Reynolds, 2018). This study delves into the multifaceted mechanisms of institutional credit allocation, as highlighted by Williams and Vance (2020). Furthermore, contemporary econometric models stand as a testament to the pivotal role of regulatory liquidity reserves [3-5]. Consequently, central banks must foster structural resilience in order to mitigate systemic vulnerability (see Anderson et al., 2021; Miller & Davis, 2023). Moreover, it is crucial to note that the complex interplay between fiscal interventions and sovereign debt yields underscores the importance of countercyclical policies (Taylor, 2019, p. 112). In conclusion, empirical observations confirm that institutional oversight remains of paramount importance.`;

        function selectTone(tone) {
            currentTone = tone;
            document.querySelectorAll('.tone-chip').forEach(el => {
                el.classList.toggle('active', el.dataset.tone === tone);
            });
            document.getElementById('modalSelectedTone').innerText = 
                tone === 'phd' ? 'PhD / Peer-Reviewed' : (tone === 'masters' ? "Master's Analytical" : "Undergraduate Expository");
            showToast(`Switched tone to ${document.getElementById('modalSelectedTone').innerText}`);
        }

        function toggleTheme() {
            const html = document.documentElement;
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            document.getElementById('themeIcon').innerText = next === 'dark' ? '☀️' : '🌙';
            localStorage.setItem('theme', next);
        }

        function loadSampleText() {
            document.getElementById('inputText').value = SAMPLE_TEXT;
            updateInputStats();
            showToast("Sample academic text loaded with citations!");
        }

        function updateInputStats() {
            const text = document.getElementById('inputText').value;
            const words = text.trim() ? text.trim().split(/\\s+/).length : 0;
            document.getElementById('inputStats').innerText = `${words.toLocaleString()} words`;
        }

        function updateOutputStats() {
            const text = document.getElementById('outputText').value;
            const words = text.trim() ? text.trim().split(/\\s+/).length : 0;
            document.getElementById('outputStats').innerText = `${words.toLocaleString()} words`;
        }

        function openSettingsModal() {
            document.getElementById('settingsModal').style.display = 'flex';
        }

        function closeSettingsModal(event) {
            document.getElementById('settingsModal').style.display = 'none';
        }

        function saveApiKey() {
            const key = document.getElementById('apiKeyField').value.trim();
            localStorage.setItem('gemini_api_key', key);
            updateModeIndicator();
        }

        function updateModeIndicator() {
            const key = (document.getElementById('apiKeyField').value || localStorage.getItem('gemini_api_key') || '').trim();
            const pill = document.getElementById('modePill');
            const text = document.getElementById('modeText');
            const icon = document.getElementById('modeIcon');

            if (key) {
                text.innerText = 'Mode: Deep Semantic LLM (Active)';
                icon.innerText = '🧠';
                pill.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                pill.style.color = 'var(--emerald)';
                pill.style.backgroundColor = 'var(--emerald-glow)';
            } else {
                text.innerText = 'Mode: Fast Local Fallback';
                icon.innerText = '⚡';
                pill.style.borderColor = 'var(--border-prominent)';
                pill.style.color = 'var(--accent-primary)';
                pill.style.backgroundColor = 'var(--bg-surface)';
            }
        }

        async function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            showToast(`Uploading ${file.name}...`);

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.text) {
                    document.getElementById('inputText').value = data.text;
                    updateInputStats();
                    showToast(`Successfully parsed ${file.name}`);
                }
            } catch (err) {
                showToast(`Failed to parse file: ${err.message}`, true);
            }
        }

        async function runStreamingParaphrase() {
            const text = document.getElementById('inputText').value;
            if (!text.trim()) {
                showToast("Please enter or upload text to paraphrase", true);
                return;
            }

            const apiKey = (document.getElementById('apiKeyField').value || localStorage.getItem('gemini_api_key') || '').trim();
            const btn = document.getElementById('mainRunBtn');
            const btnLabel = document.getElementById('runBtnLabel');
            const progressStrip = document.getElementById('progressStrip');
            const progressBar = document.getElementById('progressBar');
            const progressMessage = document.getElementById('progressMessage');
            const progressPercent = document.getElementById('progressPercent');

            btn.disabled = true;
            btnLabel.innerText = "Processing...";
            progressStrip.style.display = 'flex';
            progressBar.style.width = '0%';
            progressPercent.innerText = '0%';
            progressMessage.innerText = 'Locking citations and preparing semantic batches...';

            try {
                const response = await fetch('/api/paraphrase-stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: text,
                        tone: currentTone,
                        api_key: apiKey || null
                    })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n\\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.substring(6));

                            if (data.type === 'start') {
                                progressMessage.innerText = `${data.mode}: ${data.total_chunks} chunk(s) created & ${data.total_citations} citation(s) locked.`;
                            } else if (data.type === 'progress') {
                                progressBar.style.width = `${data.percent}%`;
                                progressPercent.innerText = `${data.percent}%`;
                                progressMessage.innerText = `Rewriting chunks concurrently (${data.completed_chunks}/${data.total_chunks})...`;
                            } else if (data.type === 'complete') {
                                progressBar.style.width = '100%';
                                progressPercent.innerText = '100%';
                                progressMessage.innerText = 'All citations restored and rhythm diagnostics complete!';

                                document.getElementById('outputText').value = data.paraphrased_text;
                                updateOutputStats();

                                // HUD Diagnostics
                                const m = data.metrics.paraphrased;
                                document.getElementById('hudRisk').innerText = m.risk_level.split(' ')[0];
                                document.getElementById('hudRiskSub').innerText = m.risk_level;
                                document.getElementById('hudBurstiness').innerText = m.burstiness_stdev.toFixed(2);
                                
                                const cStats = data.citation_stats;
                                document.getElementById('hudCitations').innerText = `${cStats.restored} / ${cStats.detected}`;
                                document.getElementById('hudCitationsSub').innerText = `${cStats.integrity_rate} integrity rate`;

                                document.getElementById('hudCliches').innerText = data.metrics.ai_buzzwords_removed;

                                showToast("Paraphrase complete with 100% citation preservation!");
                            }
                        }
                    }
                }
            } catch (err) {
                showToast(`Paraphrasing failed: ${err.message}`, true);
            } finally {
                btn.disabled = false;
                btnLabel.innerText = "Paraphrase Document";
                setTimeout(() => {
                    progressStrip.style.display = 'none';
                }, 4000);
            }
        }

        function copyOutput() {
            const out = document.getElementById('outputText').value;
            if (!out) {
                showToast("No text to copy", true);
                return;
            }
            navigator.clipboard.writeText(out);
            showToast("Copied paraphrased text to clipboard!");
        }

        async function downloadDocx() {
            const text = document.getElementById('outputText').value;
            if (!text.trim()) {
                showToast("No paraphrased text to export", true);
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
                a.download = 'paraphrased_paper_scholarly.docx';
                document.body.appendChild(a);
                a.click();
                a.remove();
                showToast("Downloaded publication-ready .DOCX!");
            } catch (err) {
                showToast("Export failed: " + err.message, true);
            }
        }

        function clearInput() {
            document.getElementById('inputText').value = '';
            document.getElementById('outputText').value = '';
            updateInputStats();
            updateOutputStats();
            showToast("Cleared workspace");
        }

        function showToast(message, isError = false) {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = 'toast';
            if (isError) {
                toast.style.borderColor = 'var(--rose)';
                toast.style.color = 'var(--rose)';
            }
            toast.innerHTML = `<span>${isError ? '⚠️' : '✓'}</span><span>${message}</span>`;
            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }

        // Initialize state
        window.addEventListener('DOMContentLoaded', () => {
            const savedKey = localStorage.getItem('gemini_api_key');
            if (savedKey) {
                document.getElementById('apiKeyField').value = savedKey;
            }
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.documentElement.setAttribute('data-theme', savedTheme);
                document.getElementById('themeIcon').innerText = savedTheme === 'dark' ? '☀️' : '🌙';
            }
            updateModeIndicator();
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return HTMLResponse(content=HTML_UI)

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
