# TrueSignal ⚡
**Semantic Talent Intelligence & OSINT Verification Engine**

TrueSignal is a production-grade hiring intelligence platform designed to eliminate "Resume Inflation" by verifying candidate claims against real-world digital footprints. Built for a high-intensity hackathon, it leverages semantic search, competitive programming APIs, and Large Language Models (LLMs) to provide an ungameable audit of technical talent.

---

## 🚀 Core Features

### 1. Holistic OSINT Verification 🔍
TrueSignal doesn't just read resumes; it verifies them. It cross-references PDF claims against:
- **GitHub**: Evaluates repository distribution, commit density, and code quality.
- **LeetCode & Codeforces**: Fetches live competitive programming stats to verify algorithmic proficiency.
- **Identity Verification**: Flags discrepancies between resume links and provided social handles.

### 2. Glass-Box Audit (AI Reasoning) 🧠
Traditional matching is a "black box." TrueSignal provides a **Glass-Box Audit** powered by **Groq LLaMA-3**:
- **HR Deep Analysis**: Career trajectory and mentorship potential evaluation.
- **Verified Skills Justification**: Each score is backed by specific evidence found in OSINT or the resume.
- **Critical Gaps**: Identifies exactly what the candidate is missing relative to the Job Description.

### 3. Enterprise RAG Talent Pool 📚
Store and query your entire applicant history semantically.
- **Persistent Vector Store**: Uses `SentenceTransformers` to index candidates.
- **Chat with your DB**: Ask questions like *"Who in our database has the strongest AWS experience?"* to retrieve the top matches instantly.

### 4. Zero-Mock Architecture 🛡️
- **No Hallucinations**: All fallback "mock data" has been removed. If a candidate cannot be verified, the system applies a **deterministic penalty** rather than inventing a score.
- **Anti-Bias Engine**: Aggressive anonymization strips names, gender, and demographics before the AI evaluates technical merit.

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **Intelligence**: Groq API (LLaMA-3.3 70B), Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Data Ingestion**: GitHub API, Codeforces API, LeetCode (GraphQL)
- **Vector Logic**: Scikit-Learn (Cosine Similarity), Chunking & Overlap RAG
- **Reporting**: FPDF-based automated audit export

---

## 📦 Installation & Setup

1. **Clone & Navigate**
   ```bash
   git clone <repo-url>
   cd TrueSignal
   ```

2. **Environment Configuration**
   Create a `.env` file in the root:
   ```env
   GITHUB_TOKEN="your_github_token"
   GROQ_API_KEY="your_groq_api_key"
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch**
   ```bash
   streamlit run app.py
   ```

---

## 🛡️ Anti-Fake & Verification
TrueSignal implements a strict **Anti-Fake Multiplier**. Candidates with **zero verifiable OSINT footprint** (no GitHub, no LeetCode, no Codeforces) are penalized by **up to 60%**, surfacing only those who demonstrate their skills in the real world.