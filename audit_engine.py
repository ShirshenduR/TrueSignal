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

CRITICAL: Do not remove technical skills, programming languages, or framework names as they are the basis for technical evaluation. Preserve ONLY the technical skills, metrics, job titles, and professional achievements.
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
    
    system_prompt = """You are a Senior AI Talent Architect evaluating a candidate's complete technical dossier.
CRITICAL RULES FOR MASTERY INFERENCE:
1. FOUNDATIONAL MASTERY: If a candidate has built a foundational technology from scratch (e.g., a Transformer/nanoGPT, an Autograd engine/micrograd, or a C-based LLM stack/llm.c), they are a VERIFIED EXPERT (10/10) in all underlying sub-skills (Backpropagation, GPU Kernels, Tokenization, Loss Functions, etc.).
2. DO NOT PENALIZE FOR ABSENCE: If a candidate has demonstrated the 'Whole' of a complex system, do NOT use phrases like 'not explicitly shown' for its components. Assume mastery.
3. RESUME IS TRUTH FOR SENIORITY: Use the Resume for years of experience. Use GitHub (sorted by impact/stars) and DSA for deep verification.
4. EVIDENCE-BASED ONLY: Only claim a skill is 'missing' if it is a JD requirement and is absent from BOTH the Resume and all OSINT sources.
5. FIRST-PRINCIPLES REASONING (DYNAMIC):
   Analyze if a project (Repo) is a "First-Principles" implementation of a complex algorithm, framework, or system. 
   If a candidate has built the "Whole" of a complex architecture from scratch, they are a VERIFIED EXPERT (10/10) in every single constituent sub-skill required to make that architecture work (e.g. Backprop, low-level math, hardware optimization, etc.). 
6. DYNAMIC EXCLUSION RULE: If a skill is a foundational component of a project the candidate has already built, it MUST NEVER appear in 'critical_skills_missing'. Trust the architectural depth over the lack of specific keywords.
7. TOOLING EXCLUSION: Tooling like VS Code, Postman, or Git are industry standards; only flag them as missing if they are explicitly mentioned as mandatory in the JD and are nowhere in the dossier.
8. EVIDENCE-BASED ONLY (STRICTOR): If a skill is listed in the 'TECHNICAL SKILLS' section of the Resume or is used in any GitHub repo, it MUST NOT be marked missing.

Provide a strict JSON response.
Schema Required:
{
  "confidence_score": <int 0-100>,
  "skill_justifications": [
      {"skill": "Skill Name", "score_out_of_10": <int>, "reasoning": "Reference specific high-impact repos or resume lines. Use First-Principles Reasoning to verify constituent skills."}
  ],
  "critical_skills_missing": [<list of strings>],
  "code_quality_assessment": "Short sentence on commit quality and architectural impact.",
  "hr_deep_analysis": "3-sentence Senior HR perspective. Focus on trajectory and industry-level impact. Do not speculate on 'missing' skills.",
  "bias_check_status": "Strict Anonymization Applied",
  "justification": "<A crisp explanation of the match based on proven impact and first-principles mastery.>"
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
