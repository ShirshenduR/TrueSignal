import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from dataset_manager import load_sample_jds, load_skills_taxonomy
from github_ingestion import GitHubParser
from resume_parser import extract_text_from_pdf, extract_profiles_from_text
from dsa_ingestion import fetch_leetcode_stats, fetch_codeforces_stats
from matching_algorithm import compute_match, compute_shannon_entropy, compute_jaccard_similarity
from audit_engine import generate_glassbox_audit, anonymize_text
import rag_engine

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
        run_audit = st.button("🚀 Run Holistic Intelligence Audit", type="primary")

    tab1, tab2, tab3 = st.tabs(['🔍 Single Profile Audit', '📊 Batch Comparison Mode', '🧠 Enterprise RAG'])
    
    with tab1:
            if strict_anonymization:
                st.info("🔒 **Anonymization Active:** Gender, name, education, and demographic proxies proactively stripped by LLM pre-processing. Decision relies 100% on pure technical artifacts.", icon="🛡️")
        
            if run_audit and (github_username or resume_file) and jd_text:
                with st.spinner("Analyzing candidate technical footprint across all sources (bounding text for API limits)..."):
                    # 1. Resume Parsing First (to extract OSINT URLs)
                    resume_text = ""
                    extracted_profiles = {"github": None, "leetcode": None, "codeforces": None}
                    if resume_file:
                        resume_raw = extract_text_from_pdf(resume_file.read())
                        extracted_profiles = extract_profiles_from_text(resume_raw)
                        resume_text = resume_raw[:2500]
        
                    # 1.5 OSINT Identity Verification (UI vs Resume)
                    mismatches = []
        
                    if extracted_profiles.get("github"):
                        if github_username and github_username.lower() != extracted_profiles["github"].lower():
                            mismatches.append(f"GitHub (UI: {github_username} vs Resume: {extracted_profiles['github']})")
                        elif not github_username:
                            github_username = extracted_profiles["github"]
        
                    if extracted_profiles.get("leetcode"):
                        if leetcode_username and leetcode_username.lower() != extracted_profiles["leetcode"].lower():
                            mismatches.append(f"LeetCode (UI: {leetcode_username} vs Resume: {extracted_profiles['leetcode']})")
                        elif not leetcode_username:
                            leetcode_username = extracted_profiles["leetcode"]
        
                    if extracted_profiles.get("codeforces"):
                        if codeforces_username and codeforces_username.lower() != extracted_profiles["codeforces"].lower():
                            mismatches.append(f"Codeforces (UI: {codeforces_username} vs Resume: {extracted_profiles['codeforces']})")
                        elif not codeforces_username:
                            codeforces_username = extracted_profiles["codeforces"]
        
                    if mismatches:
                        st.warning(f"🚨 **Identity Mismatch Detected:** Discrepancies between provided UI inputs and resume links: {', '.join(mismatches)}")
        
                    # 2. GitHub Ingestion
                    gh_data = st.session_state.gh_parser.fetch_user_data(github_username) if github_username else {"username": "No Profile", "repos_analyzed": 0, "total_commits": 0, "languages": {}, "summary_text": "", "raw_repos": []}
                    if gh_data.get("error"):
                        st.warning(f"GitHub API Error: {gh_data['error']}")
                        
                    # 3. DSA Ingestion
                    dsa_data = {
                        "leetcode": fetch_leetcode_stats(leetcode_username) if leetcode_username else {},
                        "codeforces": fetch_codeforces_stats(codeforces_username) if codeforces_username else {}
                    }
                    
                    # Truncating payloads to respect Groq TPM free tier limits
                    gh_summary = gh_data["summary_text"][:1500] if gh_data.get("summary_text") else ""
                    jd_text_bounded = jd_text[:1500] if jd_text else ""
        
                    # 4. Anti-Bias Anonymization (LLM Pre-processing)
                    display_name = "Candidate ID: Alpha-01" if strict_anonymization else gh_data.get("username", "Unknown")
                    if strict_anonymization:
                        with st.spinner("Anonymizing data layers..."):
                            if gh_summary: gh_summary = anonymize_text(gh_summary)
                            if resume_text: resume_text = anonymize_text(resume_text)
        
                    # 5. Matching Phase 1: Vector Math
                    match_results = compute_match(jd_text, gh_summary, resume_text, dsa_data, taxonomy)
                    match_score = match_results["match_score"]
                    dsa_boost = match_results["dsa_boost"]
        
                    # 5.1 Matching Phase 2: Deterministic Analytics (Non-LLM)
                    entropy_score, polyglot_label = compute_shannon_entropy(gh_data.get("languages", {}))
                    combined_candidate_text = gh_summary + " " + resume_text
                    jaccard_score = compute_jaccard_similarity(jd_text_bounded, combined_candidate_text)
        
                    # 6. Audit Explainability
                    dossier = f"---GITHUB---\n{gh_summary}\n\n---RESUME---\n{resume_text}\n\n---DSA STATS---\nLeetCode: {dsa_data['leetcode']}\nCodeforces: {dsa_data['codeforces']}"
                    # Using jd_text_bounded to prevent Groq TPM Strict Rate Limits
                    audit_report = generate_glassbox_audit(jd_text_bounded, dossier, match_score)
        
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
                        st.plotly_chart(fig)
                    else:
                        st.info("No GitHub data available for charting.", icon="ℹ️")
                        
                with vcol2:
                    st.subheader("Algorithmic Excellence (DSA Profile)")
                    st.write(f"**Validating: {display_name}**")
                    if leetcode_username or codeforces_username:
                        lc = dsa_data.get("leetcode", {})
                        cf = dsa_data.get("codeforces", {})
                        
                        if cf and cf.get('rating') and cf.get('rating') > 0:
                            fig_cf = go.Figure(go.Indicator(
                                mode = "gauge+number",
                                value = cf.get('rating', 0),
                                title = {'text': f"Codeforces ({cf.get('rank', 'Unrated')})", 'font': {'size': 14}},
                                gauge = {
                                    'axis': {'range': [None, 2400]},
                                    'bar': {'color': "#2b82ff"}
                                }
                            ))
                            fig_cf.update_layout(height=200, margin=dict(t=30, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                            st.plotly_chart(fig_cf)
                            
                        if lc and lc.get('total_solved', 0) > 0:
                            # Filter out zeroes and create dataframe for chart
                            diffs = [{"Difficulty": "Easy", "Count": lc.get("easy", 0)},
                                     {"Difficulty": "Medium", "Count": lc.get("medium", 0)},
                                     {"Difficulty": "Hard", "Count": lc.get("hard", 0)}]
                            
                            st.success(f"**LeetCode - Total Solved:** {lc.get('total_solved', 0)}")
                            df_lc = pd.DataFrame(diffs)
                            df_lc = df_lc[df_lc["Count"] > 0]
                            
                            if not df_lc.empty:
                                fig_lc = px.pie(
                                    df_lc, 
                                    names="Difficulty", 
                                    values="Count", 
                                    hole=0.6,
                                    color="Difficulty",
                                    color_discrete_map={"Easy": "#00b8a3", "Medium": "#ffc01e", "Hard": "#ef4743"},
                                    height=250
                                )
                                fig_lc.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                                st.plotly_chart(fig_lc)
                        elif lc:
                            st.success(f"**LeetCode - Total Solved:** {lc.get('total_solved', 0)} (Easy: {lc.get('easy', 0)}, Med: {lc.get('medium', 0)}, Hard: {lc.get('hard', 0)})")
                    else:
                        st.write("No algorithmic profiles provided.")
        
                st.markdown("---")
                st.subheader("⚙️ Deterministic Signals (Pure Mathematical Analytics)")
                st.write("These metrics evaluate strict Computer Science fundamentals, entirely bypassing LLM generations to ensure absolute, mathematically proven baselines.")
        
                m1, m2, m3 = st.columns(3)
                m1.metric("Dense Vector Embeddings", f"{match_results.get('base_semantic_score', 0)}%", "Cosine Similarity against JD")
                m2.metric("Polyglot Index (Shannon Entropy)", f"{entropy_score}", f"{polyglot_label} Profile")
                m3.metric("Keyword Overlap (Jaccard Index)", f"{jaccard_score}%", "Pure Set Intersection")
        
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
                    
                    if 'hr_deep_analysis' in audit_report:
                        st.write("---")
                        st.markdown("##### 🧠 HR Deep Analysis:")
                        st.write(audit_report['hr_deep_analysis'])
        
                    st.write("---")
                    st.markdown("##### 🔍 Verified Skills Justifications:")
                    skill_justs = audit_report.get('skill_justifications', [])
                    if skill_justs:
                        for s in skill_justs:
                            score = s.get('score_out_of_10', 'N/A')
                            st.markdown(f"- ✅ **{s.get('skill', 'Unknown')}** *(Score: {score}/10)*: {s.get('reasoning', '')}")
                    else:
                        st.write("None identified clearly.")
        
                    st.write("---")
                    st.markdown("##### 🚨 Critical Skills Missing:")
                    for s in audit_report.get('critical_skills_missing', []):
                        st.markdown(f"- ❌ `{s}`")
        
                    st.write("---")
                    if 'code_quality_assessment' in audit_report:
                        st.info(f"**Quality Probe:** {audit_report['code_quality_assessment']}")
        
                    st.warning(f"**Justification:** \\n\\n{audit_report.get('justification', 'No justification provided.')}")
        
                st.markdown("---")
                st.subheader("Export Assessment")
                
                md_content = f"# TrueSignal Talent Intelligence Report\\n\\n"
                md_content += f"**Candidate**: {display_name}\\n"
                md_content += f"**Holistic Match Score**: {audit_report.get('confidence_score', match_score)}%\\n"
                md_content += f"**GitHub Repos Analyzed**: {gh_data.get('repos_analyzed', 0)}\\n"
                md_content += f"**LeetCode Solved**: {total_dsa}\\n\\n"
                md_content += "## 🧠 HR Deep Analysis\\n"
                md_content += audit_report.get('hr_deep_analysis', 'Not provided.') + "\\n\\n"
                md_content += "## ⚖️ Match Justification\\n"
                md_content += audit_report.get('justification', 'Not provided.') + "\\n\\n"
                md_content += "## ✅ Verified Skills\\n"
                for s in audit_report.get('skill_justifications', []):
                    score = s.get('score_out_of_10', 'N/A')
                    md_content += f"- **{s.get('skill', 'Unknown')}** (Score: {score}/10): {s.get('reasoning', '')}\\n"
                md_content += "\\n## 🚨 Critical Missing Skills\\n"
                for s in audit_report.get('critical_skills_missing', []):
                    md_content += f"- {s}\\n"
        
                import re
                from fpdf import FPDF
                
                def create_pdf(text, name, score):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, "TrueSignal ⚡ Candidate Audit Report", ln=True, align='C')
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(0, 10, f"Candidate: {name}", ln=True, align='C')
                    pdf.cell(0, 10, f"Match Score: {score}%", ln=True, align='C')
                    pdf.ln(5)
                    pdf.set_font("Arial", size=10)
                    
                    for line in text.split('\n'):
                        # Ensure string is latin-1 compatible
                        clean_line = re.sub(r'[^\x00-\x7F]+', '', line).strip()
                        if not clean_line and not line.strip():
                            pdf.ln(3)
                            continue
                            
                        if clean_line.startswith('# '):
                            pdf.ln(5)
                            pdf.set_font("Arial", 'B', 14)
                            pdf.multi_cell(0, 8, clean_line.replace('# ', ''))
                            pdf.set_font("Arial", size=10)
                        elif clean_line.startswith('## '):
                            pdf.ln(4)
                            pdf.set_font("Arial", 'B', 12)
                            pdf.multi_cell(0, 7, clean_line.replace('## ', ''))
                            pdf.set_font("Arial", size=10)
                        else:
                            if clean_line.startswith('- '):
                                pdf.set_x(15)
                                pdf.multi_cell(0, 6, clean_line)
                            else:
                                pdf.multi_cell(0, 6, clean_line)
                                
                    # Use 'output(dest="S").encode("latin-1")' for compatibility
                    return pdf.output(dest='S').encode('latin-1')

                pdf_bytes = create_pdf(md_content, display_name, match_score)
                st.download_button(
                    label="📄 Download Full Assessment Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"{str(display_name).replace(' ', '_')}_Audit_Report.pdf",
                    mime="application/pdf",
                    type="primary"
                )

    with tab2:
        st.header("Batch Candidate Comparison")
        st.write("Upload multiple resumes to auto-extract OSINT footprints and rank candidates deterministically.")
        batch_resumes = st.file_uploader("Upload Resumes (PDFs)", type=["pdf"], accept_multiple_files=True, key="batch")
        
        if batch_resumes:
            # Sync session state
            if "batch_files" not in st.session_state or set(st.session_state.batch_files) != set([f.name for f in batch_resumes]):
                data = []
                for file in batch_resumes:
                    file.seek(0)
                    raw_text = extract_text_from_pdf(file.read())
                    osint = extract_profiles_from_text(raw_text)
                    data.append({
                        "Candidate File": file.name,
                        "GitHub": osint.get("github") or "",
                        "LeetCode": osint.get("leetcode") or "",
                        "Codeforces": osint.get("codeforces") or "",
                        "Resume_Text": raw_text[:3000]
                    })
                st.session_state.batch_df = pd.DataFrame(data)
                st.session_state.batch_files = [f.name for f in batch_resumes]
                
            st.write("### 1. Verification Grid")
            st.info("The system automatically extracted the following profiles from the resumes. If any are missing, manually type them into the grid before analyzing.")
            
            display_df = st.session_state.batch_df[["Candidate File", "GitHub", "LeetCode", "Codeforces"]]
            edited_df = st.data_editor(display_df, use_container_width=True)
            
            if st.button("🚀 Run Batch Analytics", type="primary") or st.session_state.get("batch_run", False):
                if not st.session_state.get("batch_run", False):
                    results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for index, row in edited_df.iterrows():
                        status_text.text(f"Analyzing {row['Candidate File']}...")
                        
                        gh_user = str(row["GitHub"]).strip() if pd.notna(row["GitHub"]) and str(row["GitHub"]).strip() else ""
                        lc_user = str(row["LeetCode"]).strip() if pd.notna(row["LeetCode"]) and str(row["LeetCode"]).strip() else ""
                        cf_user = str(row["Codeforces"]).strip() if pd.notna(row["Codeforces"]) and str(row["Codeforces"]).strip() else ""
                        resume_text = st.session_state.batch_df.iloc[index]["Resume_Text"]
                        
                        # Fetch Data
                        gh_data = st.session_state.gh_parser.fetch_user_data(gh_user) if gh_user else {}
                        gh_summary = gh_data.get("summary_text", "")
                        
                        dsa_data = {
                            "leetcode": fetch_leetcode_stats(lc_user) if lc_user else {},
                            "codeforces": fetch_codeforces_stats(cf_user) if cf_user else {}
                        }
                        
                        match_results = compute_match(jd_text, gh_summary, resume_text, dsa_data, taxonomy)
                        entropy_score, _ = compute_shannon_entropy(gh_data.get("languages", {}))
                        jaccard_score = compute_jaccard_similarity(jd_text, gh_summary + " " + resume_text)
                        
                        results.append({
                            "Candidate": row["Candidate File"].replace(".pdf", ""),
                            "Match Score": match_results["match_score"],
                            "Jaccard %": jaccard_score,
                            "Entropy": entropy_score,
                            "LeetCode Solved": dsa_data["leetcode"].get("total_solved", 0) if dsa_data.get("leetcode") else 0,
                            "Codeforces Rating": dsa_data["codeforces"].get("rating", 0) if dsa_data.get("codeforces") else 0
                        })
                        progress_bar.progress((index + 1) / len(edited_df))
                        
                    status_text.empty()
                    progress_bar.empty()
                    st.session_state.res_df = pd.DataFrame(results).sort_values(by="Match Score", ascending=False)
                    st.session_state.batch_run = True
                
                res_df = st.session_state.res_df
                st.subheader("🏆 Competitive Leaderboard")
                st.dataframe(res_df, use_container_width=True)
                
                st.subheader("Score Distributions")
                fig = px.bar(
                    res_df.melt(id_vars=["Candidate"], value_vars=["Match Score", "Jaccard %"]), 
                    x="Candidate", 
                    y="value", 
                    color="variable",
                    barmode="group", 
                    template="plotly_dark",
                    labels={"value": "Score (%)", "variable": "Metric"}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.subheader("🔍 Deep-Dive Profile Analysis")
                selected_cand = st.selectbox("Select a candidate from the leaderboard to view their full AI Glass-Box Audit:", options=[""] + list(res_df["Candidate"]))
                
                if selected_cand:
                    st.write(f"Generating full Deep Dive for **{selected_cand}**...")
                    # Get candidate data from edited_df
                    cand_row = edited_df[edited_df["Candidate File"] == selected_cand + ".pdf"].iloc[0]
                    orig_index = edited_df.index[edited_df["Candidate File"] == selected_cand + ".pdf"].tolist()[0]
                    
                    c_gh = str(cand_row["GitHub"]).strip() if pd.notna(cand_row["GitHub"]) and str(cand_row["GitHub"]).strip() else ""
                    c_lc = str(cand_row["LeetCode"]).strip() if pd.notna(cand_row["LeetCode"]) and str(cand_row["LeetCode"]).strip() else ""
                    c_cf = str(cand_row["Codeforces"]).strip() if pd.notna(cand_row["Codeforces"]) and str(cand_row["Codeforces"]).strip() else ""
                    c_resume = st.session_state.batch_df.iloc[orig_index]["Resume_Text"]
                    
                    gh_data_c = st.session_state.gh_parser.fetch_user_data(c_gh) if c_gh else {}
                    gh_summary_c = gh_data_c.get("summary_text", "")
                    dsa_data_c = {
                        "leetcode": fetch_leetcode_stats(c_lc) if c_lc else {},
                        "codeforces": fetch_codeforces_stats(c_cf) if c_cf else {}
                    }
                    
                    match_results_c = compute_match(jd_text, gh_summary_c, c_resume, dsa_data_c, taxonomy)
                    
                    jd_text_bounded = jd_text[:1500] if jd_text else ""
                    dossier_c = f"---GITHUB---\n{gh_summary_c}\n\n---RESUME---\n{c_resume}\n\n---DSA STATS---\nLeetCode: {dsa_data_c['leetcode']}\nCodeforces: {dsa_data_c['codeforces']}"
                    
                    with st.spinner("Running Glass-Box Audit (LLM Analysis)..."):
                        audit_report_c = generate_glassbox_audit(jd_text_bounded, dossier_c, match_results_c["match_score"])
                        
                    st.success(f"**Status:** {audit_report_c.get('bias_check_status', 'Complete')}")
                    
                    if 'hr_deep_analysis' in audit_report_c:
                        st.markdown("##### 🧠 HR Deep Analysis:")
                        st.write(audit_report_c['hr_deep_analysis'])
                    
                    st.write("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("##### 🔍 Verified Skills Justifications:")
                        for s in audit_report_c.get('skill_justifications', []):
                            score = s.get('score_out_of_10', 'N/A')
                            st.markdown(f"- ✅ **{s.get('skill', 'Unknown')}** *(Score: {score}/10)*: {s.get('reasoning', '')}")
                    with col2:
                        st.markdown("##### 🚨 Critical Skills Missing:")
                        for s in audit_report_c.get('critical_skills_missing', []):
                            st.markdown(f"- ❌ `{s}`")
                            
                    st.warning(f"**Justification:** \\n\\n{audit_report_c.get('justification', 'No justification provided.')}")

    with tab3:
        st.header("Enterprise Talent Pool (RAG Archive)")
        st.write("Build a persistent vector database of hundreds of resumes and query them semantically!")
        
        with st.expander("ℹ️ How to use the Enterprise RAG System & Real-World Use Cases", expanded=False):
            st.markdown("""
            **1. The "Needle in the Haystack" Search**
            Instead of manually control-F searching thousands of PDFs, type specific niche requirements (e.g. *"Find someone who knows GraphQL subscriptions"*). The Vector Engine instantly mathematically scans all resumes to find the exact developers who mention it, and the Groq LLM summarizes their expertise.
            
            **2. Deep Semantic Experience Querying**
            Standard keyword algorithms fail when searching for concepts. If you query: *"Find me candidates with experience building high-traffic distributed architecture"*, the RAG engine will successfully retrieve candidates who wrote *"designed microservices handling 10k requests/sec using Redis"*, even if they never physically typed the exact words "high-traffic".
            
            **3. Cross-Candidate Comparison**
            You can ask the AI highly complex comparative queries directly against your historic applicant pool: *"Out of all candidates, who has the strongest background in CI/CD automation?"* The RAG engine pulls the strongest semantic excerpts across all candidates, and the AI evaluates them side-by-side.
            """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("1. Ingest Resumes to DB")
            rag_uploads = st.file_uploader("Upload Resumes to Knowledge Base", type=["pdf"], accept_multiple_files=True, key="rag_uploader")
            if st.button("Store in Vector DB", type="primary", key="rag_store_btn"):
                if rag_uploads:
                    with st.spinner("Chunking and Embedding into Vector Space..."):
                        for f in rag_uploads:
                            f.seek(0)
                            raw = extract_text_from_pdf(f.read())
                            rag_engine.ingest_to_db(f.name, raw)
                    st.success(f"Successfully vectorized {len(rag_uploads)} PDF(s) into the RAG Database!")
                else:
                    st.warning("Please upload PDFs first.")
                    
            db_size = len(rag_engine.get_db())
            st.metric("Total Extracted Semantic Chunks in DB", db_size)
            
        with col2:
            st.subheader("2. Semantic AI Query")
            user_query = st.text_input("Ask the AI HR Assistant (e.g. 'Find me a senior dev with Docker and AWS experience')")
            if st.button("Search & Analyze", key="rag_search_btn") and user_query:
                with st.spinner("Retrieving Vectors & Generating AI Response..."):
                    top_chunks = rag_engine.search_db(user_query, top_k=6)
                    
                    if not top_chunks:
                        st.warning("The database is completely empty or no relevant vectors found. Upload resumes first.")
                    else:
                        st.markdown("#### ✨ RAG Synthesis (Powered by Groq LLaMA-3)")
                        answer = rag_engine.query_rag_llm(user_query, top_chunks)
                        st.info(answer)
                        
                        st.markdown("---")
                        st.markdown("**Top Retrieved Semantic Chunks (Evidence Context):**")
                        for idx, c in enumerate(top_chunks):
                            with st.expander(f"Context Extract {idx+1} | Source: {c['candidate']} | Cosine Score: {c['score']:.2f}"):
                                st.write(c["chunk"])

if __name__ == "__main__":
    main()
