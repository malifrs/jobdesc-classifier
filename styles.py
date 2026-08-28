"""CSS theme for the Streamlit UI (kept separate for single responsibility)."""

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
