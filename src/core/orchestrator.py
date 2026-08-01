from typing import Dict, Any, Optional
from ..agents.cover_letter import CoverLetterAgent
from ..agents.networking import NetworkingAgent
from ..agents.cv_review import CVReviewAgent
from ..utils.pdf_handler import extract_text_from_pdf
from ..utils.contact_sniffer import sniff_contact
from ..utils.scraper import scrape_job

class Orchestrator:
    def __init__(self):
        self.cover = CoverLetterAgent()
        self.net = NetworkingAgent()
        self.review = CVReviewAgent()

    def route(
        self,
        option: str,
        cv_pdf_path: str,
        job_url: str,
        jd_text_optional: str = ""
    ) -> Dict[str, Any]:
        """
        Route request to the target agent based on user selection.
        """
        cv_text = extract_text_from_pdf(cv_pdf_path)
        if not cv_text and jd_text_optional:
            # Fallback if text couldn't be extracted from PDF
            cv_text = "Candidate Profile"

        candidate = sniff_contact(cv_text)
        job = scrape_job(job_url)

        # Handle optional manual job description override if web scraper returns thin text
        if jd_text_optional and (job.get("is_thin") or len(job.get("description", "")) < 200):
            job["description"] = jd_text_optional
            job["is_thin"] = False

        opt = (option or "").lower().strip().replace(" ", "_")

        if opt in ["cover_letter", "coverletter"]:
            result = self.cover.run(cv_text=cv_text, job=job, candidate=candidate)
            return {
                "type": "cover_letter",
                "cv_text": cv_text,
                "job": job,
                "candidate": candidate,
                "letter": result["letter"],
                "pdf_path": result.get("pdf_path"),
                "messages": None,
                "review": None,
                "needs_jd_text": job.get("is_thin", False)
            }

        elif opt in ["networking", "outreach"]:
            msgs = self.net.run(cv_text=cv_text, job=job)
            return {
                "type": "networking",
                "cv_text": cv_text,
                "job": job,
                "candidate": candidate,
                "letter": None,
                "pdf_path": None,
                "messages": msgs,
                "review": None,
                "needs_jd_text": job.get("is_thin", False)
            }

        elif opt in ["cv_review", "review"]:
            rev = self.review.run(cv_text=cv_text, job=job)
            return {
                "type": "cv_review",
                "cv_text": cv_text,
                "job": job,
                "candidate": candidate,
                "letter": None,
                "pdf_path": None,
                "messages": None,
                "review": rev,
                "needs_jd_text": job.get("is_thin", False)
            }

        else:
            raise ValueError(f"Unknown option '{option}'. Choose from: cover_letter, networking, cv_review.")
