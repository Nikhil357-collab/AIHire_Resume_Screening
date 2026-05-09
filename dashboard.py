import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests


# FastAPI URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Resume Screening",
    layout="wide"
)

st.title("📄 AI Resume Screening Dashboard")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Upload Resume",
        "Results"
    ]
)
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
    font-size: 16px;
}

.stDataFrame {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
# Store Results
if "results" not in st.session_state:
    st.session_state.results = []

# ---------------- UPLOAD ---------------- #
# Store uploaded results
if "results" not in st.session_state:
    st.session_state.results = []
    
if menu == "Upload Resume":

    st.subheader("Upload Candidate Resume")

    uploaded_file = st.file_uploader(
        "Choose Resume",
        type=["pdf", "docx"]
    )

    if uploaded_file is not None:

        if st.button("Upload & Analyze"):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            response = requests.post(
                f"{API_URL}/upload_resume/",
                files=files
            )

            if response.status_code == 200:

                result = response.json()

                st.success("Resume Uploaded Successfully!")

                st.write("### Analysis Result")

                st.write(f"📄 File: {result['filename']}")
                st.write(f"⭐ Score: {result['score']}")
                st.write(f"✅ Status: {result['status']}")

                st.session_state.results.append(result)

            else:
                st.error("API Connection Failed")

# ---------------- RESULTS ---------------- #
elif menu == "Results":

    st.subheader("📊 Resume Rankings")

    if len(st.session_state.results) > 0:

        df = pd.DataFrame(st.session_state.results)

        df = df.sort_values(
            by="score",
            ascending=False
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        st.bar_chart(df.set_index("filename")["score"])

    else:
        st.warning("No resumes analyzed yet.")

option = st.sidebar.selectbox(
    "Select Option",
    [
        "Overview",
        "Resume Rankings",
        "Skills Analysis",
        "Upload Resume"
    ]
)

# Dummy Data
data = {
    "Candidate": [
        "Rahul",
        "Aman",
        "Sneha",
        "Priya",
        "Vikas"
    ],
    "Score": [92, 85, 78, 95, 88],
    "Skills": [
        "Python, ML, SQL",
        "Java, Spring",
        "Python, AI",
        "Data Science, ML",
        "React, NodeJS"
    ]
}

df = pd.DataFrame(data)

# ---------------- OVERVIEW ---------------- #

if option == "Overview":

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Resumes", len(df))
    col2.metric("Top Score", df["Score"].max())
    col3.metric("Average Score", round(df["Score"].mean(), 2))

    st.subheader("Resume Scores")

    fig = px.bar(
        df,
        x="Candidate",
        y="Score",
        color="Score",
        text="Score"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- RANKINGS ---------------- #

elif option == "Resume Rankings":

    st.subheader("Candidate Rankings")

    ranked_df = df.sort_values(by="Score", ascending=False)

    st.dataframe(ranked_df, use_container_width=True)

# ---------------- SKILLS ---------------- #

elif option == "Skills Analysis":

    st.subheader("Skills Distribution")

    skills_list = []

    for skills in df["Skills"]:
        skills_list.extend(skills.split(", "))

    skill_df = pd.DataFrame(
        skills_list,
        columns=["Skill"]
    )

    skill_count = skill_df["Skill"].value_counts().reset_index()

    skill_count.columns = ["Skill", "Count"]

    fig = px.pie(
        skill_count,
        names="Skill",
        values="Count",
        title="Skills Analysis"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- UPLOAD ---------------- #

elif option == "Upload Resume":

    st.subheader("Upload Candidate Resume")

    uploaded_file = st.file_uploader(
        "Choose Resume",
        type=["pdf", "docx"]
    )

    if uploaded_file:

        os.makedirs("uploaded_resumes", exist_ok=True)

        save_path = os.path.join(
            "uploaded_resumes",
            uploaded_file.name
        )

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"{uploaded_file.name} uploaded successfully!")

        st.info("Resume ready for screening.")