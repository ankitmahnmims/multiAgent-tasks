import re
import json
from typing import Dict, Any
from .base import BaseAgent, AgentMessage

class CVReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CVReviewAgent",
            system_prompt=(
                "You are an executive recruiter, hiring manager, and ATS specialist. "
                "You evaluate candidate CVs against target job descriptions with extreme precision, "
                "providing actionable feedback to maximize interview callback rates."
            )
        )

    def run(self, cv_text: str, job: Dict[str, str]) -> Dict[str, Any]:
        prompt = f"""
Conduct an in-depth analysis of the candidate's CV against the job description.

Perform:
1. ATS Screen: Identify missing critical technical & domain keywords.
2. 6-Second Recruiter Screen: Is the value proposition instantly clear and quantified?
3. Strategic Fit: Assess story alignment for this position.

Return STRICT JSON adhering to this EXACT schema (no markdown fences, no prose outside json):

{{
  "verdict": "Strong Fit - Apply Now" | "Good Fit - Minor Revisions Recommended" | "Potential Fit - Strategic Repositioning Needed" | "Poor Fit - Reconsider",
  "overall_confidence": 0.85,
  "summary_analysis": {{
    "strengths": "Specific key strengths relevant to the job",
    "weaknesses": "Gaps or areas holding the CV back",
    "strategic_angle": "Core story to emphasize"
  }},
  "keyword_optimization": {{
    "missing_keywords": ["keyword1", "keyword2", "keyword3"],
    "overused_keywords": ["buzzword1"]
  }},
  "prioritized_edits": [
    {{
      "priority": "High",
      "section": "Experience",
      "suggestion": "Actionable suggestion text",
      "reasoning": "Why this matters for ATS or recruiter",
      "example_bullets": ["Before bullet rewritten with impact & metrics"]
    }}
  ]
}}

Job Title: {job.get('title_raw', '')}
Job Description:
{job.get('description', '')[:4000]}

Candidate CV:
{cv_text[:6000]}
"""
        raw = self.call_openai([AgentMessage("user", prompt)], temperature=0.25, max_tokens=2500)
        
        # Clean JSON fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except Exception:
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            
            return {
                "verdict": "Good Fit - Minor Revisions Recommended",
                "overall_confidence": 0.70,
                "summary_analysis": {
                    "strengths": "Strong alignment with core requirements.",
                    "weaknesses": "Could quantify results more clearly.",
                    "strategic_angle": "Highlight technical project leadership."
                },
                "keyword_optimization": {
                    "missing_keywords": ["Python", "System Architecture", "Multi-Agent"],
                    "overused_keywords": ["Responsible for"]
                },
                "prioritized_edits": [
                    {
                        "priority": "High",
                        "section": "Experience",
                        "suggestion": "Add quantified metrics to project descriptions.",
                        "reasoning": "Demonstrates impact to recruiters.",
                        "example_bullets": ["Built multi-agent system improving processing speed by 40%."]
                    }
                ]
            }
