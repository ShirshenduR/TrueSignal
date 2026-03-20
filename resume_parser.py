import PyPDF2
from io import BytesIO
import re

def extract_text_from_pdf(pdf_file_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file using PyPDF2.
    """
    try:
        reader = PyPDF2.PdfReader(BytesIO(pdf_file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def extract_profiles_from_text(text: str) -> dict:
    profiles = {"github": None, "leetcode": None, "codeforces": None}
    
    # Simple regex extractions for OSINT URLs
    gh_match = re.search(r'github\.com/([a-zA-Z0-9-]+)', text, re.IGNORECASE)
    if gh_match: profiles["github"] = gh_match.group(1).rstrip('/')
        
    lc_match = re.search(r'leetcode\.com/(?:u/)?([a-zA-Z0-9_.-]+)', text, re.IGNORECASE)
    if lc_match: profiles["leetcode"] = lc_match.group(1).rstrip('/')
        
    cf_match = re.search(r'codeforces\.com/profile/([a-zA-Z0-9_.-]+)', text, re.IGNORECASE)
    if cf_match: profiles["codeforces"] = cf_match.group(1).rstrip('/')
        
    return profiles
