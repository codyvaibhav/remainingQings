import streamlit as st
import config  # ← import module so config.main always reflects the active model
import warnings

warnings.filterwarnings('ignore', category=UserWarning, message="Workbook contains no default style*")

# ── Model Selection (runs first, before any UI renders) ───────────────────────
_model_keys = list(config.MODELS.keys())
_model_labels = {k: config.MODELS[k]['label'] for k in _model_keys}

if 'active_model' not in st.session_state:
    st.session_state.active_model = _model_keys[0]

# Apply selected model config on every rerun so all globals are up-to-date
config.configure(st.session_state.active_model)

# ── CSS ───────────────────────────────────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── NEW: subtle app-wide background + small polish (header/nav untouched) ────
st.markdown(
    """
    <style>
    /* Soft gradient + faint dotted texture behind the whole app */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 15% 0%, rgba(94, 124, 226, 0.10) 0%, transparent 45%),
            radial-gradient(circle at 85% 15%, rgba(123, 201, 167, 0.10) 0%, transparent 45%),
            linear-gradient(180deg, #f7f8fc 0%, #eef1f8 100%);
        background-attachment: fixed;
    }

    /* Faint dotted texture layered on top, very subtle */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: radial-gradient(rgba(94, 124, 226, 0.06) 1px, transparent 1px);
        background-size: 22px 22px;
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stAppViewContainer"] > .main {
        position: relative;
        z-index: 1;
    }

    /* Sidebar (if used) gets a matching soft tone instead of flat white */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f4f6fb 100%);
        border-right: 1px solid #e7e9f2;
    }

    /* Slightly smoother global typography rendering */
    html, body, [class*="css"] {
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
    }

    /* Give content blocks (tables, cards, forms) a touch more breathing room */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* Slightly rounder, softer default containers/cards across the app */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Extra CSS for the model selectbox
st.markdown(
    """
    <style>
    div.stElementContainer.st-key-_model_sel > div.stSelectbox[data-testid="stSelectbox"] {
        background: linear-gradient(135deg, #e6f0ff 0%, #d1e7ff 100%);
        border: 2px solid #0d6efd;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        color: #0a58ca;
        transition: all 0.3s ease;
        padding: 4px 12px;
    }
    div.stElementContainer.st-key-_model_sel > div.stSelectbox[data-testid="stSelectbox"]:hover {
        border-color: #0b5ed7;
        box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.25);
    }
    div.stElementContainer.st-key-_model_sel > div.stSelectbox[data-testid="stSelectbox"] label {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #0d6efd;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    /* Dropdown arrow color */
    div.stElementContainer.st-key-_model_sel > div.stSelectbox[data-testid="stSelectbox"] svg {
        fill: #0d6efd;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(f"""
<div class="fdm-header">
    <!-- LEFT: FDM Logo -->
    <div class="fdm-logo">
        <span class="fdm-logo-mark">QIMS</span>
        <span class="fdm-logo-sub">Quality Intelligence Monitoring System</span>
    </div>

    <!-- CENTER: Dashboard Title -->
    <div class="fdm-title-block">
        <h1>Quality Intelligence Monitoring System</h1>
    </div>

    <!-- RIGHT: Model & timestamp -->
    <div class="fdm-meta">
        <div class="model-tag">Model:<span>{config.marketing_name}</span></div>
        <div class="update-tag">⟳ Last updated: {config.last_updated}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
from pages2 import summary, analysis, improvement  # imported after config is set

header_container = st.container()
with header_container:
    try:
        from streamlit_option_menu import option_menu

        NAV_PAGES = ["Summary", "Analysis", "Improvement"]
        NAV_ICONS = ["clipboard2-data", "bar-chart-line", "graph-up-arrow"]

        selected = option_menu(
            menu_title=None,
            options=NAV_PAGES,
            icons=NAV_ICONS,
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "6px 2rem",
                    "background-color": "#F5F7FA",
                    "border-radius": "20px",
                    "width": "100%",
                    "display": "flex",
                    "justify-content": "center",
                    "box-shadow": "0 2px 10px rgba(0,0,0,0.05)"
                },
                "icon": {
                    "color": "#5E7CE2",
                    "font-size": "2rem",
                },
                "nav-link": {
                    "font-family": "'Nunito', sans-serif",
                    "font-size": "1.5rem",
                    "font-weight": "600",
                    "color": "#5A6270",
                    "padding": "8px 22px",
                    "border-radius": "8px",
                    "border": "1px solid transparent",
                    "transition": "all 0.25s ease",
                },
                "nav-link:hover": {
                    "color": "#5E7CE2",
                    "background-color": "#052105",
                    "transform": "translateY(-1px)"
                },
                "nav-link-selected": {
                    "background-color": "rgba(123, 201, 167, 0.15)",
                    "color": "#4A9D75",
                    "font-weight": "700",
                    "border": "1px solid rgba(123, 201, 167, 0.25)",
                }
            }
        )
    except ImportError:
        selected = st.radio(
            "Navigation",
            options=["Summary", "Analysis", "Improvement"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
        )

    l, r = st.columns([1, 6])
    with l:
        def _on_model_change():
            new_key = st.session_state._model_sel
            if new_key != st.session_state.active_model:
                st.session_state.active_model = new_key
                st.cache_data.clear()  # force all pages to reload data

        st.selectbox(
            "Model",
            options=_model_keys,
            format_func=lambda k: f" {_model_labels[k]}",
            key="_model_sel",
            index=_model_keys.index(st.session_state.active_model),
            on_change=_on_model_change,
        )

# ── Page Routing ──────────────────────────────────────────────────────────────
if selected == "Summary":
    summary.show()
elif selected == "Analysis":
    analysis.show()
elif selected == "Improvement":
    improvement.show()
