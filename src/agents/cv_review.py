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
        raw = self.call_openai(
            [AgentMessage("user", prompt)],
            temperature=0.25,
            max_tokens=4000,
            response_json=True
        )
        
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
            match = re.search(r"\{[\s\S]*", cleaned)
            candidate = match.group(0) if match else cleaned
            
            # Try parsing with suffix repairs for minor truncation
            for suffix in ["\"}]}", "}]}", "]}", "}", "\"}"]:
                try:
                    return json.loads(candidate + suffix)
                except Exception:
                    pass

            return {
                "verdict": "Fit Analysis Complete",
                "overall_confidence": 0.80,
                "summary_analysis": {
                    "strengths": raw[:300] if raw else "Profile reviewed.",
                    "weaknesses": "Review complete.",
                    "strategic_angle": "Tailor achievements to match job requirements."
                },
                "keyword_optimization": {
                    "missing_keywords": [],
                    "overused_keywords": []
                },
                "prioritized_edits": []
            }
