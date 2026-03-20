# TrueSignal ⚡

**Semantic Talent Intelligence & OSINT Verification Engine**

TrueSignal is a production-grade hiring intelligence platform designed to eliminate "Resume Inflation" by verifying candidate claims against real-world digital footprints. Built for a high-intensity hackathon, it leverages semantic search, competitive programming APIs, and Large Language Models (LLMs) to provide an ungameable audit of technical talent.

---

## 🚀 Core Features

### 1. Holistic OSINT Verification 🔍
TrueSignal doesn't just read resumes — it **verifies** them. It cross-references PDF claims against:
- **GitHub**: Evaluates repository distribution, commit density, and code quality via the PyGithub API.
- **LeetCode & Codeforces**: Fetches live competitive programming stats to verify algorithmic proficiency.
- **Identity Verification**: Flags discrepancies between resume-extracted links and user-provided social handles (OSINT cross-check).

### 2. Glass-Box Audit (AI Reasoning) 🧠
Traditional matching is a "black box." TrueSignal provides a **Glass-Box Audit** powered by **Groq LLaMA-3**:
- **HR Deep Analysis**: Career trajectory and mentorship potential evaluation.
- **Verified Skills Justification**: Each score is backed by specific evidence found in OSINT or resume artifacts.
- **Critical Gaps**: Identifies exactly what the candidate is missing relative to the Job Description.

### 3. Enterprise RAG Talent Pool 📚
Store and query your entire applicant history semantically.
- **Persistent Vector Store**: Uses `SentenceTransformers` to chunk, embed, and index candidate resumes.
- **Chat with your DB**: Ask questions like *"Who in our database has the strongest AWS experience?"* to retrieve top matches instantly via Retrieval-Augmented Generation.

### 4. Zero-Mock Architecture 🛡️
- **No Hallucinations**: All fallback "mock data" has been removed. If a candidate cannot be verified, the system applies a **deterministic penalty** rather than inventing a score.
- **Anti-Bias Engine**: Aggressive LLM-based anonymization strips names, gender, and demographics before the AI evaluates technical merit.

### 5. Batch Comparison Mode 📊
- Upload multiple resumes simultaneously.
- Auto-extract OSINT footprints (GitHub, LeetCode, Codeforces) from each PDF.
- Rank candidates deterministically on a competitive leaderboard with interactive score distribution charts.

---

## 🧬 Technical Architecture & Algorithms

### Matching Pipeline — `matching_algorithm.py`

TrueSignal's core matching engine uses a **three-layer scoring pipeline** that fuses semantic, deterministic, and verification signals:

#### Layer 1: Dense Vector Cosine Similarity (Semantic Match)

| Detail | Value |
|---|---|
| **Model** | `all-MiniLM-L6-v2` (384-dim embeddings, ~22M params) |
| **Metric** | Cosine Similarity |
| **Complexity** | O(d) per pair, where d = embedding dimension |

The Job Description and candidate texts (GitHub summary + resume) are separately encoded into dense 384-dimensional vectors using a pre-trained Sentence-BERT model. Cosine similarity measures the angular distance between these vectors:

```
cos(θ) = (A · B) / (‖A‖ × ‖B‖)
```

**Why it's efficient**: `all-MiniLM-L6-v2` is a distilled model optimized for inference speed — ~5x faster than full BERT with only a ~1% accuracy loss on STS benchmarks. The model is loaded once via `@st.cache_resource` and reused across all requests, eliminating cold-start overhead.

#### Layer 2: Shannon Entropy — Polyglot Index

Shannon Entropy quantifies the **diversity** of a candidate's programming language usage from GitHub:

```
H(X) = -Σ p(xᵢ) × log₂(p(xᵢ))
```

| Entropy Score | Classification |
|---|---|
| H < 1.0 | **Deep Specialist** — Focused on 1-2 languages |
| 1.0 ≤ H < 2.0 | **Versatile Developer** — Balanced across a few languages |
| H ≥ 2.0 | **Broad Generalist** — Significant spread across many languages |

