import os
import unittest
import pathlib
import tempfile

from src.utils.pdf_handler import extract_text_from_pdf, save_cover_letter_pdf
from src.utils.contact_sniffer import sniff_contact
from src.utils.scraper import scrape_job
from src.agents.base import BaseAgent, AgentMessage
from src.agents.cover_letter import CoverLetterAgent
from src.agents.networking import NetworkingAgent
from src.agents.cv_review import CVReviewAgent
from src.core.orchestrator import Orchestrator
from src.core.coordinator import ReviewCoordinator

class TestMultiAgentSystem(unittest.TestCase):

    def test_contact_sniffer(self):
        cv = """Ankit Sharma
ankit.sharma@example.com
+1 (555) 019-2834
San Francisco, CA

Senior AI Engineer with 5 years experience.
        """
        contact = sniff_contact(cv)
        self.assertEqual(contact["name"], "Ankit Sharma")
        self.assertEqual(contact["email"], "ankit.sharma@example.com")
        self.assertEqual(contact["phone"], "+1 (555) 019-2834")
        self.assertEqual(contact["location"], "San Francisco, CA")

    def test_pdf_handler_save(self):
        letter_text = """Ankit Sharma
ankit@example.com

Hiring Manager
Tech Corp

Dear Hiring Manager,

I am writing to express my strong interest in the Senior AI Engineer role...

Sincerely,
Ankit
        """
        pdf_path = save_cover_letter_pdf(letter_text)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(pdf_path.endswith(".pdf") or pdf_path.endswith(".txt"))

    def test_networking_fallback(self):
        agent = NetworkingAgent()
        fallbacks = agent._fallback_messages("https://example.com/job")
        self.assertIn("referral_request", fallbacks)
        self.assertIn("cold_email", fallbacks)

    def test_orchestrator_initialization(self):
        orchestrator = Orchestrator()
        self.assertIsNotNone(orchestrator.cover)
        self.assertIsNotNone(orchestrator.net)
        self.assertIsNotNone(orchestrator.review)

    def test_review_coordinator_satisfaction(self):
        cover = CoverLetterAgent()
        net = NetworkingAgent()
        coord = ReviewCoordinator(cover, net)
        
        state = {"type": "cover_letter", "letter": "Original Letter"}
        res = coord.handle(state, "Yes - Satisfied", "")
        self.assertTrue(res.get("done"))
        self.assertIn("approved", res.get("status_message").lower())

if __name__ == "__main__":
    unittest.main()
