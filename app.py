"""Web UI for the JobDesc Classifier (Streamlit).

The app stores no data. Every request is processed in memory and the result is
shown immediately, with nothing persisted to a database or file.
"""

import time
from html import escape

import streamlit as st

from analisis import MIN_CHARS, AnalysisResult, load_classifier

# --- Page config must be the first Streamlit call in the file ---
st.set_page_config(page_title="JobDesc Classifier", layout="wide")

# --- CSS theme for the app (green palette, custom cards & buttons) ---
STYLES = """
<style>
    :root {
        --green: #0A6B4E;
        --green-dark: #0F4A38;
        --bg: #F1F6F3;
        --panel: #E7F0EA;
        --chip: #CDE7D8;
        --muted: #5B6B63;
    }
    .stApp { background: var(--bg); }
    header[data-testid="stHeader"], #MainMenu, footer { display: none; }
    .block-container { padding: 2.5rem 4rem 4rem; max-width: 1500px; }

    .topbar { display: flex; align-items: center; gap: 3rem; margin-bottom: 3.5rem; }
    .brand { font-size: 1.25rem; font-weight: 700; color: var(--green); }
    .menu {
        font-size: .95rem; font-weight: 600; color: var(--green);
        border-bottom: 2px solid var(--green); padding-bottom: .25rem;
    }

    .title { font-size: 2rem; font-weight: 600; color: #1B2A22; margin-bottom: .75rem; }
    .description { font-size: 1rem; color: var(--muted); line-height: 1.6; margin-bottom: 2rem; }

    /* Input panel */
    div[data-testid="stTextArea"] textarea {
        background: var(--panel); border: none; border-radius: 12px;
        min-height: 320px; font-size: 1rem; color: #1B2A22; padding: 1.25rem;
    }
    div[data-testid="stTextArea"] textarea::placeholder { color: #7C8C84; }
    div[data-testid="stTextArea"] label { display: none; }

    /* Descendant selectors (not direct child) because Streamlit wraps buttons
       inside an extra div. */
    div[data-testid="stButton"] button, .stButton button {
        background: var(--green); color: #fff; border: none; border-radius: 10px;
        padding: .85rem 1rem; font-size: 1.05rem; font-weight: 600; min-height: 3rem;
    }
    div[data-testid="stButton"] button:hover, .stButton button:hover {
        background: var(--green-dark); color: #fff; border: none;
    }
    div[data-testid="stButton"] button p, .stButton button p {
        font-size: 1.05rem; font-weight: 600;
    }

    /* Output cards */
    .card-primary {
        background: #fff; border-radius: 14px; padding: 2rem 2.25rem; margin-bottom: 1.5rem;
    }
    .label-small {
        font-size: .75rem; letter-spacing: .12em; text-transform: uppercase;
        color: var(--muted); margin-bottom: .6rem;
    }
    .role { font-size: 2.5rem; font-weight: 700; color: var(--green); line-height: 1.1; }
    .duration { margin-top: .9rem; font-size: .8rem; color: var(--muted); }

    .card { background: var(--panel); border-radius: 14px; padding: 1.5rem 1.75rem; margin-bottom: 1.25rem; }
    .card-title { font-size: 1rem; font-weight: 700; color: #1B2A22; margin-bottom: 1rem; }
    .content { font-size: 1.05rem; color: #1B2A22; }

    .chip {
        display: inline-block; background: var(--chip); color: var(--green-dark);
        border-radius: 999px; padding: .35rem .8rem; margin: 0 .4rem .5rem 0; font-size: .85rem;
    }
    .empty { color: var(--muted); font-style: italic; }
</style>
"""

# Apply the CSS theme to the page.
st.markdown(STYLES, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading model...")
def get_classifier():
    """Load the trained model bundle once and reuse it for every request."""
    return load_classifier()


def render_topbar() -> None:
    """Render the brand name and menu bar at the top of the page."""
    st.markdown(
        '<div class="topbar"><span class="brand">JobDesc Classifier</span>'
        '<span class="menu">Dashboard</span></div>',
        unsafe_allow_html=True,
    )


def render_input_panel() -> tuple[str, bool]:
    """Render the title, description, textarea, and Predict button; return the text and click state."""
    st.markdown('<div class="title">Job description classifier</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="description">Paste your raw job description text below. Our model will '
        "decompose the requirements and classify the career archetype.</div>",
        unsafe_allow_html=True,
    )
    text = st.text_area(
        "Job description",
        placeholder="Input your job description here...",
        key="input",
    )
    # width="stretch" must be set explicitly because Streamlit defaults to
    # "content", which makes the button shrink to fit its label width.
    clicked = st.button("Predict", width="stretch")
    return text, clicked


def run_prediction(text: str, clicked: bool) -> None:
    """Validate the input and run analysis, storing the result in session state."""
    if not clicked:
        return

    cleaned = text.strip()
    if not cleaned:
        st.session_state["result"] = None
        st.session_state["message"] = "The input field is empty. Please enter a job description first."
        return

    if len(cleaned) < MIN_CHARS:
        st.session_state["result"] = None
        st.session_state["message"] = (
            f"The job description is too short. Please enter at least {MIN_CHARS} characters "
            f"(currently {len(cleaned)})."
        )
        return

    # Time only the analysis step (after the model is in memory) so the shown
    # number reflects the per-listing compute cost, not the one-time load cost.
    start = time.perf_counter()
    st.session_state["result"] = get_classifier().analyze(cleaned)
    st.session_state["duration"] = time.perf_counter() - start
    st.session_state["message"] = None


def render_skills(skills: list) -> None:
    """Render the list of matched skills as chips (or an empty-state message)."""
    if skills:
        chips = "".join(
            f'<span class="chip">{escape(s["skill"])}</span>' for s in skills
        )
    else:
        chips = '<span class="empty">No O*NET skills were recognised in this text.</span>'
    st.markdown(
        f'<div class="card"><div class="card-title">Skills</div>{chips}</div>',
        unsafe_allow_html=True,
    )


def render_results() -> None:
    """Render the prediction results (role card, sub-role, skills) or a warning."""
    message = st.session_state.get("message")
    result: AnalysisResult | None = st.session_state.get("result")

    if message:
        st.warning(message)
        return

    if not result:
        return

    duration = st.session_state.get("duration")
    duration_note = (
        f'<div class="duration">Processed in {duration:.2f} seconds</div>'
        if duration is not None
        else ""
    )
    st.markdown(
        '<div class="card-primary">'
        '<div class="label-small">Predicted job category</div>'
        f'<div class="role">{escape(result["main_role"])}</div>'
        f"{duration_note}"
        "</div>",
        unsafe_allow_html=True,
    )

    sub_role = result["sub_role"] or "Not available"
    st.markdown(
        '<div class="card"><div class="card-title">Sub-role</div>'
        f'<div class="content">{escape(sub_role)}</div></div>',
        unsafe_allow_html=True,
    )

    # Skills are already sorted by weight; the weight value itself is not shown.
    render_skills(result["skills"])


def main() -> None:
    """App entry point: render the top bar, two-column layout, input, and results."""
    render_topbar()

    left, right = st.columns(2, gap="large")

    with left:
        text, clicked = render_input_panel()

    run_prediction(text, clicked)

    with right:
        render_results()


main()