**Why it's efficient**: Computed in O(n) where n = number of distinct languages. No ML inference required — pure mathematical signal. Gives recruiters an immediate, objective profile classification.

#### Layer 3: Jaccard Similarity Index — Keyword Overlap

Measures exact keyword overlap between the JD and candidate text using set-theoretic intersection:

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

Words are tokenized using regex (`\b[a-zA-Z]{3,}\b`), lowercased, and compared as sets.

**Why it's efficient**: O(n + m) time complexity with Python's built-in hash-set operations. Provides a deterministic, LLM-free baseline that catches keyword matches the neural model might abstract away.

### Anti-Fake Multiplier System

TrueSignal applies a **verification-based scoring penalty** to prevent resume inflation:

| Verification Status | Multiplier | Effect |
|---|---|---|
| No GitHub + No DSA | 0.4x | **60% penalty** — completely unverifiable |
| GitHub only, no DSA | 0.75x | **25% penalty** — partial verification |
| GitHub + DSA verified | 1.0x | **Full score** + DSA boost applied |

**DSA Boost Formula**:
- **LeetCode**: `+15 + min(total_solved, 300) / 20` → up to **+30** points
- **Codeforces**: `+15 + min(rating, 2000) / 100` → up to **+35** points

Final score: `min(100, base_semantic × penalty_multiplier + dsa_boost)`

---

### RAG Engine — `rag_engine.py`

The Enterprise RAG (Retrieval-Augmented Generation) system implements a full vector search pipeline:

#### Chunking Strategy
Resumes are split into **overlapping windows** for optimal semantic coverage:

| Parameter | Value |
|---|---|
| Chunk Size | 500 characters |
| Overlap | 100 characters |
| Strategy | Sliding window |

**Why overlap matters**: A 100-char overlap ensures that no sentence is split in half between two chunks. Critical skills mentioned at chunk boundaries are preserved in at least one complete chunk.

#### Vector Search
1. Query is embedded using the same `all-MiniLM-L6-v2` model.
2. Cosine similarity is computed against **all** stored chunk embeddings.
3. Results below a 0.1 relevance threshold are filtered out.
4. Top-K chunks are retrieved and passed to the LLM for synthesis.

#### LLM Synthesis
- **Model**: `llama-3.3-70b-versatile` via Groq API
- **Temperature**: 0.2 (low-creativity, factual retrieval)
- **Max Tokens**: 800

**Why Groq**: Groq's LPU (Language Processing Unit) hardware delivers ~10x faster inference than GPU-based LLM hosting, enabling real-time RAG responses within the Streamlit session.

---

### Glass-Box Audit Engine — `audit_engine.py`

The audit engine produces a fully **explainable** AI evaluation:

| Component | Detail |
|---|---|
| **Model** | `llama-3.1-8b-instant` via Groq |
| **Output Format** | Strict JSON schema (enforced via `response_format`) |
| **Temperature** | 0.1 (near-deterministic for consistency) |

**Structured Output Fields**:
- `confidence_score` — Integer 0-100
- `skill_justifications[]` — Per-skill score with evidence citations
- `critical_skills_missing[]` — Gaps relative to the JD
- `code_quality_assessment` — Commit message quality evaluation
- `hr_deep_analysis` — Senior HR-level career trajectory analysis
- `bias_check_status` — Whether anonymization was applied

#### Anti-Bias Anonymization
When enabled, an LLM pre-processing step strips:
- Candidate names, gender markers
- University/college names
- Geographic locations
- All demographic proxies

This ensures decisions rely **100%** on technical artifact evidence.

---

### OSINT Data Ingestion

#### GitHub — `github_ingestion.py`
- Authenticates via `GITHUB_TOKEN` (Personal Access Token)
- Fetches the **top 6 most recently updated** repos (owner-only, sorted by update time)
- Extracts: repo name, description, language, stars, commit count, and **most recent 3 commit messages** (for code quality assessment)
- Aggregates a language distribution dictionary for Shannon Entropy

