from fastapi import FastAPI, UploadFile, File
import shutil
import os
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    extract_skills,
    load_job_description
)


app = FastAPI()

# Create upload folder
UPLOAD_FOLDER = "uploaded_resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home Route
@app.get("/")
def home():
    return {
        "message": "welcome to AI Resume Screening API Running"
    }

# Upload Route
@app.post("/upload_resume/")
async def upload_resume(
    file: UploadFile = File(...)
):

    try:

        # Save file path
        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # Dummy AI score
        score = random.randint(70, 98)

        return {
            "filename": file.filename,
            "score": score,
            "status": "Resume Uploaded & Analyzed"
        }

    except Exception as e:

        return {
            "error": str(e)
        }


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )
   # LOGIN SYSTEM


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    # Demo login
    if email == "admin@gmail.com" and password == "admin123":

        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request}
        )

    return {
        "message": "Invalid Login"
    }

# JOB DESCRIPTION UI ROUTE

@app.post("/create-job-ui")
def create_job_ui(
    job_description: str = Form(...)
):

    with open("jd.txt", "w", encoding="utf-8") as f:
        f.write(job_description)

    return {
        "message": "Job Description Saved"
    }


UPLOAD_FOLDER = "uploaded_resumes"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------------
# HOME
# -----------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to SmartHire AI - Automated Resume Screening Platform"
    }

# -----------------------------------
# CREATE JOB DESCRIPTION
# -----------------------------------

@app.post("/create-job")
def create_job(job_description: str):

    with open("jd.txt", "w", encoding="utf-8") as f:
        f.write(job_description)

    return {
        "message": "Job Description Saved"
    }

# -----------------------------------
# UPLOAD RESUME
# -----------------------------------

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "message": "Resume uploaded successfully"
    }

# -----------------------------------
# RANK CANDIDATES
# -----------------------------------

@app.get("/rank-candidates")
def rank_candidates():

    # -----------------------------
    # LOAD JOB DESCRIPTION
    # -----------------------------

    job_description = load_job_description("jd.txt")

    results = []

    # -----------------------------
    # REQUIRED SKILLS
    # -----------------------------

    required_skills = [
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
        "scikit learn"
    ]

    # -----------------------------
    # PROCESS RESUMES
    # -----------------------------

    for file_name in os.listdir(UPLOAD_FOLDER):

        file_path = os.path.join(
            UPLOAD_FOLDER,
            file_name
        )

        resume_text = ""

        # PDF
        if file_name.endswith(".pdf"):

            resume_text = extract_text_from_pdf(file_path)

        # DOCX
        elif file_name.endswith(".docx"):

            resume_text = extract_text_from_docx(file_path)

        else:
            continue

        # Skip empty resumes
        if not resume_text.strip():
            continue

        # -----------------------------
        # CLEAN TEXT
        # -----------------------------

        cleaned_resume = clean_text(resume_text)

        # -----------------------------
        # EXTRACT SKILLS
        # -----------------------------

        skills = extract_skills(cleaned_resume)

        # -----------------------------
        # TF-IDF
        # -----------------------------

        documents = [
            job_description,
            cleaned_resume
        ]

        tfidf = TfidfVectorizer(
            stop_words="english"
        )

        tfidf_matrix = tfidf.fit_transform(documents)

        similarity_score = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        tfidf_score = similarity_score * 100

        # -----------------------------
        # SKILL MATCHING
        # -----------------------------

        matched_skills = []

        for skill in required_skills:

            if skill in cleaned_resume:
                matched_skills.append(skill)

        skill_match_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 100

        # -----------------------------
        # FINAL SCORE
        # -----------------------------

        final_score = (
            (0.9 * skill_match_score) +
            (0.1 * tfidf_score)
        )

        final_score = round(final_score, 2)

        # -----------------------------
        # STATUS
        # -----------------------------

        if final_score >= 80:
            status = "Shortlisted"

        elif final_score >= 60:
            status = "Review"

        else:
            status = "Rejected"

        # -----------------------------
        # STORE RESULTS
        # -----------------------------

        results.append({
            "resume": file_name,
            "score": final_score,
            "skills": skills,
            "matched_skills": matched_skills,
            "status": status
        })

    # -----------------------------
    # SORT RESULTS
    # -----------------------------

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    # -----------------------------
    # SAVE CSV REPORT
    # -----------------------------

    df = pd.DataFrame(results)

    os.makedirs("reports", exist_ok=True)

    df.to_csv(
        "reports/final_report.csv",
        index=False
    )

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------

    return {
        "total_candidates": len(results),
        "ranked_candidates": results
    }