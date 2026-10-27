"""
document_io.py - File Ingestion & Export Engine
Handles DOCX, PDF, and TXT files for limitless size processing.
"""

import io
from typing import Tuple
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader

class DocumentIO:
    """
    Ingests and exports multi-format documents.
    """

    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
        """
        Extracts clean plain text from DOCX, PDF, or TXT binary buffers.
        """
        filename_lower = filename.lower()

        if filename_lower.endswith('.docx'):
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)

        elif filename_lower.endswith('.pdf'):
            reader = PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for page in reader.pages:
                t = page.extract_text()
                if t and t.strip():
                    pages_text.append(t.strip())
            return "\n\n".join(pages_text)

        elif filename_lower.endswith('.txt') or filename_lower.endswith('.md'):
            return file_bytes.decode('utf-8', errors='replace')

        else:
            # Fallback text decode
            return file_bytes.decode('utf-8', errors='replace')

    @staticmethod
    def create_academic_docx(text: str, title: str = "Paraphrased Academic Document") -> bytes:
        """
        Creates a clean, university-grade styled Word Document (.docx).
        - 1-inch margins
        - Times New Roman, 12pt
        - Double or 1.5 line spacing
        - Paragraph indentation
        """
        doc = Document()

        # Page setup: 1-inch margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Title
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(title)
        title_run.font.name = 'Times New Roman'
        title_run.font.size = Pt(16)
        title_run.bold = True
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_p.paragraph_format.space_after = Pt(18)

        # Body paragraphs
        paragraphs = text.split("\n\n")
        for para in paragraphs:
            para_clean = para.strip()
            if not para_clean:
                continue

            p = doc.add_paragraph()
            # Check if this paragraph looks like a section header
            if len(para_clean) < 80 and not para_clean.endswith('.'):
                run = p.add_run(para_clean)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(13)
                run.bold = True
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
            else:
                run = p.add_run(para_clean)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
                p.paragraph_format.line_spacing = 1.5
                p.paragraph_format.space_after = Pt(8)

        out_io = io.BytesIO()
        doc.save(out_io)
        out_io.seek(0)
        return out_io.getvalue()
