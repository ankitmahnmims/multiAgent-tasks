import re
import pathlib
import tempfile
import uuid
from typing import Dict, Any
from ..agents.cover_letter import CoverLetterAgent
from ..agents.networking import NetworkingAgent
from ..utils.pdf_handler import save_cover_letter_pdf

class ReviewCoordinator:
    def __init__(self, cover_agent: CoverLetterAgent, net_agent: NetworkingAgent):
        self.cover = cover_agent
        self.net = net_agent

    def handle(self, state: Dict[str, Any], satisfaction: str, feedback: str) -> Dict[str, Any]:
        """
        Process user feedback:
        - If satisfaction is 'Yes', mark done=True.
        - If satisfaction is 'No' (or anything else), call .revise() on the active agent.
        """
        if not state or not state.get("type"):
            return {**(state or {}), "status_message": "Please run a generator task first.", "done": False}

        sat_lower = (satisfaction or "").strip().lower()
        if any(kw in sat_lower for kw in ["yes", "y", "satisfied", "looks good", "approved"]):
            return {**state, "status_message": "✅ Output approved and saved!", "done": True}

        fb = (feedback or "").strip() or "Please make it clearer, more compelling, and better tailored."

        try:
            state_type = state.get("type")

            if state_type == "cover_letter":
                revised_letter = self.cover.revise(
                    original_letter=state.get("letter", ""),
                    feedback=fb,
                    cv_text=state.get("cv_text", ""),
                    job=state.get("job", {}),
                    candidate=state.get("candidate", {})
                )

                safe_name = re.sub(r"[^A-Za-z0-9]+", "_", state.get("candidate", {}).get("name", "Candidate")).strip("_") or "Candidate"
                pdf_filename = f"{safe_name}_{uuid.uuid4().hex[:8]}_Cover_Letter.pdf"
                pdf_path = str(pathlib.Path(tempfile.gettempdir()) / pdf_filename)
                saved_pdf = save_cover_letter_pdf(revised_letter, pdf_path)

                return {
                    **state,
                    "letter": revised_letter,
                    "pdf_path": saved_pdf,
                    "status_message": "🔁 Cover Letter revised per your feedback!",
                    "done": False
                }

            elif state_type == "networking":
                revised_msgs = self.net.revise(
                    original_msgs=state.get("messages", {}),
                    feedback=fb,
                    cv_text=state.get("cv_text", ""),
                    job=state.get("job", {}),
                    candidate_name=state.get("candidate", {}).get("name", "Candidate")
                )

                return {
                    **state,
                    "messages": revised_msgs,
                    "status_message": "🔁 Networking outreach messages revised per your feedback!",
                    "done": False
                }

            else:
                return {**state, "status_message": "Revision complete.", "done": True}

        except Exception as e:
            return {
                **state,
                "status_message": f"⚠️ Revisions encountered an issue: {e}",
                "done": False
            }
