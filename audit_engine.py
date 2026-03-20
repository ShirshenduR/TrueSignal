import os
import json
from groq import Groq
from typing import Dict, Any

def anonymize_text(text: str) -> str:
    """
    Uses Groq to proactively strip PII, demographics, gender, universities, and locations from text.
    Returns the sanitized text.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or not text.strip():
        return text

    client = Groq(api_key=api_key)
    
    system_prompt = """You are a strict Anonymization & Anti-Bias text processor.
Rewrite the input text to completely REMOVE any mention of:
- Candidate Names
- Gender (use gender-neutral terms)
- Universities, Colleges, or Educational Institutions
- Geographic Locations
- Any other demographic markers.

Preserve ONLY the technical skills, metrics, job titles, and professional achievements.
Do NOT add any opening remarks, tags, or markdown formatting. Output ONLY the sanitized text."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Anonymization Error: {e}")
        return text

def generate_glassbox_audit(jd_text: str, candidate_dossier: str, match_score: float) -> Dict[str, Any]:
    """
    Calls the Groq API with a strict system prompt forcing a JSON output.
    Evaluates the total combined dossier (GitHub + Resume + DSA data).
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"bias_check_status": "Failed", "justification": "GROQ_API_KEY environment variable is missing for the AI Audit."}

    client = Groq(api_key=api_key)
    
    system_prompt = """You are an AI Talent Analyst evaluating a candidate's complete technical dossier (GitHub commits, Resume, and DSA scores) against a Job Description.
Provide a strict JSON response.
Schema Required:
{
  "confidence_score": <integer from 0 to 100>,
  "skill_justifications": [
      {"skill": "Skill Name", "score_out_of_10": <int>, "reasoning": "'We believe this candidate has this skill because...' (Reference specific repos, DSA stats, or resume lines)"}
  ],
  "critical_skills_missing": [<list of strings>],
  "code_quality_assessment": "Short sentence evaluating commit message quality and algorithmic capability.",
  "hr_deep_analysis": "Detailed 3-sentence Senior HR perspective analyzing career trajectory, project scale/impact, and true seniority indicators.",
  "bias_check_status": "Strict Anonymization Applied" or "Not Applied",
  "justification": "<A crisp, 2-sentence explanation of the match>"
}"""

    user_prompt = f"""
Job Description:
{jd_text}

Candidate Dossier (Sanitized):
{candidate_dossier}

Math Match Score: {match_score}%
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Groq API Error: {e}")
        return {
            "bias_check_status": "API Failed",
            "justification": f"Glass-Box AI Generation failed due to API Error: {e}",
            "hr_deep_analysis": "Unavailable.",
            "code_quality_assessment": "Unavailable.",
            "critical_skills_missing": [],
            "skill_justifications": []
        }
