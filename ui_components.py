"""
ui_components.py — Reusable Streamlit UI Components
=====================================================
All display helpers are isolated here so app.py stays clean.
Each function uses st.markdown with unsafe_allow_html=True to render
styled HTML cards, badges, and progress bars.
"""

import streamlit as st


def render_header():
    # FIX 2: Separated the emoji from the gradient text span.
    # Applying -webkit-text-fill-color: transparent to a node that contains
    # an emoji causes the emoji to vanish entirely in most browsers.
    # The emoji is now a sibling element outside the gradient span.
    st.markdown(
        """
        <div class="fade-in" style="text-align:center; padding: 3rem 0 2rem;">
            <h1 style="font-size: 2.8rem; font-weight: 900; margin-bottom: 0.6rem; letter-spacing: -1px;">
                <span style="font-size: 2.8rem;">📄</span>
                <span style="
                    background: linear-gradient(90deg, #6c63ff, #3ecf8e);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                "> AI Resume Reviewer</span>
            </h1>
            <p style="
                color: #334155;
                font-size: 1.15rem;
                max-width: 640px;
                margin: 0 auto;
                line-height: 1.7;
            ">
                Upload your resume, receive intelligent feedback, and optimize it for ATS systems and recruiters.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_gauge(score):
    """
    Render the overall resume score as a large styled badge with a
    colour-coded progress bar beneath it.

    Args:
        score: Numeric score between 0 and 10 (int or float).
    """
    try:
        score = float(score)
        score = max(0.0, min(10.0, score))
    except (TypeError, ValueError):
        score = 0.0

    if score >= 8:
        color = "#3ecf8e"
        label = "Excellent"
        bg = "linear-gradient(135deg, #3ecf8e, #20c997)"
    elif score >= 6:
        color = "#ffa94d"
        label = "Good"
        bg = "linear-gradient(135deg, #ffa94d, #fd7e14)"
    elif score >= 4:
        color = "#ff9f43"
        label = "Needs Work"
        bg = "linear-gradient(135deg, #ff9f43, #ee5a24)"
    else:
        color = "#ff6b6b"
        label = "Poor"
        bg = "linear-gradient(135deg, #ff6b6b, #c0392b)"

    bar_pct = int(score * 10)

    st.markdown(
        f"""
        <div style="text-align:center; padding: 1.2rem 0;">
            <p style="
                font-size: 0.78rem;
                color: #999;
                margin-bottom: 0.5rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            ">Overall Score</p>
            <div style="
                display: inline-block;
                background: {bg};
                color: white;
                font-size: 2.6rem;
                font-weight: 800;
                padding: 0.35rem 1.4rem;
                border-radius: 50px;
                box-shadow: 0 6px 24px rgba(0,0,0,0.15);
                line-height: 1.2;
            ">
                {score:.1f}<span style="font-size:1.1rem; opacity:0.85;">/10</span>
            </div>
            <p style="
                color: {color};
                font-weight: 700;
                font-size: 1rem;
                margin-top: 0.7rem;
                margin-bottom: 0.5rem;
            ">{label}</p>
            <div style="
                background: #e9ecef;
                border-radius: 99px;
                height: 10px;
                width: 220px;
                margin: 0 auto;
                overflow: hidden;
            ">
                <div style="
                    width: {bar_pct}%;
                    height: 10px;
                    border-radius: 99px;
                    background: {bg};
                    transition: width 0.4s ease;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ats_match_score(score):
    """
    Render the ATS keyword match score as a percentage with a coloured bar.

    Args:
        score: Integer 0-100 representing ATS match percentage.
    """
    try:
        score = int(score)
        score = max(0, min(100, score))
    except (TypeError, ValueError):
        score = 0

    if score >= 75:
        color = "#3ecf8e"
        label = "Strong Match"
        bg = "linear-gradient(135deg, #3ecf8e, #20c997)"
    elif score >= 50:
        color = "#ffa94d"
        label = "Moderate Match"
        bg = "linear-gradient(135deg, #ffa94d, #fd7e14)"
    else:
        color = "#ff6b6b"
        label = "Weak Match"
        bg = "linear-gradient(135deg, #ff6b6b, #c0392b)"

    st.markdown(
        f"""
        <div style="text-align:center; padding: 1.2rem 0;">
            <p style="
                font-size: 0.78rem;
                color: #999;
                margin-bottom: 0.5rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            ">ATS Match Score</p>
            <div style="
                display: inline-block;
                background: {bg};
                color: white;
                font-size: 2.6rem;
                font-weight: 800;
                padding: 0.35rem 1.4rem;
                border-radius: 50px;
                box-shadow: 0 6px 24px rgba(0,0,0,0.15);
                line-height: 1.2;
            ">
                {score}<span style="font-size:1.1rem; opacity:0.85;">%</span>
            </div>
            <p style="
                color: {color};
                font-weight: 700;
                font-size: 1rem;
                margin-top: 0.7rem;
                margin-bottom: 0.5rem;
            ">{label}</p>
            <div style="
                background: #e9ecef;
                border-radius: 99px;
                height: 10px;
                width: 220px;
                margin: 0 auto;
                overflow: hidden;
            ">
                <div style="
                    width: {score}%;
                    height: 10px;
                    border-radius: 99px;
                    background: {bg};
                    transition: width 0.4s ease;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str, content: str, color_class: str = ""):
    """
    Render a single feedback section as a styled card with a left accent border.

    Newline characters in content are converted to HTML line-breaks so
    multi-point feedback renders correctly inside the card.

    Args:
        title:       Section heading, may include a leading emoji.
        content:     Text body — newlines become <br> tags.
        color_class: One of: green, red, orange, blue, purple, teal (or empty
                     for the default indigo accent).
    """
    border_colors = {
        "green":  "#3ecf8e",
        "red":    "#ff6b6b",
        "orange": "#ffa94d",
        "blue":   "#4dabf7",
        "purple": "#cc5de8",
        "teal":   "#20c997",
    }
    accent = border_colors.get(color_class, "#6c63ff")

    # Convert newlines to HTML line-breaks for display
    html_body = content.replace("\n", "<br>")

    st.markdown(
        f"""
        <div style="
            background: #ffffff;
            border-radius: 14px;
            padding: 1.3rem 1.6rem;
            margin-bottom: 1.1rem;
            box-shadow: 0 2px 14px rgba(0,0,0,0.055);
            border-left: 5px solid {accent};
        ">
            <div style="
                font-size: 1rem;
                font-weight: 700;
                color: #1a1a2e;
                margin-bottom: 0.55rem;
            ">{title}</div>
            <div style="
                font-size: 0.925rem;
                color: #444;
                line-height: 1.75;
            ">{html_body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_keyword_gaps(found: list, missing: list):
    """
    Render two groups of keyword pills — present (green) and absent (orange).

    Args:
        found:   List of keywords present in both resume and job description.
        missing: List of keywords from the JD that are absent from the resume.
    """
    # FIX 1: Removed gap="medium" — the gap parameter was dropped in
    # Streamlit >= 1.28 and raises TypeError: columns() got an unexpected
    # keyword argument 'gap'
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "<p style='font-weight:700; font-size:0.95rem; margin-bottom:0.5rem;'>"
            "✅ Keywords Found in Resume</p>",
            unsafe_allow_html=True,
        )
        if found:
            pills_html = " ".join(
                f"""<span style="
                    display:inline-block;
                    background:#e8f5e9;
                    color:#2e7d32;
                    border:1px solid #a5d6a7;
                    padding:3px 12px;
                    border-radius:20px;
                    font-size:0.8rem;
                    margin:3px;
                    font-weight:500;
                ">{kw}</span>"""
                for kw in found
            )
            st.markdown(pills_html, unsafe_allow_html=True)
        else:
            st.info("No matching keywords detected.", icon="ℹ️")

    with col2:
        st.markdown(
            "<p style='font-weight:700; font-size:0.95rem; margin-bottom:0.5rem;'>"
            "❌ Missing Keywords (from Job Description)</p>",
            unsafe_allow_html=True,
        )
        if missing:
            pills_html = " ".join(
                f"""<span style="
                    display:inline-block;
                    background:#fff3e0;
                    color:#e65100;
                    border:1px solid #ffcc80;
                    padding:3px 12px;
                    border-radius:20px;
                    font-size:0.8rem;
                    margin:3px;
                    font-weight:500;
                ">{kw}</span>"""
                for kw in missing
            )
            st.markdown(pills_html, unsafe_allow_html=True)
        else:
            st.success("No significant keyword gaps found!", icon="🎉")