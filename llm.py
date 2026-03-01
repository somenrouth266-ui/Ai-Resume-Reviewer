"""
llm.py — Multi-Provider LLM Integration
=========================================
Supports Anthropic Claude, Google Gemini, Groq, OpenRouter, and Mistral.
Set the PROVIDER variable below to switch between them.
All providers except Anthropic use the OpenAI-compatible SDK.

Install dependencies:
    pip install anthropic openai
"""

import os

# ── CONFIGURATION — change PROVIDER to switch ────────────────────────────────
# Options: "anthropic" | "gemini" | "groq" | "openrouter" | "mistral"
PROVIDER = "groq"

PROVIDER_CONFIG = {
    "anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "model":       "claude-sonnet-4-6",
        "base_url":    None,
    },
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "model":       "gemini-1.5-flash",
        "base_url":    "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "groq": {
        "api_key_env": "GROQ_API_KEY",
        "model":       "llama-3.1-8b-instant",
        "base_url":    "https://api.groq.com/openai/v1",
    },
    "openrouter": {
        "api_key_env": "OPENROUTER_API_KEY",
        "model":       "mistralai/mistral-7b-instruct",
        "base_url":    "https://openrouter.ai/api/v1",
    },
    "mistral": {
        "api_key_env": "MISTRAL_API_KEY",
        "model":       "mistral-small-latest",
        "base_url":    "https://api.mistral.ai/v1",
    },
}

_MAX_TOKENS = 3000


def _build_prompt(resume_text: str, job_description) -> str:
    """
    Construct the structured prompt sent to the LLM.
    Explicitly forbids arrays — all fields must be plain strings.
    """
    jd_block       = ""
    jd_instruction = ""
    ats_fields     = ""

    if job_description:
        jd_block = f"\n--- JOB DESCRIPTION ---\n{job_description}\n-----------------------\n"
        jd_instruction = (
            "A job description has been provided. "
            "Compute an ATS match score (0-100) and perform keyword gap analysis."
        )
        ats_fields = """
  "ats_match_score": <integer 0-100>,
  "keyword_gap_analysis": {
    "found_keywords": ["keyword1", "keyword2"],
    "missing_keywords": ["keyword3", "keyword4"]
  },"""

    prompt = f"""You are an expert resume coach, ATS specialist, and senior recruiter with 15+ years of experience.

Carefully read the resume below and provide detailed, specific, actionable feedback.
{jd_block}
--- RESUME ---
{resume_text}
--------------

{jd_instruction}

Return ONLY a single valid JSON object. No prose, no markdown, no code fences, no text before or after.

IMPORTANT FORMATTING RULES — you MUST follow these exactly:
- Every field value MUST be a plain STRING — never an array or list
- Use newline characters \\n to separate multiple points within a string
- Do NOT use square brackets [ ] for any field except found_keywords and missing_keywords
- Do NOT wrap the response in ```json or any markdown

Use exactly this JSON structure:

{{
  "overall_score": <integer 1-10>,{ats_fields}
  "strengths": "Point 1\\nPoint 2\\nPoint 3",
  "weaknesses": "Point 1\\nPoint 2\\nPoint 3",
  "ats_optimization_review": "Detailed ATS analysis as a single string with \\n between points",
  "bullet_point_improvements": "Before: old bullet\\nAfter: improved bullet\\n\\nBefore: old bullet 2\\nAfter: improved bullet 2",
  "skills_section_feedback": "Feedback as a single string with \\n between points",
  "grammar_clarity_issues": "Issues found as a single string, or state the resume is clean",
  "final_action_steps": "1. First action\\n2. Second action\\n3. Third action\\n4. Fourth action\\n5. Fifth action"
}}

Additional rules:
- Reference ACTUAL content from the resume — no generic advice
- Be specific, honest, and constructive
- ALL text fields must be strings with \\n separators — NEVER arrays
- Return ONLY the JSON object
"""
    return prompt


def _call_openai_compatible(prompt: str, config: dict) -> str:
    """
    Call any OpenAI-compatible API endpoint.
    Used for Gemini, Groq, OpenRouter, and Mistral.
    """
    from openai import OpenAI

    api_key = os.environ.get(config["api_key_env"], "")
    if not api_key:
        raise EnvironmentError(
            f"{config['api_key_env']} environment variable is not set.\n"
            f"Run: set {config['api_key_env']}=your-key-here"
        )

    client = OpenAI(api_key=api_key, base_url=config["base_url"])
    response = client.chat.completions.create(
        model=config["model"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=_MAX_TOKENS,
    )
    return response.choices[0].message.content


def _call_anthropic(prompt: str, config: dict) -> str:
    """
    Call the Anthropic Claude API using the native anthropic SDK.
    """
    import anthropic

    api_key = os.environ.get(config["api_key_env"], "")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable is not set.\n"
            "Run: set ANTHROPIC_API_KEY=sk-ant-..."
        )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=config["model"],
        max_tokens=_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def analyze_resume(resume_text: str, job_description=None) -> str:
    """
    Analyze a resume using the configured LLM provider.

    Args:
        resume_text:     Extracted plain text of the resume.
        job_description: Optional job posting text for ATS analysis.

    Returns:
        Raw JSON string from the model.

    Raises:
        EnvironmentError: If the API key for the selected provider is not set.
        RuntimeError:     If the API call fails.
        ValueError:       If PROVIDER is set to an unknown value.
    """
    if PROVIDER not in PROVIDER_CONFIG:
        raise ValueError(
            f"Unknown PROVIDER '{PROVIDER}'. "
            f"Choose from: {list(PROVIDER_CONFIG.keys())}"
        )

    config = PROVIDER_CONFIG[PROVIDER]
    prompt = _build_prompt(resume_text, job_description)

    try:
        if PROVIDER == "anthropic":
            return _call_anthropic(prompt, config)
        else:
            return _call_openai_compatible(prompt, config)

    except EnvironmentError:
        raise
    except Exception as exc:
        raise RuntimeError(
            f"API call to '{PROVIDER}' failed: {exc}\n"
            f"Check your API key and network connection."
        ) from exc
