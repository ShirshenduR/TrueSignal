import os
import pickle
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

DB_PATH = "talent_pool.pkl"
# Load embedding model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_db() -> List[Dict[str, Any]]:
    """Loads the local persistent vector database."""
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading RAG DB: {e}")
            return []
    return []

def save_db(db: List[Dict[str, Any]]):
    """Saves the vector database array to disk."""
    with open(DB_PATH, "wb") as f:
        pickle.dump(db, f)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Splits resume text into overlapping windows for semantic embedding."""
    chunks = []
    start = 0
    text_len = len(text)
    
    if text_len == 0:
        return []
        
    while start < text_len:
        chunks.append(text[start:start+chunk_size])
        start += chunk_size - overlap
    return chunks

def ingest_to_db(candidate_name: str, resume_text: str):
    """Chunks the text, embeds into vectors, and saves to the local DB."""
    db = get_db()
    
    # Remove old chunks for this candidate if re-ingesting
    db = [entry for entry in db if entry["candidate"] != candidate_name]
    
    chunks = chunk_text(resume_text)
    if not chunks:
        return
        
    embeddings = model.encode(chunks)
    
    for chunk, emb in zip(chunks, embeddings):
        db.append({
            "candidate": candidate_name,
            "chunk": chunk,
            "embedding": emb
        })
        
    save_db(db)

def search_db(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Embeds the query and fetches the mathematically closest Resume chunks."""
    db = get_db()
    if not db:
        return []
    
    query_emb = model.encode([query])[0]
    
    db_embs = [entry["embedding"] for entry in db]
    sims = cosine_similarity([query_emb], db_embs)[0]
    
    results = []
    for idx, sim in enumerate(sims):
        results.append({
            "candidate": db[idx]["candidate"],
            "chunk": db[idx]["chunk"],
            "score": float(sim)
        })
        
    # Sort descending by cosine similarity score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Filter out extreme low relevance
    results = [r for r in results if r["score"] > 0.1]
    
    # Return Top K unique or duplicate candidate chunks
    return results[:top_k]

def query_rag_llm(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """Takes the retrieved vector chunks and asks Groq LLaMA-3 to synthesize an answer."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY environment variable is missing."
        
    client = Groq(api_key=api_key)
    
    # Assemble context string
    context = ""
    for idx, res in enumerate(retrieved_chunks):
        context += f"\n[Excerpt {idx+1} | Source: {res['candidate']} | Relevance: {res['score']:.2f}]\n{res['chunk']}\n"
        
    prompt = f"""
    You are an Enterprise HR Intelligence Assistant. You are equipped with a Retrieval-Augmented Generation (RAG) system.
    
    The hiring manager has searched the talent pool database with the following query:
    '{query}'
    
    The vector database successfully retrieved the following highest-scoring semantic excerpts from various candidate resumes:
    {context}
    
    Task:
    Analyze ONLY the retrieved context and synthesize a direct answer to the manager's query. 
    Point out specifically which candidates best fit the request based on the excerpts.
    If the context does not contain enough information to fully answer, state that clearly.
    Use markdown, and be extremely concise, analytical, and professional.
    """
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a specialized Enterprise HR Assistant equipped with a Retrieval-Augmented Generation Knowledge Base."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=800
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Groq API Error: {str(e)}"
