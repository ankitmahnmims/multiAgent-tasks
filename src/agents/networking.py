import re
import json
from typing import Dict, Any
from .base import BaseAgent, AgentMessage

class NetworkingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="NetworkingAgent",
            system_prompt=(
                "You are a principal networking & executive outreach strategist. "
                "Your objective is to craft high-conversion, relationship-first outreach messages "
                "for networking with employees or recruiters. Focus on advice/insight asks, not direct referral begging."
            )
        )

    @staticmethod
    def _safe_json(s: str) -> Dict[str, Any]:
        s = (s or "").strip()
        try:
            return json.loads(s)
        except Exception:
            pass
        match = re.search(r"\{[\s\S]*\}", s)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {}

    @staticmethod
    def _fallback_messages(job_url: str = "") -> Dict[str, str]:
        dm = (
            "Hi {{recipient_name}}, I'm exploring the {{role}} role at {{company}} ({{job_link}}). "
            "I've shipped results in similar technical problem spaces and would value your perspective. "
            "If you have 10-15 minutes this week, could I ask two focused questions about the team's engineering priorities? "
            "Happy to keep it brief. — {{your_name}}"
        )
        email = (
            "Subject: Quick question regarding {{role}} at {{company}}\n\n"
            "Hi {{recipient_name}},\n\n"
            "I'm preparing to apply for the {{role}} position at {{company}} ({{job_link}}). "
            "My experience aligns directly with the challenges your team is solving.\n\n"
            "Would you be open to a brief 10-minute chat, or answering two quick questions about the role's key success metrics? "
            "I will keep it concise and come prepared.\n\n"
            "Best regards,\n{{your_name}}"
        )
        return {"referral_request": dm, "cold_email": email}

    def run(self, cv_text: str, job: Dict[str, str], tone: str = "Professional & concise") -> Dict[str, Any]:
        prompt = f"""
Generate TWO relationship-first outreach messages for an employee or hiring manager at the target company:

1. LinkedIn DM ("referral_request"):
   - 4-10 sentences maximum. No Subject line.
   - High hook, candidate bridge, single low-friction CTA (advice/chat ask).

2. Cold Email ("cold_email"):
   - FIRST LINE MUST BE: "Subject: <compelling subject line>"
   - Body: 100-200 words max. Clear value hook & CTA.

Placeholders allowed: {{{{recipient_name}}}}, {{{{your_name}}}}, {{{{role}}}}, {{{{company}}}}, {{{{job_link}}}}.

Tone: {tone}

Context:
Candidate CV: {cv_text[:4000]}
Job Title: {job.get('title_raw', 'Target Role')}
Job Link: {job.get('url', '')}
Job Description: {job.get('description', '')[:3000]}

Return STRICT JSON ONLY (no markdown formatting around json, no commentary) with keys:
"referral_request": "<text>",
"cold_email": "Subject: ...\\n\\n<text>"
"""
        raw = self.call_openai([AgentMessage("user", prompt)], temperature=0.4, max_tokens=2000)
        parsed = self._safe_json(raw)
        
        dm = (parsed.get("referral_request") or "").strip()
        email = (parsed.get("cold_email") or "").strip()

        if not dm or not email:
            fallbacks = self._fallback_messages(job.get("url", ""))
            dm = dm or fallbacks["referral_request"]
            email = email or fallbacks["cold_email"]

        if not email.lower().startswith("subject:"):
            email = f"Subject: Question regarding {job.get('title_raw', 'Role')}\n\n" + email

        return {
            "referral_request": dm,
            "cold_email": email
        }

    def revise(self, original_msgs: Dict[str, str], feedback: str, cv_text: str, job: Dict[str, str], candidate_name: str) -> Dict[str, str]:
        prompt = f"""
Revise the outreach messages based on user feedback:

User Feedback: {feedback}
Candidate Name: {candidate_name}

Original Messages JSON:
{json.dumps(original_msgs, indent=2)}

Job Title: {job.get('title_raw', '')}
Job Description: {job.get('description', '')[:2500]}

Return STRICT JSON ONLY with keys "referral_request" and "cold_email".
"""
        raw = self.call_openai([AgentMessage("user", prompt)], max_tokens=1500)
        parsed = self._safe_json(raw)

        dm = (parsed.get("referral_request") or original_msgs.get("referral_request", "")).strip()
        email = (parsed.get("cold_email") or original_msgs.get("cold_email", "")).strip()

        return {
            "referral_request": dm,
            "cold_email": email
        }
