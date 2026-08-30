import time
from html import escape

import streamlit as st

from core import MIN_CHARS, AnalysisResult, create_analyzer

st.set_page_config(
    page_title="JobDesc Classifier",
    page_icon=":material/work:",
    layout="wide",
)

MAX_CHARS = 5000

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

:root {
  --primary: #036c55;
  --primary-dim: #005f4a;
  --on-primary: #e4fff3;
  --surface: #f6faf6;
  --surface-low: #eff5f0;
  --surface-lowest: #ffffff;
  --surface-variant: #dae5df;
  --on-surface: #2b3530;
  --on-surface-variant: #57615d;
  --secondary-container: #cee9dd;
  --on-secondary-container: #3f574e;
  --outline-variant: #aab4af;
}

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
}

[data-testid="stIconMaterial"] {
  font-family: 'Material Symbols Rounded', sans-serif;
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  vertical-align: middle;
}

header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }

.block-container {
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
  max-width: 100%;
}

.jd-appbar {
  position: sticky;
  top: 0;
  z-index: 999;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 0;
  margin-bottom: 2.5rem;
  background: rgba(246, 250, 246, 0.8);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(170, 180, 175, 0.15);
}
.jd-appbar .material-symbols-outlined { color: var(--primary); }
.jd-appbar-title {
  font-family: 'Manrope', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--on-surface);
}

.jd-hero-text h1 {
  font-family: 'Manrope', sans-serif;
  font-size: 1.75rem;
  line-height: 2.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--on-surface);
  margin: 0 0 0.75rem 0;
}
.jd-hero-text p {
  color: var(--on-surface-variant);
  max-width: 28rem;
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

[data-testid="stVerticalBlock"].st-key-input_card {
  background: var(--surface-low);
  border: none;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

div[data-testid="stTextArea"] label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--on-surface);
  margin-bottom: 0.5rem;
}
div[data-testid="stTextArea"] textarea {
  background: var(--surface-lowest);
  border: 1px solid rgba(170, 180, 175, 0.2);
  border-radius: 0.5rem;
  color: var(--on-surface);
  font-family: 'Inter', sans-serif;
}
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(3, 108, 85, 0.2);
}
div[data-testid="stTextArea"] textarea::placeholder {
  color: rgba(87, 97, 93, 0.6);
}

div.st-key-predict_btn button {
  width: 100%;
  background-image: linear-gradient(90deg, var(--primary), var(--primary-dim));
  color: var(--on-primary);
  font-weight: 600;
  border-radius: 0.5rem;
  padding: 0.875rem 1rem;
  border: none;
  box-shadow: 0 10px 20px rgba(3, 108, 85, 0.12);
  transition: opacity 0.15s ease, transform 0.15s ease;
}
div.st-key-predict_btn button:hover {
  opacity: 0.9;
  color: var(--on-primary);
  background-image: linear-gradient(90deg, var(--primary), var(--primary-dim));
}
div.st-key-predict_btn button:active { transform: scale(0.99); }

div.st-key-clear_btn button {
  background: transparent;
  border: none;
  color: var(--on-surface-variant);
  padding: 0;
  font-size: 0.875rem;
}
div.st-key-clear_btn button:hover {
  color: var(--on-surface);
  background: transparent;
  border: none;
}

.jd-counter {
  text-align: right;
  font-size: 0.75rem;
  color: var(--on-surface-variant);
}

.jd-empty {
  border: 2px dashed rgba(170, 180, 175, 0.25);
  border-radius: 0.75rem;
  padding: 5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.jd-empty .material-symbols-outlined {
  font-size: 48px;
  color: rgba(87, 97, 93, 0.4);
  margin-bottom: 1rem;
}
.jd-empty p { color: var(--on-surface-variant); font-weight: 500; margin: 0; }
.jd-empty .sub { color: rgba(87, 97, 93, 0.6); font-size: 0.875rem; margin-top: 0.25rem; }

.jd-hero {
  background: var(--surface-lowest);
  border: 1px solid rgba(170, 180, 175, 0.1);
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 24px 48px rgba(43, 53, 48, 0.06);
}
.jd-eyebrow {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--on-surface-variant);
  margin-bottom: 0.75rem;
}
.jd-hero h2 {
  font-family: 'Manrope', sans-serif;
  font-size: 2.25rem;
  line-height: 2.5rem;
  font-weight: 800;
  color: var(--primary);
  margin: 0 0 1.25rem 0;
}
.jd-subrole {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.5rem;
  margin-top: 0.25rem;
}
.jd-subrole-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--on-surface-variant);
}
.jd-subrole-value {
  font-family: 'Manrope', sans-serif;
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--on-surface);
}
.jd-onet {
  font-size: 0.75rem;
  color: var(--on-surface-variant);
  background: var(--surface-variant);
  padding: 0.15rem 0.55rem;
  border-radius: 9999px;
}

