# TrueSignal ⚡

TrueSignal is a highly polished, production-grade Talent Intelligence prototype built for a 6-hour hackathon. 

It holistic extracts real-world developer capabilities from:
- **GitHub Profiles**: Evaluates repo language distribution, activity, and commit hygiene/quality.
- **Resumes (PDF)**: Parses resumes into semantic blocks.
- **DSA Platforms**: Fetches stats from LeetCode (Unofficial GraphQL) and Codeforces (Official API).

It matches this aggregate data against a provided Job Description using dense vector embeddings (`all-MiniLM-L6-v2`) and provides a fully auditable, bias-resistant reasoning chain using the Groq API (`llama3-8b-8192`).

## Features
- **Holistic ingestion**: Combine Resume, GitHub, and competitive programming stats.
- **AI Glass-Box Audit**: Fast explainability for match scores mapping clear verified vs missing criteria.
- **Strict Anonymization (Anti-Bias)**: Uses an LLM pass to aggressively scrub gender, names, locations, and educational institutions before the matching logic assesses the data, ensuring decisions rely strictly on technical merit.

## Setup & Installation

1. Clone this repository and `cd` into it.
2. Create a `.env` file in the root directory (do not commit this file):
   ```env
   GITHUB_TOKEN="your_github_token"
   GROQ_API_KEY="your_groq_api_key"
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```