# TrueSignal ⚡ — Hackathon Abstract

> **Tagline**: _"Don't trust the resume. Verify the engineer."_

---

## 📹 Demo

[![Watch the Demo](https://img.shields.io/badge/▶️_Watch_Demo-YouTube-red?style=for-the-badge&logo=youtube)](https://drive.google.com/file/d/1z9ZDi1bw9lbH0dgUwR0B_2lnlHKtYp0V/view?usp=sharing)

---

## 🔥 The Problem

**68% of resumes contain exaggerated or fabricated claims** (HireRight Employment Screening Benchmark). The hiring industry relies on a fundamentally broken system — PDF-parsed keyword matching — where candidates can game their way past ATS filters by stuffing buzzwords they've never actually used in production.

Current solutions fail because they:
- **Trust the resume as ground truth** — ATS systems parse and rank resumes without verifying a single claim
- **Are opaque black boxes** — Recruiters get a "match score" with zero explanation of _why_
- **Ignore real-world proof** — Open-source contributions, competitive programming records, and commit histories are never considered
- **Introduce bias** — Names, universities, and demographics unconsciously influence decisions, even in "AI-powered" tools

**The cost?** Bad hires cost companies **$17,000–$240,000** per mis-hire (U.S. Department of Labor). The problem isn't finding candidates — it's _trusting_ that they are who they say they are.

---

## 💡 Our Approach — "Verify, Don't Trust"

TrueSignal flips the hiring intelligence model on its head. Instead of scoring resumes, we **audit engineers** by cross-referencing every claim against independently verifiable digital footprints.

### The TrueSignal Pipeline

```
Resume (PDF)  ──►  OSINT Extraction  ──►  Multi-Source Verification  ──►  Glass-Box Audit
                   (GitHub, LC, CF)       (Semantic + Deterministic)      (Explainable AI)
```

**Step 1 — OSINT Identity Extraction**
We auto-extract GitHub, LeetCode, and Codeforces profile URLs directly from the resume PDF using regex-based OSINT parsing. These are cross-checked against user-provided handles to detect **identity mismatches** — the first red flag of a fraudulent application.

**Step 2 — Multi-Source Data Ingestion**
We pull live data from three independent verification sources:
- **GitHub API** — Top 10 repos ranked by a blended impact sort (Stars × Recency), deep per-repo language analysis via `get_languages()`, and the 3 most recent commit messages for code quality assessment
- **LeetCode GraphQL API** — Easy/Medium/Hard solve breakdown, total solved, global ranking
- **Codeforces REST API** — Current rating, max rating, competitive rank title

**Step 3 — Three-Layer Scoring Engine (Semantic + Deterministic)**

| Layer | Algorithm | What It Measures | Complexity |
|---|---|---|---|
| **Cosine Similarity** | `all-MiniLM-L6-v2` (384-dim Sentence-BERT) | Semantic alignment between JD and candidate artifacts | O(d) |
| **Shannon Entropy** | H(X) = −Σ p(xᵢ) log₂ p(xᵢ) | Language diversity → Specialist vs. Generalist classification | O(n) |
| **Jaccard Index** | J(A,B) = \|A∩B\| / \|A∪B\| | Hard keyword overlap — catches what embeddings abstract away | O(n+m) |

**Step 4 — Anti-Fake Multiplier & Trust Score**
We compute a **Trust Score** by checking how many skills claimed on the resume are independently verifiable through GitHub repos or DSA platform data. If a candidate claims 10 skills but only 1 is verifiable, their Trust Score drops to 10% — and they receive an **additional 20% penalty** on their final match score. Completely unverifiable candidates (no GitHub, no DSA) receive a **60% penalty**.

**Step 5 — Glass-Box AI Audit (Explainable LLM)**
Unlike black-box matching, our Groq-powered LLaMA-3 audit produces a fully structured JSON explanation:
- Per-skill scores (1-10) with **evidence citations** referencing specific repos, commit messages, or resume lines
- **First-Principles Reasoning** — If a candidate built a Transformer from scratch, they are automatically verified as expert-level in all constituent sub-skills (backpropagation, tokenization, attention mechanisms, etc.)
- Critical missing skills (only flagged if absent from **both** resume and all OSINT sources)
- HR-grade career trajectory analysis

**Step 6 — Enterprise RAG (Retrieval-Augmented Generation)**
Resumes are chunked into 500-character overlapping windows (100-char overlap) and embedded into a persistent vector database. Hiring managers can semantically query their entire historical applicant pool — e.g., _"Find me someone who built distributed systems handling 10k+ RPS"_ — and get AI-synthesized answers backed by retrieved evidence chunks.

---

## 🏆 What Makes TrueSignal Different

| Feature | Traditional ATS | AI Resume Screeners | **TrueSignal** |
|---|---|---|---|
| Data Source | Resume only | Resume only | Resume + GitHub + LeetCode + Codeforces |
| Verification | ❌ None | ❌ None | ✅ OSINT cross-referencing + Trust Score |
| Explainability | ❌ Black box | ⚠️ Partial | ✅ Full Glass-Box audit with per-skill evidence |
| Anti-Fake | ❌ None | ❌ None | ✅ 60% penalty for unverifiable candidates |
| Bias Mitigation | ❌ None | ⚠️ Basic | ✅ LLM-powered demographic anonymization |
| Semantic Search | ❌ Keyword only | ⚠️ Basic | ✅ Dense vector embeddings (Sentence-BERT) |
| Talent Pool Query | ❌ None | ❌ None | ✅ Enterprise RAG with natural language queries |
| Batch Ranking | ⚠️ Basic | ⚠️ Basic | ✅ Competitive leaderboard with DSA tiebreakers |

### Key Differentiators

1. **Verification-First Architecture** — We are the only system that _penalizes_ unverifiable claims rather than rewarding keyword stuffing
2. **Three Algorithm Fusion** — Cosine Similarity captures meaning, Jaccard catches exact keywords, Shannon Entropy profiles specialization — no single point of failure
3. **First-Principles AI Reasoning** — Our LLM doesn't just keyword-match; it infers mastery from architectural depth (building nanoGPT → verified expert in backprop, attention, GPU kernels)
4. **Zero-Mock, Zero-Hallucination** — Every score is backed by real data or explicitly penalized. We never fabricate confidence.
5. **Enterprise RAG** — The only hackathon-grade system with a persistent vector talent pool and natural language HR queries

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| LLM Intelligence | Groq API — LLaMA-3.3 70B (RAG) + LLaMA-3.1 8B (Audit) |
| Embeddings | Sentence-Transformers (`all-MiniLM-L6-v2`, 384-dim) |
| OSINT Ingestion | PyGithub, LeetCode GraphQL, Codeforces REST API |
| Vector Store | Pickle-based persistent store + Cosine Similarity search |
| Deterministic Analytics | Shannon Entropy, Jaccard Index, Anti-Fake Multiplier |
| PDF Processing | PyPDF2 (parsing) + FPDF (report generation) |
| Visualization | Plotly Express & Graph Objects |

---

## 👥 Team

| Member | Role |
|---|---|
| [Name 1] | [Role] |
| [Name 2] | [Role] |
| [Name 3] | [Role] |

---

_Built with conviction that hiring should reward proof, not persuasion._