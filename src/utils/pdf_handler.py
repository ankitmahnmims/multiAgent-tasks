import os
import pathlib
import tempfile
import uuid
from typing import Optional

def extract_text_from_pdf(pdf_file_path: str) -> str:
    """
    Extract text content from a PDF file.
    Supports file path string or file-like object.
    """
    if not pdf_file_path or not os.path.exists(pdf_file_path):
        return ""
    
    text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"[PDF Extractor Warning] Failed reading with pypdf: {e}")
        try:
            # Fallback for plain text files passed as pdf
            with open(pdf_file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            pass
            
    return text.strip()


def save_cover_letter_pdf(letter_text: str, output_path: Optional[str] = None) -> str:
    """
    Convert letter text into a formatted PDF document using ReportLab.
    Returns the absolute path to the generated PDF.
    """
    if not output_path:
        safe_dir = tempfile.gettempdir()
        filename = f"Cover_Letter_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(safe_dir, filename)

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        # Custom styles for clean, professional typography
        body_style = ParagraphStyle(
            'CoverLetterBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor('#222222'),
            spaceAfter=10
        )
        
        header_style = ParagraphStyle(
            'CoverLetterHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#111111'),
            spaceAfter=12
        )

        story = []
        lines = letter_text.strip().split('\n')
        
        # First few lines treated as header/contact block
        is_header = True
        for line in lines:
            line_str = line.strip()
            if not line_str:
                story.append(Spacer(1, 6))
                is_header = False
                continue
                
            # Escape HTML characters for ReportLab Paragraph
            escaped = (line_str
                       .replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;'))
            
            if is_header and len(line_str) < 80:
                story.append(Paragraph(escaped, header_style))
            else:
                story.append(Paragraph(escaped, body_style))

        doc.build(story)
    except Exception as e:
        print(f"[PDF Generation Warning] Fallback text output due to ReportLab error: {e}")
        # Write text version if ReportLab is unavailable
        txt_path = output_path.replace(".pdf", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(letter_text)
        return txt_path

    return output_path