#### LeetCode — `dsa_ingestion.py`
- Queries [LeetCode's unofficial GraphQL API](https://leetcode.com/graphql/)
- Extracts: Easy / Medium / Hard solve counts, total solved, and global ranking
- Supports both raw usernames and full profile URLs (auto-cleaned)

#### Codeforces — `dsa_ingestion.py`
- Queries [Codeforces' official REST API](https://codeforces.com/apiHelp)
- Extracts: Current rating, max rating, and rank title (e.g., "Expert", "Candidate Master")

#### Resume Parser — `resume_parser.py`
- Extracts raw text from PDF using **PyPDF2**
- **OSINT Auto-Extraction**: Regex patterns automatically identify GitHub, LeetCode, and Codeforces profile URLs embedded in the resume
- Extracted profiles are cross-checked against user-provided inputs for identity verification

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (wide layout, dark theme compatible) |
| **LLM Intelligence** | Groq API — LLaMA-3.3 70B (RAG) + LLaMA-3.1 8B (Audit & Anonymization) |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`, 384-dim) |
| **Data Ingestion** | PyGithub, Codeforces REST API, LeetCode GraphQL |
| **Vector Store** | Custom pickle-based persistent store with cosine similarity search |
| **Deterministic Analytics** | scikit-learn (cosine similarity), Shannon Entropy, Jaccard Index |
| **PDF Parsing** | PyPDF2 |
| **Report Export** | FPDF (latin-1 compatible PDF generation) |
| **Visualization** | Plotly Express & Plotly Graph Objects |
| **Environment** | python-dotenv |

---

## 📐 System Flow

```
┌──────────────┐
│  Resume PDF  │──► PyPDF2 Text Extraction ──► OSINT Regex (GitHub/LC/CF URLs)
└──────────────┘                                        │
                                                        ▼
┌──────────────┐                              ┌──────────────────┐
│  GitHub User │──► PyGithub API ────────────► │                  │
└──────────────┘                               │  MATCHING ENGINE │
┌──────────────┐                               │                  │
│  LeetCode ID │──► GraphQL API ─────────────► │  1. Cosine Sim   │
└──────────────┘                               │  2. Entropy      │
┌──────────────┐                               │  3. Jaccard      │
│ Codeforces ID│──► REST API ────────────────► │  4. Anti-Fake    │
└──────────────┘                               └────────┬─────────┘
                                                        │
                                                        ▼
                                              ┌──────────────────┐
┌──────────────┐                              │  GLASS-BOX AUDIT │
│ Job Descript.│──► Bounded Text (1500 chars)─►│  (Groq LLaMA-3)  │
└──────────────┘                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  Dashboard +     │
                                              │  PDF Export       │
                                              └──────────────────┘
```

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

## 📁 Project Structure

```
TrueSignal/
├── app.py                  # Main Streamlit application (535 lines)
├── matching_algorithm.py   # Cosine similarity, Shannon entropy, Jaccard index
├── audit_engine.py         # Groq LLM-powered Glass-Box audit & anonymization
├── rag_engine.py           # Enterprise RAG: chunking, vector store, LLM synthesis
├── github_ingestion.py     # GitHub API data fetcher (repos, commits, languages)
├── dsa_ingestion.py        # LeetCode (GraphQL) & Codeforces (REST) stats
├── resume_parser.py        # PDF text extraction & OSINT URL extraction
├── dataset_manager.py      # Sample JDs & skills taxonomy
├── talent_pool.pkl         # Persistent RAG vector database
├── requirements.txt        # Python dependencies
└── .env                    # API keys (GITHUB_TOKEN, GROQ_API_KEY)
```

---

## 🛡️ Anti-Fake & Verification

TrueSignal implements a strict **Anti-Fake Multiplier**. Candidates with **zero verifiable OSINT footprint** (no GitHub, no LeetCode, no Codeforces) are penalized by **up to 60%**, surfacing only those who demonstrate their skills in the real world. This is not a heuristic — it is a deterministic, mathematically-enforced scoring constraint.

---

## 📄 License

This project was built for a hackathon. Please reach out before using commercially.
