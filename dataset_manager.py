import pandas as pd
import streamlit as st
from typing import Dict, List

@st.cache_data
def load_sample_jds() -> Dict[str, str]:
    """
    Returns a dictionary of pre-configured Job Descriptions.
    These are used to populate a Streamlit dropdown for one-click loading during the demo.
    """
    return {
        "Full Stack Developer": """
We are looking for a Full Stack Developer to produce scalable software solutions. You’ll be part of a cross-functional team that’s responsible for the full software development life cycle, from conception to deployment.
Key Skills: Python, React, JavaScript, SQL, API Design, Docker, Git.
""",
        "Data Scientist": """
We are seeking a Data Scientist to analyze large amounts of raw information to find patterns that will help improve our company. We will rely on you to build data products to extract valuable business insights.
Key Skills: Python, Machine Learning, scikit-learn, pandas, SQL, Deep Learning, Data Visualization.
""",
        "DevOps Engineer": """
We are looking for a DevOps Engineer to help us build functional systems that improve customer experience. Responsibilities include deploying product updates, identifying production issues and implementing integrations that meet customer needs.
Key Skills: CI/CD, AWS, Kubernetes, Terraform, Docker, Python, Bash.
"""
    }

@st.cache_data
def load_skills_taxonomy() -> List[str]:
    """
    Loads a dummy list of standard technical skills representing the Lightcast/O*NET taxonomy.
    """
    # In a real environment, this might load a CSV or an API.
    skills = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Ruby",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "Docker", "Kubernetes", "AWS", "Google Cloud", "Azure", "Terraform",
        "Machine Learning", "Deep Learning", "scikit-learn", "TensorFlow", "PyTorch", "pandas",
        "Git", "CI/CD", "Linux", "Bash", "Agile", "API Design", "Data Visualization",
        "Cloud Computing", "Microservices", "System Design", "Algorithms"
    ]
    return sorted(skills)
