import streamlit as st
import pdfplumber
from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import os
import base64
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

job_titles = [
    # --- Entry-Level & Graduate Roles ---
    "Graduate Engineer Trainee", "Graduate Analyst", "Software Intern", "Data Science Intern",
    "Machine Learning Intern", "AI Intern", "DevOps Intern", "Cloud Intern", "Cybersecurity Intern",
    "IT Intern", "Frontend Intern", "Backend Intern", "Web Development Intern",

    # --- Data & AI ---
    "Data Scientist", "Data Analyst", "Data Engineer", "Business Intelligence Analyst",
    "Machine Learning Engineer", "Deep Learning Engineer", "NLP Engineer", "AI Researcher",
    "AI Engineer", "Computer Vision Engineer", "Research Scientist", "ML Ops Engineer",

    # --- Software Engineering ---
    "Software Engineer", "Full Stack Developer", "Frontend Developer", "Backend Developer",
    "Application Developer", "Web Developer", "Mobile App Developer", "Android Developer",
    "iOS Developer", "Game Developer", "Java Developer", "Python Developer", "C++ Developer",

    # --- Cloud & DevOps ---
    "DevOps Engineer", "Site Reliability Engineer", "Cloud Engineer", "Solutions Architect",
    "Cloud Architect", "Infrastructure Engineer", "Platform Engineer", "AWS Engineer", "Azure Engineer",

    # --- Cybersecurity ---
    "Cybersecurity Analyst", "Security Engineer", "Information Security Analyst",
    "Penetration Tester", "Security Consultant", "Network Security Engineer", "Ethical Hacker",

    # --- Product, Design & Management ---
    "Product Manager", "Associate Product Manager", "Project Manager", "Scrum Master",
    "Technical Program Manager", "UX/UI Designer", "UX Researcher", "Design Lead",

    # --- Business & Analytics ---
    "Business Analyst", "BI Developer", "Data Consultant", "Strategy Analyst",
    "Operations Analyst", "Digital Marketing Analyst", "Marketing Data Analyst",

    # --- Quality Assurance & Testing ---
    "QA Engineer", "Test Engineer", "Automation Tester", "Manual Tester", "SDET",

    # --- Hardware & Embedded Systems ---
    "Embedded Systems Engineer", "Robotics Engineer", "Firmware Engineer", "IoT Developer",
    "Hardware Design Engineer", "Mechatronics Engineer",

    # --- IT, Networking & Admin ---
    "Network Engineer", "System Administrator", "Linux Administrator", "Database Administrator",
    "IT Support Specialist", "Technical Support Engineer", "Storage Engineer",

    # --- Specialized & Emerging Tech ---
    "Blockchain Developer", "AR/VR Developer", "Prompt Engineer", "No-Code Developer",
    "Low-Code Developer", "Technical Writer", "Simulation Engineer", "Research Assistant"
]


st.set_page_config(page_title="AI Resume Analyzer")
st.title("🤖 AI Resume Analyzer using OpenAI")

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text.strip()

def check_ats_compatibility(resume_text):
    feedback = []
    if "skills" not in resume_text.lower():
        feedback.append("🟡 Add a 'Skills' section.")
    if "experience" not in resume_text.lower():
        feedback.append("🟡 Add a 'Professional Experience' section.")
    if "education" not in resume_text.lower():
        feedback.append("🟡 Add an 'Education' section.")
    if len(resume_text.split()) < 150:
        feedback.append("🟡 Resume seems too short.")
    if not feedback:
        feedback.append("✅ Resume appears ATS-friendly.")
    return feedback

def summarize_resume(resume_text):
    prompt = f"Summarize this resume in 3-5 concise bullet points:\n\n{resume_text}"
    completion = client.chat.completions.create(
        model="deepseek/deepseek-prover-v2:free",
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "HTTP-Referer": "https://yourdomain.com",
            "X-Title": "AI Resume Analyzer"
        },
    )
    return completion.choices[0].message.content

def analyze_resume_for_role(resume_text, job_title):
    prompt = f"""
You are an AI recruiter. Assess the following resume for the job title: {job_title}.
Provide:
1. Skill match score (0 to 100).
2. Top relevant skills found.
3. Strengths.
4. Suggestions for improvement.

Resume:
{resume_text}
"""
    completion = client.chat.completions.create(
        model="deepseek/deepseek-prover-v2:free",
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "HTTP-Referer": "https://yourdomain.com",
            "X-Title": "AI Resume Analyzer"
        },
    )
    return completion.choices[0].message.content

def generate_pdf_report(summary, analysis, ats_feedback):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'C:\\xampp\\htdocs\\project\\html\\Resumeeee\\DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, "🧾 AI Resume Analysis Report\n\n")
    pdf.multi_cell(0, 10, f"🔹 Summary:\n{summary}\n")
    pdf.multi_cell(0, 10, f"🔹 Analysis:\n{analysis}\n")
    pdf.multi_cell(0, 10, f"🔹 ATS Compatibility Feedback:\n" + '\n'.join(ats_feedback))
    report_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(report_file.name)
    return report_file.name

st.sidebar.header("📄 Upload Resume")
uploaded_file = st.sidebar.file_uploader("Upload PDF Resume", type=["pdf"])
job_title = st.sidebar.selectbox("🎯 Target Job Role", ["Select"] + job_titles)

if uploaded_file and job_title != "Select":
    with st.spinner("Analyzing your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        ats_feedback = check_ats_compatibility(resume_text)
        summary = summarize_resume(resume_text)
        analysis = analyze_resume_for_role(resume_text, job_title)

        report_path = generate_pdf_report(summary, analysis, ats_feedback)

        st.subheader("✅ Summary")
        st.write(summary)

        st.subheader("🧠 Job Fit Analysis")
        st.markdown(analysis, unsafe_allow_html=False)

        st.subheader("📌 ATS Feedback")
        st.write("\n".join(ats_feedback))

        with open(report_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f'<a href="data:application/octet-stream;base64,{b64}" download="Resume_Report.pdf">📥 Download Full Report</a>',
                unsafe_allow_html=True
            )

elif uploaded_file and job_title == "Select":
    st.warning("⚠️ Please select a job title to analyze your resume.")
