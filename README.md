# 📄 AI Resume Reviewer

An AI-powered resume review web application built with Python, Streamlit, and Claude (Anthropic).

## Project Structure

```
resume_reviewer/
├── app.py            # Main Streamlit application (UI, routing)
├── parser_utils.py   # PDF and DOCX text extraction
├── llm.py            # Prompt builder + Claude API integration
├── display.py        # Feedback parser and section renderer
├── requirements.txt  # Python dependencies
└── README.md
```

## Features

- 📤 Upload PDF or DOCX resume
- 🤖 AI analysis via Claude (Anthropic)
- 📊 Overall score (1–10) with visual indicator
- ✅ Strengths & ⚠️ Weaknesses
- 🤖 ATS Optimization Review
- ✏️ Bullet Point Rewrite Suggestions
- 🛠️ Skills Section Feedback
- ✍️ Grammar & Clarity Issues
- 🚀 Prioritized Action Steps
- 🎯 **Bonus:** ATS match score + keyword gap analysis (when job description is provided)

## Setup & Run

### 1. Clone / download the project

```bash
cd resume_reviewer
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Anthropic API key

**Option A – Environment variable (recommended for production):**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."    # macOS/Linux
set ANTHROPIC_API_KEY=sk-ant-...         # Windows CMD
$env:ANTHROPIC_API_KEY="sk-ant-..."      # Windows PowerShell
```

**Option B – Enter it in the sidebar** when the app is running.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

## Usage

1. Enter your Anthropic API key in the left sidebar (if not set via env variable)
2. Upload your resume (PDF or DOCX)
3. Optionally paste a job description for ATS match analysis
4. Click **"🔍 Analyze Resume"**
5. Review the structured feedback sections

## API Key

Get your Anthropic API key at: https://console.anthropic.com/
