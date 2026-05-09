import os
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    extract_skills,
    load_job_description
)

# -----------------------------------
# LOAD JOB DESCRIPTION
# -----------------------------------

job_description_path = "jd.txt"

job_description = load_job_description(job_description_path)

print("\n===== JOB DESCRIPTION =====\n")
print(job_description[:500])

# -----------------------------------
# RESUME FOLDER
# -----------------------------------

resume_folder = "resumes"

# Check folder exists
if not os.path.exists(resume_folder):
    print("Resume folder not found")
    exit()

# -----------------------------------
# RESULTS LIST
# IMPORTANT: OUTSIDE LOOP
# -----------------------------------

results = []

# -----------------------------------
# PROCESS EACH RESUME
# -----------------------------------

for file_name in os.listdir(resume_folder):

    file_path = os.path.join(resume_folder, file_name)

    resume_text = ""

    print(f"\n\nProcessing Resume: {file_name}")

    # -----------------------------------
    # PDF EXTRACTION
    # -----------------------------------

    if file_name.endswith(".pdf"):

        resume_text = extract_text_from_pdf(file_path)

    # -----------------------------------
    # DOCX EXTRACTION
    # -----------------------------------

    elif file_name.endswith(".docx"):

        resume_text = extract_text_from_docx(file_path)

    else:
        print("Unsupported file")
        continue

    # Skip empty resumes
    if not resume_text.strip():
        print("No text extracted")
        continue

    # -----------------------------------
    # CLEAN TEXT
    # -----------------------------------

    cleaned_resume = clean_text(resume_text)

    print("\n===== RESUME TEXT =====\n")
    print(cleaned_resume[:700])

    # -----------------------------------
    # EXTRACT SKILLS
    # -----------------------------------

    skills = extract_skills(cleaned_resume)

    # -----------------------------------
    # TF-IDF SIMILARITY
    # -----------------------------------

    documents = [job_description, cleaned_resume]

    tfidf = TfidfVectorizer(stop_words='english')

    tfidf_matrix = tfidf.fit_transform(documents)

    similarity_score = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    tfidf_score = similarity_score * 100

    # -----------------------------------
    # REQUIRED SKILLS
    # -----------------------------------

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

    matched_skills = []

    for skill in required_skills:

        if skill in cleaned_resume:
            matched_skills.append(skill)

    # -----------------------------------
    # SKILL MATCH SCORE
    # -----------------------------------

    skill_match_score = (
        len(matched_skills) / len(required_skills)
    ) * 100

    # -----------------------------------
    # FINAL HYBRID SCORE
    # -----------------------------------

    final_score = (
    (0.9 * skill_match_score) +
    (0.1 * tfidf_score)
)

    score_percentage = round(final_score, 2)

    print(f"\nTFIDF Score: {tfidf_score:.2f}")
    print(f"Skill Match Score: {skill_match_score:.2f}")
    print(f"Final Score: {score_percentage:.2f}")

    # -----------------------------------
    # SHORTLIST DECISION
    # -----------------------------------

    if score_percentage >= 80:
        status = "Shortlisted"

    elif score_percentage >= 60:
        status = "Review"

    else:
        status = "Rejected"

    # -----------------------------------
    # APPEND RESULTS
    # -----------------------------------

    results.append({
        "Resume": file_name,
        "Score": score_percentage,
        "Skills": ", ".join(skills),
        "Matched Skills": ", ".join(matched_skills),
        "Status": status
    })

# -----------------------------------
# CREATE DATAFRAME
# -----------------------------------

df = pd.DataFrame(results)

# Empty check
if df.empty:
    print("\nNo resumes processed")
    exit()

# -----------------------------------
# SORT SCORES
# -----------------------------------

df = df.sort_values(by="Score", ascending=False)

# -----------------------------------
# SAVE REPORT
# -----------------------------------

os.makedirs("reports", exist_ok=True)

report_path = "reports/resume_screening_report.csv"

df.to_csv(report_path, index=False)

# -----------------------------------
# FINAL OUTPUT
# -----------------------------------

print("\n\n===== RESUME SCREENING RESULTS =====\n")

print(df)

print(f"\nReport saved at: {report_path}")