.jd-card {
  background: var(--surface-low);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-top: 1.5rem;
}
.jd-card h3 {
  font-family: 'Manrope', sans-serif;
  color: var(--on-surface);
  font-weight: 700;
  font-size: 1rem;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.jd-card h3 .material-symbols-outlined { color: var(--primary); font-size: 20px; }
.jd-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.jd-chip {
  background: var(--secondary-container);
  color: var(--on-secondary-container);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}
.jd-chip-empty {
  color: var(--on-surface-variant);
  font-style: italic;
  font-size: 0.85rem;
}

.jd-rank-list { display: flex; flex-direction: column; gap: 1rem; }
.jd-rank-item { display: flex; gap: 0.75rem; align-items: flex-start; }
.jd-rank-pos {
  flex-shrink: 0;
  width: 1.5rem; height: 1.5rem;
  display: flex; align-items: center; justify-content: center;
  background: var(--secondary-container);
  color: var(--on-secondary-container);
  border-radius: 9999px;
  font-size: 0.75rem; font-weight: 700;
  font-family: 'Manrope', sans-serif;
}
.jd-rank-body { flex-grow: 1; min-width: 0; }
.jd-rank-name {
  font-size: 0.9rem; font-weight: 600; color: var(--on-surface);
  line-height: 1.3;
}
.jd-rank-meta {
  font-size: 0.72rem; color: var(--on-surface-variant);
  margin-top: 0.15rem;
}
.jd-rank-bar {
  height: 0.375rem;
  background: var(--surface-variant);
  border-radius: 9999px;
  overflow: hidden;
  margin-top: 0.4rem;
}
.jd-rank-bar-fill { height: 100%; background: var(--primary); border-radius: 9999px; }

.jd-gap { height: 0.5rem; }

.jd-footer {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 0;
  margin-top: 2.5rem;
  border-top: 1px solid rgba(170, 180, 175, 0.15);
  color: var(--on-surface-variant);
  font-size: 0.75rem;
}
.jd-footer-links { display: flex; gap: 1.5rem; }
.jd-footer-links a { color: var(--on-surface-variant); text-decoration: none; transition: color 0.15s ease; }
.jd-footer-links a:hover { color: var(--on-surface); }
@media (min-width: 640px) {
  .jd-footer { flex-direction: row; }
}
"""


@st.cache_resource(show_spinner="Loading model...")
def get_analyzer():
    """Load the trained model bundle once and reuse it for every request."""
    return create_analyzer()


def render_hero(result: AnalysisResult) -> None:
    """Render the predicted job category hero card with the sub-role and O*NET code."""
    sub_role = result["sub_role"] or "Not available"
    onet_code = result["onet_code"] or "—"
    st.html(
        f"""
        <div class="jd-hero">
          <span class="jd-eyebrow">Predicted job category</span>
          <h2>{escape(result["main_role"])}</h2>
          <div class="jd-subrole">
            <span class="jd-subrole-label">Sub-role</span>
            <span class="jd-subrole-value">{escape(sub_role)}</span>
            <span class="jd-onet">{escape(onet_code)}</span>
          </div>
        </div>
        """
    )


def render_skill_card(icon: str, title: str, chips: list[str]) -> None:
    """Render a card with skill chips, or an empty-state message when none match."""
    if chips:
        chips_html = "".join(
            f'<span class="jd-chip">{escape(chip)}</span>' for chip in chips
        )
    else:
        chips_html = '<span class="jd-chip-empty">No O*NET skills were recognised in this text.</span>'
    st.html(
        f"""
        <div class="jd-card">
          <h3><span class="material-symbols-outlined">{icon}</span>{escape(title)}</h3>
          <div class="jd-chips">{chips_html}</div>
        </div>
        """
    )


def render_subroles_card(items: list) -> None:
    """Render the top O*NET sub-role candidates ranked by cosine similarity."""
    if not items:
        return
    max_sim = max((it["cosine_similarity"] for it in items), default=0.0) or 1.0
    rows = ""
    for i, it in enumerate(items, 1):
        sim = it["cosine_similarity"]
        width = (sim / max_sim * 100) if max_sim > 0 else 0
        rows += (
            f'<div class="jd-rank-item">'
            f'<span class="jd-rank-pos">{i}</span>'
            f'<div class="jd-rank-body">'
            f'<div class="jd-rank-name">{escape(it["sub_role"])}</div>'
            f'<div class="jd-rank-meta">{escape(it["onet_code"])} · {sim * 100:.1f}%</div>'
            f'<div class="jd-rank-bar"><div class="jd-rank-bar-fill" style="width:{width:.1f}%"></div></div>'
            f'</div></div>'
        )
    st.html(
        f"""
        <div class="jd-card">
          <h3><span class="material-symbols-outlined">account_tree</span>Top sub-roles</h3>
          <div class="jd-rank-list">{rows}</div>
        </div>
        """
    )


def render_role_ranking_card(items: list) -> None:
    """Render the top role candidates ranked by SVM decision-function margin.

    Margins are not probabilities, so only a relative bar (normalized across the
    shown candidates) is drawn and no numeric value is displayed.
    """
    if not items:
        return
    margins = [it["margin"] for it in items]
    lo, hi = min(margins), max(margins)
    span = (hi - lo) or 1.0
    rows = ""
    for i, it in enumerate(items, 1):
        width = (it["margin"] - lo) / span * 100
        rows += (
            f'<div class="jd-rank-item">'
            f'<span class="jd-rank-pos">{i}</span>'
            f'<div class="jd-rank-body">'
            f'<div class="jd-rank-name">{escape(it["role"])}</div>'
            f'<div class="jd-rank-bar"><div class="jd-rank-bar-fill" style="width:{width:.1f}%"></div></div>'
            f'</div></div>'
        )
    st.html(
        f"""
        <div class="jd-card">
          <h3><span class="material-symbols-outlined">leaderboard</span>Role ranking</h3>
          <div class="jd-rank-list">{rows}</div>
        </div>
        """
    )


def render_results(result: AnalysisResult) -> None:
    """Render the full results panel: hero, skills, top sub-roles, and role ranking."""
    render_hero(result)
    st.html('<div class="jd-gap"></div>')
    render_skill_card("bolt", "Skills", [s["skill"] for s in result["skills"]])
    left, right = st.columns(2, gap="medium")
    with left:
        render_subroles_card(result["top_3_sub_role"])
    with right:
        render_role_ranking_card(result["top_3_role_margins"])


def render_empty_state() -> None:
    st.html(
        """
        <div class="jd-empty">
          <span class="material-symbols-outlined">inbox</span>
          <p>Your prediction will appear here</p>
          <p class="sub">Enter a job description and hit Predict to see the classification.</p>
        </div>
        """
    )


def clear_input() -> None:
    """Reset the input and clear any stored result so the empty state reappears."""
    st.session_state.jd_input = ""
    st.session_state.phase = "empty"
    st.session_state.pop("result", None)
    st.session_state.pop("pending_text", None)


st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

if "phase" not in st.session_state:
    st.session_state.phase = "empty"

st.html(
    """
    <div class="jd-appbar">
      <span class="material-symbols-outlined">work</span>
      <span class="jd-appbar-title">JobDesc Classifier</span>
    </div>
    """
)

left, right = st.columns([5, 7], gap="large")

with left:
    st.html(
        """
        <div class="jd-hero-text">
          <h1>Job description classifier</h1>
          <p>Paste your raw job description text below. Our model will decompose the requirements and classify the career archetype.</p>
        </div>
        """
    )

    with st.container(border=True, key="input_card"):
        st.text_area(
            "Job description",
            key="jd_input",
            placeholder="Paste a job description here...",
            max_chars=MAX_CHARS,
            height=240,
            width="stretch",
        )
        clear_col, counter_col = st.columns([1, 1], vertical_alignment="center")
        with clear_col:
            st.button(
                "Clear",
                key="clear_btn",
                icon=":material/close:",
                width="stretch",
                on_click=clear_input,
            )
        with counter_col:
            st.html(
                f'<div class="jd-counter">{len(st.session_state.jd_input)} / {MAX_CHARS}</div>'
            )

        if st.button(
            "Predict",
            key="predict_btn",
            type="primary",
            icon=":material/analytics:",
            width="stretch",
            disabled=st.session_state.phase == "loading",
        ):
            text = st.session_state.jd_input.strip()
            if not text:
                st.toast("Please paste a job description first.", icon=":material/info:")
            elif len(text) < MIN_CHARS:
                st.toast(
                    f"Job description is too short. Please enter at least {MIN_CHARS} "
                    f"characters (currently {len(text)}).",
                    icon=":material/info:",
                )
            else:
                st.session_state.phase = "loading"
                st.session_state.pending_text = text

with right:
    if st.session_state.phase == "loading":
        with st.status("Analyzing job description...", expanded=True) as status:
            analyzer = get_analyzer()
            st.write("Classifying role and matching O*NET occupation...")
            start = time.perf_counter()
            st.session_state.result = analyzer.analyze(st.session_state.pending_text)
            st.session_state.duration = time.perf_counter() - start
            status.update(label="Analysis complete", state="complete", expanded=False)
        st.session_state.phase = "results"
        st.rerun()
    elif st.session_state.phase == "results":
        result = st.session_state.get("result")
        if result:
            render_results(result)
        else:
            render_empty_state()
    else:
        render_empty_state()

st.html(
    """
    <footer class="jd-footer">
      <span>© 2026 JobDesc Classifier. All rights reserved.</span>
      <div class="jd-footer-links">
        <a href="#">Privacy Policy</a>
        <a href="#">Methodology</a>
        <a href="#">Support</a>
      </div>
    </footer>
    """
)
