import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from dataset_manager import load_sample_jds, load_skills_taxonomy
from github_ingestion import GitHubParser
from resume_parser import extract_text_from_pdf
from dsa_ingestion import fetch_leetcode_stats, fetch_codeforces_stats
from matching_algorithm import compute_match
from audit_engine import generate_glassbox_audit, anonymize_text

st.set_page_config(
    page_title="TrueSignal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .reportview-container .main .block-container { padding-top: 2rem; }
    .metric-card { background-color: #1E1E1E; border-radius: 10px; padding: 20px; text-align: center; }
    h1 { font-family: 'Inter', sans-serif; }
    .stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

def initialize_state():
    if "gh_parser" not in st.session_state:
        st.session_state.gh_parser = GitHubParser()

def main():
    initialize_state()
    taxonomy = load_skills_taxonomy()
    jds = load_sample_jds()
    
    st.title("TrueSignal: Holistic Talent Intelligence ⚡")
    
    with st.sidebar:
        st.header("Configuration")
        
        selected_jd_title = st.selectbox("Select Sample Job Description", options=list(jds.keys()))
        jd_text = st.text_area("Or Paste Custom Job Description", value=jds[selected_jd_title], height=150)
        
        st.markdown("---")
        st.header("Candidate Artifacts")
        github_username = st.text_input("GitHub Username", value="defunkt")
        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        leetcode_username = st.text_input("LeetCode Username (Optional)")
        codeforces_username = st.text_input("Codeforces Handle (Optional)")
        
        st.markdown("### Compliance Settings")
        strict_anonymization = st.toggle("🛡️ Enable Strict Anonymization (Bias Check)", value=False)
        
        st.markdown("---")
        run_audit = st.button("🚀 Run Holistic Intelligence Audit", use_container_width=True, type="primary")

    if strict_anonymization:
        st.info("🔒 **Anonymization Active:** Gender, name, education, and demographic proxies proactively stripped by LLM pre-processing. Decision relies 100% on pure technical artifacts.", icon="🛡️")

    if run_audit and (github_username or resume_file) and jd_text:
        with st.spinner("Analyzing candidate technical footprint across all sources..."):
            # 1. GitHub Ingestion
            gh_data = st.session_state.gh_parser.fetch_user_data(github_username) if github_username else {"username": "No Profile", "repos_analyzed": 0, "total_commits": 0, "languages": {}, "summary_text": "", "raw_repos": []}
            if gh_data.get("error"):
                st.warning(f"GitHub fallback data active: {gh_data['error']}")
            gh_summary = gh_data["summary_text"]
            
            # 2. Resume Parsing
            resume_text = ""
            if resume_file:
                resume_text = extract_text_from_pdf(resume_file.read())
                
            # 3. DSA Ingestion
            dsa_data = {
                "leetcode": fetch_leetcode_stats(leetcode_username) if leetcode_username else {},
                "codeforces": fetch_codeforces_stats(codeforces_username) if codeforces_username else {}
            }
            
            # 4. Anti-Bias Anonymization (LLM Pre-processing)
            display_name = "Candidate ID: Alpha-01" if strict_anonymization else gh_data.get("username", "Unknown")
            if strict_anonymization:
                with st.spinner("Anonymizing data layers..."):
                    if gh_summary: gh_summary = anonymize_text(gh_summary)
                    if resume_text: resume_text = anonymize_text(resume_text)

            # 5. Matching
            match_results = compute_match(jd_text, gh_summary, resume_text, dsa_data, taxonomy)
            match_score = match_results["match_score"]
            dsa_boost = match_results["dsa_boost"]

            # 6. Audit Explainability
            dossier = f"---GITHUB---\n{gh_summary}\n\n---RESUME---\n{resume_text}\n\n---DSA STATS---\nLeetCode: {dsa_data['leetcode']}\nCodeforces: {dsa_data['codeforces']}"
            audit_report = generate_glassbox_audit(jd_text, dossier, match_score)

        st.markdown("---")
        
        # TOP ROW: Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Holistic Match Score", f"{audit_report.get('confidence_score', match_score)}%")
        col2.metric("DSA Boost Check", f"+{dsa_boost}%")
        col3.metric("Repos Analyzed", gh_data.get("repos_analyzed", 0))
        
        total_dsa = (dsa_data["leetcode"].get("total_solved", 0) if dsa_data["leetcode"] else 0)
        col4.metric("DSA Solved (LeetCode)", total_dsa)

        st.markdown("---")

        # Visuals & DSA Profile
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            st.subheader("Coding Activity & Languages")
            if gh_data.get("languages"):
                lang_df = pd.DataFrame(list(gh_data["languages"].items()), columns=["Language", "Repository Count"])
                fig = px.bar(lang_df, x="Language", y="Repository Count", color="Language", template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No GitHub data available for charting.", icon="ℹ️")
                
        with vcol2:
            st.subheader("Algorithmic Excellence (DSA Profile)")
            st.write(f"**Validating: {display_name}**")
            if leetcode_username or codeforces_username:
                lc = dsa_data["leetcode"]
                cf = dsa_data["codeforces"]
                if lc:
                    st.success(f"**LeetCode - Total Solved:** {lc.get('total_solved', 0)} (Easy: {lc.get('easy', 0)}, Med: {lc.get('medium', 0)}, Hard: {lc.get('hard', 0)})")
                if cf:
                    st.info(f"**Codeforces - Max Rating:** {cf.get('max_rating', 0)} ({cf.get('rank', 'Unrated')})")
            else:
                st.write("No algorithmic profiles provided.")

        st.markdown("---")

        # BOTTOM ROW: The Glass-Box Audit (2 Columns)
        bottom_col1, bottom_col2 = st.columns(2)

        with bottom_col1:
            st.subheader("Artifact Insights")
            if gh_data.get("raw_repos"):
                st.markdown("**GitHub Repositories (Focusing on Commit Quality):**")
                for repo in gh_data["raw_repos"][:3]:
                    with st.container(border=True):
                        st.markdown(f"**📦 {repo['name']}**")
                        if repo.get('recent_commit_messages'):
                            st.write("*Recent Commits:*")
                            for msg in repo['recent_commit_messages']:
                                st.caption(f"- {msg}")
            if resume_file:
                st.markdown("**Resume Abstract:**")
                st.caption(f"{resume_text[:400]}...")

        with bottom_col2:
            st.subheader("AI Reasoning (Glass-Box Audit)")
            st.success(f"**Status:** {audit_report.get('bias_check_status', 'Passed')}")
            
            st.write("---")
            st.markdown("##### 🔍 Verified Skills Present:")
            for s in audit_report.get('verified_skills_present', []):
                st.markdown(f"- ✅ `{s}`")

            st.write("---")
            st.markdown("##### 🚨 Critical Skills Missing:")
            for s in audit_report.get('critical_skills_missing', []):
                st.markdown(f"- ❌ `{s}`")

            st.write("---")
            if 'code_quality_assessment' in audit_report:
                st.info(f"**Quality Probe:** {audit_report['code_quality_assessment']}")

            st.warning(f"**Justification:** \n\n{audit_report.get('justification', 'No justification provided.')}")

if __name__ == "__main__":
    main()
