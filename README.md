# 📄 AI Resume Reviewer

An AI-powered resume analysis tool built with Streamlit and Groq (LLaMA).

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-resume-reviewer-3dmjtzpi9n7xxrmdngj5ug.streamlit.app)

## Features
- Upload PDF or DOCX resume
- AI analysis via Groq (LLaMA 3.1)
- Overall score (1–10) with visual indicator
- Strengths & Weaknesses
- ATS Optimization Review
- Bullet Point Rewrite Suggestions
- Skills Section Feedback
- Grammar & Clarity Issues
- Prioritized Action Steps
- Bonus: ATS match score + keyword gap analysis (when job description is provided)

## Setup & Run

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Set your API key: `set GROQ_API_KEY=your-key-here`
4. Run: `streamlit run app.py`

## Project Structure
- `app.py` — Main Streamlit application
- `resume_parser.py` — PDF and DOCX text extraction
- `llm.py` — Prompt builder + Groq API integration
- `ui_components.py` — Reusable UI components
- `requirements.txt` — Python dependencies
