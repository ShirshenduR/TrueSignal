import PyPDF2
from io import BytesIO

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
