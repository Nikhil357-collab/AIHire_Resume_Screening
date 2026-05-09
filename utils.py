import os
import re
import pdfplumber
import docx

# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_text_from_pdf(pdf_path):

    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                extracted = page.extract_text()

                if extracted:
                    text += extracted + " "

    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")

    return text


# -----------------------------
# DOCX TEXT EXTRACTION
# -----------------------------
def extract_text_from_docx(docx_path):

    text = ""

    try:
        document = docx.Document(docx_path)

        for para in document.paragraphs:
            text += para.text + " "

    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")

    return text


# -----------------------------
# TEXT CLEANING
# -----------------------------
def clean_text(text):

    text = text.lower()

    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -----------------------------
# SKILL EXTRACTION
# -----------------------------
def extract_skills(text):

    skills_db = [
        "python",
        "sql",
        "machine learning",
        "pandas",
        "numpy",
        "apis",
        "data analysis",
        "cloud computing",
        "nlp",
        "deep learning",
        "scikit learn",
        "tensorflow",
        "power bi",
        "tableau",
        "excel",
        "communication",
        "leadership"
    ]

    found_skills = []

    for skill in skills_db:

        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))


# -----------------------------
# READ JOB DESCRIPTION
# -----------------------------
def load_job_description(file_path):

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            jd = file.read()

        return clean_text(jd)

    except Exception as e:
        print(f"Error loading Job Description: {e}")
        return ""