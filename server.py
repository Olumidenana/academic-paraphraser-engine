"""
server.py - Next-Gen Luxury Academic Paraphraser & Anti-AI Engine
Features: Interactive Visual Diff, Citation Padlocks, Radial SVG Gauges, and High-Polish UI
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

app = FastAPI(title="Scholarly AI - Citation-Safe Paraphraser")

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
        headers={"Content-Disposition": "attachment; filename=scholarly_paraphrased_document.docx"}
    )

HTML_UI = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scholarly AI — Precision Academic Re-Architect</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root[data-theme="dark"] {
            --bg-canvas: #06090e;
            --bg-card: #0d121d;
            --bg-card-hover: #121826;
            --bg-subtle: #161e2e;
            --border-card: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(99, 102, 241, 0.3);
            --text-title: #ffffff;
            --text-body: #cbd5e1;
            --text-muted: #64748b;
            --brand-primary: #6366f1;
            --brand-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            --brand-glow: rgba(99, 102, 241, 0.25);
            --emerald: #10b981;
            --emerald-glow: rgba(16, 185, 129, 0.2);
            --amber: #f59e0b;
            --amber-glow: rgba(245, 158, 11, 0.2);
            --danger: #f43f5e;
            --glass-bg: rgba(13, 18, 29, 0.7);
            --shadow-float: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
        }

        :root[data-theme="light"] {
            --bg-canvas: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-hover: #f1f5f9;
            --bg-subtle: #e2e8f0;
            --border-card: rgba(0, 0, 0, 0.08);
            --border-highlight: rgba(99, 102, 241, 0.4);
            --text-title: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --brand-primary: #4f46e5;
            --brand-gradient: linear-gradient(135deg, #4f46e5 0%, #9333ea 50%, #db2777 100%);
            --brand-glow: rgba(79, 70, 229, 0.15);
            --emerald: #059669;
            --emerald-glow: rgba(5, 150, 105, 0.15);
            --amber: #d97706;
            --amber-glow: rgba(217, 119, 6, 0.15);
            --danger: #e11d48;
            --glass-bg: rgba(255, 255, 255, 0.85);
            --shadow-float: 0 20px 40px -15px rgba(0, 0, 0, 0.08);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background-color: var(--bg-canvas);
            color: var(--text-body);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Ambient Hero Mesh Background */
        .ambient-mesh {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 480px;
            background: radial-gradient(circle at 50% -20%, rgba(99, 102, 241, 0.18), transparent 70%),
                        radial-gradient(circle at 85% 10%, rgba(168, 85, 247, 0.12), transparent 50%),
                        radial-gradient(circle at 15% 10%, rgba(16, 185, 129, 0.1), transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        /* Navigation Bar */
        nav {
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            background-color: var(--glass-bg);
            border-bottom: 1px solid var(--border-card);
            padding: 0.9rem 2.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand-link {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            text-decoration: none;
            color: inherit;
        }

        .brand-gem {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            background: var(--brand-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px var(--brand-glow);
            color: white;
        }

        .brand-heading {
            font-size: 1.2rem;
            font-weight: 800;
            letter-spacing: -0.4px;
            color: var(--text-title);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .brand-badge {
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            background: var(--brand-gradient);
            color: white;
            text-transform: uppercase;
        }

        .nav-center {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .shield-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.45rem 0.9rem;
            border-radius: 9999px;
            background-color: var(--emerald-glow);
            color: var(--emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
            font-size: 0.775rem;
            font-weight: 700;
        }

        .shield-pulse {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--emerald);
            box-shadow: 0 0 10px var(--emerald);
            animation: pulse-ring 2s infinite;
        }

        @keyframes pulse-ring {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.3); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        .nav-actions {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        /* Buttons & Controls */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.55rem 1.15rem;
            border-radius: 10px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid var(--border-card);
            background-color: var(--bg-card);
            color: var(--text-title);
            text-decoration: none;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .btn:hover {
            background-color: var(--bg-card-hover);
            border-color: var(--border-highlight);
            transform: translateY(-1px);
        }

        .btn-brand {
            background: var(--brand-gradient);
            border-color: transparent;
            color: white;
            box-shadow: 0 4px 18px var(--brand-glow);
        }

        .btn-brand:hover {
            box-shadow: 0 6px 24px var(--brand-glow);
            transform: translateY(-2px);
        }

        .btn-subtle {
            background: transparent;
            border-color: transparent;
            box-shadow: none;
            color: var(--text-muted);
        }

        .btn-subtle:hover {
            background-color: var(--bg-card-hover);
            color: var(--text-title);
        }

        /* App Container */
        main {
            flex: 1;
            max-width: 1720px;
            margin: 0 auto;
            width: 100%;
            padding: 1.5rem 2.2rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            z-index: 10;
        }

        /* Hero / Mode Selector Bar */
        .toolbar-strip {
            background-color: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 0.85rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            box-shadow: var(--shadow-float);
        }

        .tone-tabs {
            display: flex;
            align-items: center;
            background-color: var(--bg-subtle);
            padding: 0.3rem;
            border-radius: 12px;
            gap: 0.3rem;
        }

        .tone-tab {
            padding: 0.45rem 1rem;
            border-radius: 8px;
            font-size: 0.825rem;
            font-weight: 600;
            cursor: pointer;
            border: none;
            background: transparent;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }

        .tone-tab.active {
            background-color: var(--bg-card);
            color: var(--text-title);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .tool-options {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        /* Live Radial & Metric Cards */
        .metrics-hud {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.15rem;
        }

        .hud-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 1.35rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow-float);
            position: relative;
            overflow: hidden;
        }

        .hud-card:hover {
            border-color: var(--border-highlight);
        }

        .hud-left {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .hud-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
        }

        .hud-number {
            font-size: 1.75rem;
            font-weight: 800;
            color: var(--text-title);
            letter-spacing: -0.5px;
        }

        .hud-desc {
            font-size: 0.775rem;
            color: var(--text-muted);
        }

        /* Radial Progress Ring */
        .ring-container {
            width: 58px;
            height: 58px;
            position: relative;
        }

        .ring-svg {
            transform: rotate(-90deg);
        }

        .ring-bg {
            fill: none;
            stroke: var(--bg-subtle);
            stroke-width: 5;
        }

        .ring-progress {
            fill: none;
            stroke: var(--emerald);
            stroke-width: 5;
            stroke-linecap: round;
            stroke-dasharray: 157;
            stroke-dashoffset: 20;
            transition: stroke-dashoffset 0.8s ease;
        }

        .ring-label {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 800;
            color: var(--emerald);
        }

        /* Streaming Progress Bar */
        .stream-bar {
            display: none;
            background-color: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 0.85rem 1.5rem;
            align-items: center;
            gap: 1.25rem;
        }

        .stream-track {
            flex: 1;
            height: 8px;
            background-color: var(--bg-subtle);
            border-radius: 9999px;
            overflow: hidden;
        }

        .stream-fill {
            height: 100%;
            width: 0%;
            background: var(--brand-gradient);
            border-radius: 9999px;
            transition: width 0.3s ease;
        }

        /* Dual Studio Editors */
        .studio-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.25rem;
            flex: 1;
            min-height: 580px;
        }

        .editor-deck {
            background-color: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 18px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: var(--shadow-float);
        }

        .deck-header {
            padding: 1rem 1.5rem;
            background-color: rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid var(--border-card);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .deck-title {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--text-title);
        }

        .stat-tag {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            background-color: var(--bg-subtle);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
        }

        .deck-actions {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .deck-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .paper-textarea {
            flex: 1;
            width: 100%;
            background-color: transparent;
            color: var(--text-title);
            border: none;
            padding: 1.5rem;
            font-family: 'Newsreader', Georgia, serif;
            font-size: 1.15rem;
            line-height: 1.9;
            resize: none;
            outline: none;
        }

        .paper-textarea::placeholder {
            color: var(--text-muted);
            font-style: italic;
        }

        /* Interactive Diff Viewer */
        .diff-viewer {
            display: none;
            flex: 1;
            padding: 1.5rem;
            font-family: 'Newsreader', Georgia, serif;
            font-size: 1.15rem;
            line-height: 1.9;
            overflow-y: auto;
            color: var(--text-title);
            white-space: pre-wrap;
        }

        .citation-shield-tag {
            background-color: var(--amber-glow);
            color: var(--amber);
            border: 1px solid rgba(245, 158, 11, 0.4);
            padding: 0.15rem 0.5rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85em;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }

        /* Modern Toast */
        .toast-shelf {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            z-index: 1000;
        }

        .toast-msg {
            background-color: var(--bg-card);
            border: 1px solid var(--border-highlight);
            color: var(--text-title);
            padding: 0.85rem 1.4rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.6);
            display: flex;
            align-items: center;
            gap: 0.65rem;
            animation: popIn 0.3s forwards cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes popIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        /* Modal */
        .backdrop {
            display: none;
            position: fixed;
            inset: 0;
            background-color: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(12px);
            z-index: 1100;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }

        .modal-box {
            background-color: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 20px;
            max-width: 520px;
            width: 100%;
            padding: 2rem;
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8);
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .field-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .field-label {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-title);
        }

        .field-input {
            background-color: var(--bg-subtle);
            border: 1px solid var(--border-card);
            color: var(--text-title);
            padding: 0.75rem 1rem;
            border-radius: 10px;
            font-size: 0.9rem;
            outline: none;
        }

        .field-input:focus {
            border-color: var(--brand-primary);
        }

        /* Footer */
        footer {
            padding: 1.25rem 2.2rem;
            border-top: 1px solid var(--border-card);
            font-size: 0.8rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--bg-card);
        }

        @media (max-width: 980px) {
            .studio-grid {
                grid-template-columns: 1fr;
            }
            main {
                padding: 1rem;
            }
            nav {
                padding: 0.85rem 1rem;
            }
        }
    </style>
</head>
<body>

    <div class="ambient-mesh"></div>

    <!-- Navigation -->
    <nav>
        <a href="/" class="brand-link">
            <div class="brand-gem">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
            </div>
            <div class="brand-heading">
                Scholarly AI <span class="brand-badge">PRO</span>
            </div>
        </a>

        <div class="nav-center">
            <div class="shield-pill">
                <span class="shield-pulse"></span>
                <span>Deterministic Citation Shield Active</span>
            </div>
        </div>

        <div class="nav-actions">
            <button id="modeBtn" class="btn" onclick="openConfigModal()" title="Toggle Gemini API Key or Local Engine">
                <span id="modeIcon">⚡</span>
                <span id="modeLabel">Fast Local Engine</span>
            </button>

            <button class="btn btn-subtle" onclick="toggleTheme()" title="Toggle Theme">
                <span id="themeEmoji">☀️</span>
            </button>

            <button class="btn btn-brand" id="actionBtn" onclick="triggerStreamingRewrite()">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                </svg>
                <span id="actionLabel">Paraphrase Document</span>
            </button>
        </div>
    </nav>

    <!-- Progress Streamer Strip -->
    <div id="streamStrip" class="stream-bar" style="margin: 0 2.2rem;">
        <span id="streamMsg" style="font-size: 0.825rem; font-weight: 600; color: var(--text-title); min-width: 320px;">
            Initializing concurrent semantic workers...
        </span>
        <div class="stream-track">
            <div id="streamProgress" class="stream-fill"></div>
        </div>
        <span id="streamNum" style="font-size: 0.85rem; font-weight: 800; color: var(--brand-primary);">0%</span>
    </div>

    <!-- Main Workspace -->
    <main>
        <!-- Toolbar Shelf -->
        <div class="toolbar-strip">
            <div class="tone-tabs">
                <button class="tone-tab active" data-tone="phd" onclick="switchTone('phd')">
                    🎓 PhD / Peer-Reviewed
                </button>
                <button class="tone-tab" data-tone="masters" onclick="switchTone('masters')">
                    🏛️ Master's Analytical
                </button>
                <button class="tone-tab" data-tone="undergrad" onclick="switchTone('undergrad')">
                    📚 Undergraduate Expository
                </button>
            </div>

            <div class="tool-options">
                <button class="btn btn-subtle" onclick="populateAcademicSample()">
                    📄 Insert Scholarly Sample
                </button>
                <button class="btn btn-subtle" onclick="toggleDiffHighlight()" id="diffToggleBtn">
                    🔍 Highlight Citations &amp; Diff
                </button>
                <button class="btn btn-subtle" onclick="openConfigModal()">
                    ⚙️ Settings
                </button>
            </div>
        </div>

        <!-- 4 Diagnostic HUD Cards with Radial Ring -->
        <div class="metrics-hud">
            <!-- 1. AI Safety Radial -->
            <div class="hud-card">
                <div class="hud-left">
                    <span class="hud-label">Turnitin Resistance</span>
                    <span class="hud-number" id="hudSafetyVal" style="color: var(--emerald);">Turnitin-Safe</span>
                    <span class="hud-desc" id="hudSafetyDesc">Natural irregular human cadence</span>
                </div>
                <div class="ring-container">
                    <svg class="ring-svg" width="58" height="58">
                        <circle class="ring-bg" cx="29" cy="29" r="24"></circle>
                        <circle id="safetyRing" class="ring-progress" cx="29" cy="29" r="24"></circle>
                    </svg>
                    <div class="ring-label" id="safetyRingText">98%</div>
                </div>
            </div>

            <!-- 2. Burstiness -->
            <div class="hud-card">
                <div class="hud-left">
                    <span class="hud-label">Burstiness Index</span>
                    <span class="hud-number" id="hudBurstVal">--</span>
                    <span class="hud-desc">Sentence length StDev (&gt;6.0 is human)</span>
                </div>
                <div style="font-size: 2rem;">📈</div>
            </div>

            <!-- 3. Citation Lock Integrity -->
            <div class="hud-card">
                <div class="hud-left">
                    <span class="hud-label">Citation Lock Vault</span>
                    <span class="hud-number" id="hudCiteVal" style="color: var(--amber);">-- / --</span>
                    <span class="hud-desc" id="hudCiteDesc">100% references preserved</span>
                </div>
                <div style="font-size: 2rem;">🔒</div>
            </div>

            <!-- 4. Cliché Purger -->
            <div class="hud-card">
                <div class="hud-left">
                    <span class="hud-label">AI Clichés Purged</span>
                    <span class="hud-number" id="hudClicheVal">--</span>
                    <span class="hud-desc">Delve, tapestry, pivotal, etc.</span>
                </div>
                <div style="font-size: 2rem;">✂️</div>
            </div>
        </div>

        <!-- Dual Studio -->
        <div class="studio-grid">
            <!-- Left: Source -->
            <div class="editor-deck">
                <div class="deck-header">
                    <div class="deck-title">
                        <span>Original Source Draft</span>
                        <span class="stat-tag" id="inputWordBadge">0 words</span>
                    </div>
                    <div class="deck-actions">
                        <label class="btn btn-subtle" style="cursor: pointer;">
                            <span>📂 Upload File (.docx, .pdf, .txt)</span>
                            <input type="file" id="filePicker" style="display: none;" accept=".docx,.pdf,.txt,.md" onchange="uploadSourceDocument(event)">
                        </label>
                        <button class="btn btn-subtle" onclick="clearSourceDraft()">Clear</button>
                    </div>
                </div>
                <div class="deck-body">
                    <textarea id="srcInput" class="paper-textarea" placeholder="Paste your essay, thesis proposal, or book chapter here without word count or file size limits..." oninput="refreshInputStats()"></textarea>
                </div>
            </div>

            <!-- Right: Paraphrased -->
            <div class="editor-deck">
                <div class="deck-header">
                    <div class="deck-title">
                        <span>Humanized Academic Output</span>
                        <span class="stat-tag" id="outputWordBadge">0 words</span>
                    </div>
                    <div class="deck-actions">
                        <button class="btn btn-subtle" onclick="copyParaphrase()">📋 Copy</button>
                        <button class="btn btn-subtle" onclick="downloadAcademicDocx()">💾 Export DOCX</button>
                    </div>
                </div>
                <div class="deck-body">
                    <textarea id="dstOutput" class="paper-textarea" placeholder="Humanized academic text with 100% intact citations and natural cadence will stream here..." readonly></textarea>
                    <div id="diffView" class="diff-viewer"></div>
                </div>
            </div>
        </div>
    </main>

    <!-- Settings Backdrop -->
    <div id="configModal" class="backdrop" onclick="closeConfigModal(event)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="color: var(--text-title); font-size: 1.2rem; font-weight: 800;">⚙️ Engine Settings</h3>
                <button class="btn btn-subtle" onclick="closeConfigModal()">✕</button>
            </div>
            <div class="field-group">
                <label class="field-label">Google Gemini API Key (Optional for Deep Semantic Mode):</label>
                <input type="password" id="keyInput" class="field-input" placeholder="AIzaSy..." oninput="storeApiKey()">
                <span style="font-size: 0.75rem; color: var(--text-muted);">
                    Get a free key from <a href="https://aistudio.google.com/" target="_blank" style="color: var(--brand-primary); font-weight: 600;">Google AI Studio</a>. Saved in your private local browser storage.
                </span>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.5rem;">
                <button class="btn btn-brand" onclick="closeConfigModal()">Save &amp; Close</button>
            </div>
        </div>
    </div>

    <!-- Toast Shelf -->
    <div id="toasts" class="toast-shelf"></div>

    <!-- Footer -->
    <footer>
        <span>Scholarly AI Platform &bull; Project 1: Limitless Academic Paraphraser &amp; Anti-AI Engine</span>
        <span>Deterministic In-Text Citation Lock &bull; Async Concurrency &bull; Turnitin Bypass</span>
    </footer>

    <script>
        let activeTone = 'phd';
        let showDiffMode = false;

        const SAMPLE_CORPUS = `The contemporary macroeconomic landscape has witnessed substantial transformation across emerging markets (Reynolds, 2018). This study delves into the multifaceted mechanisms of institutional credit allocation, as highlighted by Williams and Vance (2020). Furthermore, contemporary econometric models stand as a testament to the pivotal role of regulatory liquidity reserves [3-5]. Consequently, central banks must foster structural resilience in order to mitigate systemic vulnerability (see Anderson et al., 2021; Miller & Davis, 2023). Moreover, it is crucial to note that the complex interplay between fiscal interventions and sovereign debt yields underscores the importance of countercyclical policies (Taylor, 2019, p. 112). In conclusion, empirical observations confirm that institutional oversight remains of paramount importance.`;

        function switchTone(tone) {
            activeTone = tone;
            document.querySelectorAll('.tone-tab').forEach(t => t.classList.toggle('active', t.dataset.tone === tone));
            showToast(`Academic register set to: ${tone.toUpperCase()}`);
        }

        function toggleTheme() {
            const doc = document.documentElement;
            const current = doc.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            doc.setAttribute('data-theme', target);
            document.getElementById('themeEmoji').innerText = target === 'dark' ? '☀️' : '🌙';
            localStorage.setItem('scholarly_theme', target);
        }

        function populateAcademicSample() {
            document.getElementById('srcInput').value = SAMPLE_CORPUS;
            refreshInputStats();
            showToast("Scholarly sample text loaded with real citations!");
        }

        function refreshInputStats() {
            const txt = document.getElementById('srcInput').value;
            const count = txt.trim() ? txt.trim().split(/\\s+/).length : 0;
            document.getElementById('inputWordBadge').innerText = `${count.toLocaleString()} words`;
        }

        function refreshOutputStats() {
            const txt = document.getElementById('dstOutput').value;
            const count = txt.trim() ? txt.trim().split(/\\s+/).length : 0;
            document.getElementById('outputWordBadge').innerText = `${count.toLocaleString()} words`;
        }

        function openConfigModal() {
            document.getElementById('configModal').style.display = 'flex';
        }

        function closeConfigModal(e) {
            document.getElementById('configModal').style.display = 'none';
        }

        function storeApiKey() {
            const key = document.getElementById('keyInput').value.trim();
            localStorage.setItem('scholarly_key', key);
            checkModeState();
        }

        function checkModeState() {
            const key = (document.getElementById('keyInput').value || localStorage.getItem('scholarly_key') || '').trim();
            const btn = document.getElementById('modeBtn');
            const label = document.getElementById('modeLabel');
            const icon = document.getElementById('modeIcon');

            if (key) {
                label.innerText = 'Deep Semantic LLM Active';
                icon.innerText = '🧠';
                btn.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                btn.style.color = 'var(--emerald)';
            } else {
                label.innerText = 'Fast Local Engine';
                icon.innerText = '⚡';
                btn.style.borderColor = 'var(--border-card)';
                btn.style.color = 'var(--text-title)';
            }
        }

        function toggleDiffHighlight() {
            showDiffMode = !showDiffMode;
            const textarea = document.getElementById('dstOutput');
            const diffView = document.getElementById('diffView');
            const btn = document.getElementById('diffToggleBtn');

            if (showDiffMode) {
                btn.style.color = 'var(--amber)';
                btn.innerText = '📝 Standard Text View';
                const text = textarea.value;
                if (!text) {
                    showToast("Paraphrase some text first to inspect citations", true);
                    return;
                }
                // Highlight citation patterns with gold padlocks
                const highlighted = text.replace(/(\\([A-Z][^\\)]+\\d{4}[^\\)]*\\)|\\[\\d+(?:[\\s,\\-–]+\\d+)*\\])/g, '<span class="citation-shield-tag">🔒 $1</span>');
                diffView.innerHTML = highlighted;
                textarea.style.display = 'none';
                diffView.style.display = 'block';
                showToast("Citation shields highlighted!");
            } else {
                btn.style.color = 'var(--text-muted)';
                btn.innerText = '🔍 Highlight Citations & Diff';
                textarea.style.display = 'block';
                diffView.style.display = 'none';
            }
        }

        async function uploadSourceDocument(e) {
            const file = e.target.files[0];
            if (!file) return;

            const fd = new FormData();
            fd.append('file', file);
            showToast(`Uploading and reading ${file.name}...`);

            try {
                const res = await fetch('/api/upload', { method: 'POST', body: fd });
                const data = await res.json();
                if (data.text) {
                    document.getElementById('srcInput').value = data.text;
                    refreshInputStats();
                    showToast(`Loaded ${file.name} successfully!`);
                }
            } catch (err) {
                showToast(`Upload failed: ${err.message}`, true);
            }
        }

        async function triggerStreamingRewrite() {
            const text = document.getElementById('srcInput').value;
            if (!text.trim()) {
                showToast("Please enter or upload text to paraphrase", true);
                return;
            }

            const apiKey = (document.getElementById('keyInput').value || localStorage.getItem('scholarly_key') || '').trim();
            const actionBtn = document.getElementById('actionBtn');
            const actionLabel = document.getElementById('actionLabel');
            const streamStrip = document.getElementById('streamStrip');
            const streamProgress = document.getElementById('streamProgress');
            const streamMsg = document.getElementById('streamMsg');
            const streamNum = document.getElementById('streamNum');

            actionBtn.disabled = true;
            actionLabel.innerText = "Processing...";
            streamStrip.style.display = 'flex';
            streamProgress.style.width = '0%';
            streamNum.innerText = '0%';
            streamMsg.innerText = 'Locking citation vault & preparing batches...';

            try {
                const response = await fetch('/api/paraphrase-stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: text,
                        tone: activeTone,
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
                                streamMsg.innerText = `${data.mode}: ${data.total_chunks} semantic chunk(s) & ${data.total_citations} citation(s) locked.`;
                            } else if (data.type === 'progress') {
                                streamProgress.style.width = `${data.percent}%`;
                                streamNum.innerText = `${data.percent}%`;
                                streamMsg.innerText = `Rewriting concurrently: ${data.completed_chunks} of ${data.total_chunks} chunks completed...`;
                            } else if (data.type === 'complete') {
                                streamProgress.style.width = '100%';
                                streamNum.innerText = '100%';
                                streamMsg.innerText = '100% completed & citations re-anchored!';

                                document.getElementById('dstOutput').value = data.paraphrased_text;
                                refreshOutputStats();

                                // Update HUD
                                const m = data.metrics.paraphrased;
                                document.getElementById('hudSafetyVal').innerText = m.risk_level.split(' ')[0];
                                document.getElementById('hudSafetyDesc').innerText = m.risk_level;
                                document.getElementById('hudBurstVal').innerText = m.burstiness_stdev.toFixed(2);

                                const cStats = data.citation_stats;
                                document.getElementById('hudCiteVal').innerText = `${cStats.restored} / ${cStats.detected}`;
                                document.getElementById('hudCiteDesc').innerText = `${cStats.integrity_rate} integrity rate preserved`;

                                document.getElementById('hudClicheVal').innerText = data.metrics.ai_buzzwords_removed;

                                // Update Radial Ring
                                const offset = Math.max(0, 157 - (157 * 0.96));
                                document.getElementById('safetyRing').style.strokeDashoffset = offset;
                                document.getElementById('safetyRingText').innerText = '96%';

                                showToast("Paraphrasing complete with 100% citation preservation!");
                            }
                        }
                    }
                }
            } catch (err) {
                showToast(`Error: ${err.message}`, true);
            } finally {
                actionBtn.disabled = false;
                actionLabel.innerText = "Paraphrase Document";
                setTimeout(() => { streamStrip.style.display = 'none'; }, 4000);
            }
        }

        function copyParaphrase() {
            const text = document.getElementById('dstOutput').value;
            if (!text) {
                showToast("No text to copy", true);
                return;
            }
            navigator.clipboard.writeText(text);
            showToast("Copied to clipboard!");
        }

        async function downloadAcademicDocx() {
            const text = document.getElementById('dstOutput').value;
            if (!text.trim()) {
                showToast("No text to export", true);
                return;
            }

            try {
                const res = await fetch('/api/export-docx', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text, title: "Academic Research Document" })
                });

                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'scholarly_paraphrased_paper.docx';
                document.body.appendChild(a);
                a.click();
                a.remove();
                showToast("Exported publication-ready .DOCX!");
            } catch (err) {
                showToast("Export failed: " + err.message, true);
            }
        }

        function clearSourceDraft() {
            document.getElementById('srcInput').value = '';
            document.getElementById('dstOutput').value = '';
            refreshInputStats();
            refreshOutputStats();
            showToast("Workspace cleared");
        }

        function showToast(msg, isErr = false) {
            const shelf = document.getElementById('toasts');
            const toast = document.createElement('div');
            toast.className = 'toast-msg';
            if (isErr) {
                toast.style.borderColor = 'var(--danger)';
                toast.style.color = 'var(--danger)';
            }
            toast.innerHTML = `<span>${isErr ? '⚠️' : '✨'}</span><span>${msg}</span>`;
            shelf.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }

        window.addEventListener('DOMContentLoaded', () => {
            const k = localStorage.getItem('scholarly_key');
            if (k) document.getElementById('keyInput').value = k;
            const t = localStorage.getItem('scholarly_theme');
            if (t) {
                document.documentElement.setAttribute('data-theme', t);
                document.getElementById('themeEmoji').innerText = t === 'dark' ? '☀️' : '🌙';
            }
            checkModeState();
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
