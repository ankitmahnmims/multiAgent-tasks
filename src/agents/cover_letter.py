import re
import pathlib
import tempfile
import uuid
from typing import Dict, Any
from .base import BaseAgent, AgentMessage
from ..utils.pdf_handler import save_cover_letter_pdf

class CoverLetterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CoverLetterAgent",
            system_prompt=(
                "You are an expert career storyteller and executive cover letter writer. "
                "Your style is persuasive, authentic, concise, and focused on connecting candidate "
                "achievements to company requirements. Avoid corporate jargon and clichés."
            )
        )

    def run(self, cv_text: str, job: Dict[str, str], candidate: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate a tailored cover letter text and PDF artifact.
        """
        prompt = f"""
First, perform an internal strategic analysis (do not include analysis in final output):
1. Deconstruct the Role: Identify the top 3 critical responsibilities & qualifications.
2. Map the Candidate: Connect specific projects, skills, or quantified metrics from the CV to those 3 requirements.
3. Establish Core Narrative: Formulate a clear value proposition.

Using your analysis, write the cover letter:
- Header: Include Candidate Contact Details ({candidate.get('name', 'Candidate')}, {candidate.get('email', '')}, {candidate.get('phone', '')}, {candidate.get('location', '')}) and Date.
- Opening: Hook the hiring manager and specify the role ({job.get('title_raw', 'Position')}).
- Body: 2 distinct paragraphs with concrete, quantified evidence showing how the candidate's achievements solve the company's needs.
- Closing: Professional, enthusiastic call to action.

Candidate CV:
{cv_text[:6000]}

Job Posting Details:
Title: {job.get('title_raw', '')}
URL: {job.get('url', '')}
Description: {job.get('description', '')[:4000]}

OUTPUT ONLY THE FULL FINAL COVER LETTER TEXT STARTING WITH THE CONTACT HEADER.
"""
        letter_text = self.call_openai([AgentMessage("user", prompt)], max_tokens=3000)

        # Generate downloadable PDF
        safe_name = re.sub(r"[^A-Za-z0-9]+", "_", candidate.get("name", "Candidate")).strip("_") or "Candidate"
        pdf_filename = f"{safe_name}_{uuid.uuid4().hex[:8]}_Cover_Letter.pdf"
        pdf_path = str(pathlib.Path(tempfile.gettempdir()) / pdf_filename)
        saved_pdf = save_cover_letter_pdf(letter_text, pdf_path)

        return {
            "letter": letter_text,
            "pdf_path": saved_pdf
        }

    def revise(self, original_letter: str, feedback: str, cv_text: str, job: Dict[str, str], candidate: Dict[str, str]) -> str:
        """
        Revise existing cover letter based on user feedback.
        """
        prompt = f"""
Revise the following cover letter to address the user's specific feedback while maintaining accuracy and impact.

User Feedback:
{feedback.strip() or "(Make it sharper and more tailored to the role)"}

Candidate CV:
{cv_text[:4000]}

Job Posting:
Title: {job.get('title_raw', '')}
Description: {job.get('description', '')[:2500]}

Original Cover Letter:
{original_letter}

OUTPUT ONLY THE REVISED FULL LETTER TEXT STARTING WITH THE CONTACT HEADER. NO COMMENTARY.
"""
        return self.call_openai([AgentMessage("user", prompt)], max_tokens=3000)
