import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import math
import re

def compute_shannon_entropy(language_dict: Dict[str, int]) -> tuple:
    """Computes Shannon Entropy to mathematically determine if a candidate is a Specialist or Generalist."""
    if not language_dict:
        return 0.0, "Unknown"
        
    total_bytes = sum(language_dict.values())
    if total_bytes == 0:
        return 0.0, "Unknown"
    
    entropy = 0.0
    for lang, bytes_count in language_dict.items():
         p = bytes_count / total_bytes
         if p > 0:
             entropy -= p * math.log2(p)
             
    entropy = round(entropy, 2)
    if entropy < 1.0:
        label = "Deep Specialist"
    elif entropy < 2.0:
        label = "Versatile Developer"
    else:
        label = "Broad Generalist"
        
    return entropy, label

def compute_jaccard_similarity(text1: str, text2: str) -> float:
    """Computes exact keyword overlap using Jaccard Similarity (Deterministic)."""
    def get_words(text):
        return set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
    
    set1 = get_words(text1)
    set2 = get_words(text2)
    if not set1 or not set2:
         return 0.0
    
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    if len(union) == 0:
        return 0.0
    return round((len(intersection) / len(union)) * 100, 2)

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
    
    # Process Verification Multipliers & DSA Boosts (Anti-Fake System)
    dsa_boost = 0
    lc = dsa_data.get("leetcode", {})
    cf = dsa_data.get("codeforces", {})
    
    total_solved = lc.get("total_solved", 0) if lc else 0
    rating = cf.get("rating", 0) if cf else 0
    
    # 1. Massive boosts for verified algorithmic skills
    if total_solved > 0:
        dsa_boost += 15 + (min(total_solved, 300) / 20)  # Up to +30 boost
    if rating > 0:
        dsa_boost += 15 + (min(rating, 2000) / 100)      # Up to +35 boost
        
    # 2. Unverified Resume Penalty ("Anti-Fake" Multiplier)
    has_github = len(github_summary.strip()) > 50
    has_dsa = total_solved > 0 or rating > 0
    
    penalty_multiplier = 1.0
    if not has_github and not has_dsa:
        penalty_multiplier = 0.4  # 60% penalty for completely unverified candidates
    elif not has_dsa:
        penalty_multiplier = 0.75 # 25% penalty for missing algorithmic verification
        
    final_score = (base_match * penalty_multiplier) + dsa_boost
    final_score = round(min(100.0, final_score), 2)
    
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
