import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def compute_match(jd_text: str, github_summary: str, resume_text: str, dsa_data: Dict[str, Any], taxonomy_list: List[str]) -> Dict[str, Any]:
    """
    Computes semantic similarity for GitHub and Resume documents against the JD.
    Applies score boosts based on validated computational algorithmic (DSA) strength.
    """
    model = load_model()
    
    texts_to_match = []
    if github_summary.strip():
        texts_to_match.append(github_summary)
    if resume_text.strip():
        texts_to_match.append(resume_text)
        
    if not texts_to_match:
         return {"match_score": 0, "extracted_skills": []}
         
    # Embed JD
    jd_emb = model.encode([jd_text])[0]
    
    # Calculate similarity for each source
    scores = []
    combined_text = github_summary + " " + resume_text
    
    for t in texts_to_match:
        t_emb = model.encode([t])[0]
        sim = cosine_similarity([jd_emb], [t_emb])[0][0]
        scores.append(max(0, float(sim)) * 100)
        
    base_match = round(sum(scores) / len(scores), 2)
    
    # Process DSA Boosts
    dsa_boost = 0
    lc = dsa_data.get("leetcode", {})
    cf = dsa_data.get("codeforces", {})
    
    if lc.get("total_solved", 0) > 50:
        dsa_boost += 5
    if cf.get("rating", 0) > 1200:
        dsa_boost += 5
        
    final_score = min(100, base_match + dsa_boost)
    final_score = round(final_score, 2)
    
    # Taxonomy tagging
    found_skills = []
    combined_lower = combined_text.lower()
    for skill in taxonomy_list:
        if skill.lower() in combined_lower:
            found_skills.append(skill)
            
    return {
        "match_score": final_score,
        "base_semantic_score": base_match,
        "dsa_boost": dsa_boost,
        "extracted_skills": list(set(found_skills))
    }
