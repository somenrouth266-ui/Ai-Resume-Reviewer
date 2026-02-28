"""
AI-Powered Resume Reviewer — app.py
====================================
Main Streamlit application. Orchestrates file upload, text extraction,
LLM analysis, and structured result display.
"""

import streamlit as st
import json
import re

from resume_parser import extract_text_from_pdf, extract_text_from_docx
from llm import analyze_resume
from ui_components import (
    render_header,
    render_score_gauge,
    render_section,
    render_keyword_gaps,
    render_ats_match_score,
)

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Reviewer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #eef2ff, #f8fafc);
    }

    h1, h2, h3 {
        color: #1e293b !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    p {
        color: #334155;
    }

    section[data-testid="stFileUploader"] {
        border: 2px dashed #6c63ff;
        border-radius: 14px;
        padding: 1rem;
        background: white;
        transition: all 0.3s ease;
    }

    section[data-testid="stFileUploader"]:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 30px rgba(108,99,255,0.15);
    }

    .section-card {
        background: white;
        border-radius: 18px;
        padding: 1.6rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    body {
        background-color: #f8fafc;
    }

    .section-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
    }

    .fade-in {
        animation: fadeInUp 0.7s ease forwards;
        opacity: 0;
    }

    @keyframes fadeInUp {
        from { transform: translateY(20px); opacity: 0; }
        to   { transform: translateY(0);    opacity: 1; }
    }

    div.stButton > button {
        background: linear-gradient(135deg, #6c63ff, #3ecf8e);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.8rem 2.2rem;
        font-size: 1rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(62,207,142,0.4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Page header ───────────────────────────────────────────────────────────────
render_header()

# ── Input row ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### 📤 Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Drag & drop or click to browse",
        type=["pdf", "docx"],
        label_visibility="collapsed",
    )

with col_right:
    st.markdown("### 🎯 Job Description *(optional)*")
    job_description = st.text_area(
        "Paste the job posting here for ATS keyword analysis",
        height=160,
        label_visibility="collapsed",
        placeholder="Paste the full job description here to get ATS match score and keyword gap analysis...",
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ── Analyze button ────────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze_clicked = st.button("🔍 Analyze My Resume", use_container_width=True)

# ── Helper: robust JSON extractor ────────────────────────────────────────────
def extract_json(raw: str) -> dict:
    """
    Robustly extract a JSON object from the LLM response.
    Handles:
      - Markdown code fences (```json ... ```)
      - Prose before/after the JSON object
      - Lists returned instead of strings for text fields
    """
    text = raw.strip()

    # 1. Strip markdown code fences
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    text = text.strip()

    # 2. Extract the JSON object — find outermost { ... }
    start = text.find("{")
    end   = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")
    text = text[start : end + 1]

    # 3. Parse
    data = json.loads(text)

    # 4. Normalise list fields → newline-joined string
    list_fields = [
        "strengths", "weaknesses", "ats_optimization_review",
        "bullet_point_improvements", "skills_section_feedback",
        "grammar_clarity_issues", "final_action_steps",
    ]
    for field in list_fields:
        if field in data and isinstance(data[field], list):
            data[field] = "\n".join(str(i) for i in data[field])

    return data


# ── Core workflow ─────────────────────────────────────────────────────────────
if analyze_clicked:

    # 1. Validate upload
    if not uploaded_file:
        st.warning("⚠️ Please upload a resume (PDF or DOCX) before analyzing.")
        st.stop()

    # 2. Extract text from the uploaded file
    with st.spinner("📖 Extracting resume text..."):
        try:
            file_bytes = uploaded_file.read()
            fname = uploaded_file.name.lower()

            if fname.endswith(".pdf"):
                resume_text = extract_text_from_pdf(file_bytes)
            elif fname.endswith(".docx"):
                resume_text = extract_text_from_docx(file_bytes)
            else:
                st.error("Unsupported file type. Please upload a PDF or DOCX.")
                st.stop()

            if not resume_text.strip():
                st.error(
                    "Could not extract text. The file may be a scanned image. "
                    "Please use a text-based PDF or DOCX."
                )
                st.stop()

        except Exception as exc:
            st.error(f"File parsing error: {exc}")
            st.stop()

    # 3. Send to LLM for analysis
    with st.spinner("🤖 AI is reviewing your resume — this may take 15–30 seconds..."):
        try:
            raw_response = analyze_resume(
                resume_text,
                job_description.strip() or None,
            )
        except Exception as exc:
            st.error(f"AI analysis error: {exc}")
            st.stop()

    # 4. Parse the structured JSON from the LLM response
    try:
        feedback = extract_json(raw_response)
    except (json.JSONDecodeError, ValueError) as exc:
        st.error("The AI returned an unexpected format. Please try again.")
        with st.expander("Raw AI response (debug)"):
            st.text(raw_response)
        st.stop()

    # 5. Display results ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📊 Resume Analysis Results")
    st.markdown("<hr>", unsafe_allow_html=True)

    score_col, ats_col = st.columns([1, 1])
    with score_col:
        render_score_gauge(feedback.get("overall_score", 0))
    with ats_col:
        if job_description.strip() and "ats_match_score" in feedback:
            render_ats_match_score(feedback["ats_match_score"])

    st.markdown("<hr>", unsafe_allow_html=True)

    sections = [
        ("✅ Strengths",                 "strengths",                "green"),
        ("⚠️ Weaknesses",                "weaknesses",               "red"),
        ("🤖 ATS Optimization Review",   "ats_optimization_review",  "blue"),
        ("📌 Bullet Point Improvements", "bullet_point_improvements", "orange"),
        ("🛠️ Skills Section Feedback",   "skills_section_feedback",   "purple"),
        ("✍️ Grammar & Clarity Issues",  "grammar_clarity_issues",    "teal"),
        ("🚀 Final Action Steps",        "final_action_steps",        ""),
    ]

    for title, key, color in sections:
        content = feedback.get(key, "")
        if content:
            render_section(title, content, color)

    # Keyword gap analysis (only when job description was provided)
    if job_description.strip() and "keyword_gap_analysis" in feedback:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 🔑 Keyword Gap Analysis")
        kga = feedback["keyword_gap_analysis"]
        render_keyword_gaps(
            kga.get("found_keywords", []),
            kga.get("missing_keywords", []),
        )

    st.success("✅ Analysis complete! Use the feedback above to level up your resume.")
