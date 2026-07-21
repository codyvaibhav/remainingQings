"""
Improvement page — per-model, locally-persisted data + a redesigned card UI.

Why it changed
---------------
1. DATA IS NOW DYNAMIC PER MODEL
   Previously every model shared the exact same hard-coded seed rows.
   Now each model starts with an EMPTY improvement list. As soon as
   someone submits the "Add New Improvement" form, that entry is:
     a) appended to the in-memory list for the currently active model, and
     b) written to a small local JSON file on disk, so it survives app
        restarts and is shared by anyone using the same app instance.
   No cloud/external storage is used — everything lives in a folder
   called `improvement_data/` next to this file (one .json per model).
   If you'd rather have Excel files instead of JSON, see the
   `USE_EXCEL_BACKEND` flag near the top — flipping it to True switches
   the read/write functions to .xlsx files with zero changes elsewhere.

2. UI HAS BEEN REDESIGNED
   The old plain HTML <table> has been replaced with a "hero" banner,
   live stat cards, a search + filter bar, and a responsive grid of
   glassy/gradient improvement cards. The add-improvement form now
   lives in its own styled panel with per-item bordered sub-cards and
   a control to add/remove improvement items dynamically.
"""

import streamlit as st
from datetime import datetime, date
import pandas as pd
import json
import os
import io

import config

# ─────────────────────────────────────────────────────────────────────────────
# Storage configuration
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR = "improvement_data"
USE_EXCEL_BACKEND = False  # flip to True to persist as .xlsx instead of .json

SYMPTOM_OPTIONS = ["Display", "Application", "Appearance", "Battery", "Camera"]
PROG_STAT_OPTIONS = [
    "Resolve - Released",
    "Resolve – Process Improved",
    "Resolve – Training & OPL",
    "Resolve – Vendor Process Improved",
]
ITEM_OPTIONS = ["Software", "Hardware", "Process"]

STATUS_COLORS = {
    "Resolve - Released": "#16a34a",
    "Resolve – Process Improved": "#2563eb",
    "Resolve – Training & OPL": "#d97706",
    "Resolve – Vendor Process Improved": "#7c3aed",
}
SYMPTOM_COLORS = {
    "Display": "#0ea5e9",
    "Application": "#8b5cf6",
    "Appearance": "#ec4899",
    "Battery": "#f59e0b",
    "Camera": "#10b981",
}


def _safe_key(model_key: str) -> str:
    """Turn a model key into a filesystem-safe file name."""
    key = "".join(c for c in str(model_key) if c.isalnum() or c in ("-", "_"))
    return key or "default"


def _json_path(model_key: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{_safe_key(model_key)}.json")


def _xlsx_path(model_key: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{_safe_key(model_key)}.xlsx")


def _serialize(rows):
    """Make everything JSON safe (dates -> isoformat strings)."""
    out = []
    for row in rows:
        r = dict(row)
        d = r.get("Imp. Applied Date")
        if isinstance(d, (datetime, date)):
            r["Imp. Applied Date"] = d.isoformat()
        out.append(r)
    return out


def _deserialize(rows):
    out = []
    for row in rows:
        r = dict(row)
        d = r.get("Imp. Applied Date")
        if isinstance(d, str):
            try:
                r["Imp. Applied Date"] = datetime.fromisoformat(d).date()
            except ValueError:
                pass
        out.append(r)
    return out


def load_improvements(model_key: str):
    """Load this model's improvements from disk. Empty list if none yet —
    this is what makes the page start fresh/empty per model."""
    if USE_EXCEL_BACKEND:
        path = _xlsx_path(model_key)
        if not os.path.exists(path):
            return []
        try:
            df = pd.read_excel(path)
            df = df.where(pd.notnull(df), None)
            records = df.to_dict("records")
            for r in records:
                if isinstance(r.get("Improvement"), str) and r["Improvement"]:
                    try:
                        r["Improvement"] = json.loads(r["Improvement"])
                    except json.JSONDecodeError:
                        r["Improvement"] = []
            return _deserialize(records)
        except Exception:
            return []
    else:
        path = _json_path(model_key)
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return _deserialize(json.load(f))
        except (json.JSONDecodeError, OSError):
            return []


def save_improvements(model_key: str, rows):
    """Persist this model's improvement list to disk."""
    if USE_EXCEL_BACKEND:
        path = _xlsx_path(model_key)
        flat = []
        for r in _serialize(rows):
            r = dict(r)
            r["Improvement"] = json.dumps(r.get("Improvement", []))
            flat.append(r)
        pd.DataFrame(flat).to_excel(path, index=False)
    else:
        path = _json_path(model_key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_serialize(rows), f, indent=2, ensure_ascii=False)


def export_to_excel_bytes(rows) -> bytes:
    """Build an in-memory .xlsx for the download button (readable, one row
    per improvement item so nothing nested gets flattened away)."""
    flat_rows = []
    for r in rows:
        base = {
            "Symptom": r.get("Symptom", ""),
            "Sub-Symptom": r.get("Sub-Symptom", ""),
            "Case Code": r.get("Case Code", ""),
            "Progr.Stat.": r.get("Progr.Stat.", ""),
            "Imp. Applied Date": r.get("Imp. Applied Date", ""),
        }
        items = r.get("Improvement", []) or [{}]
        for it in items:
            row = dict(base)
            row["Item"] = it.get("Item", "")
            row["S/W version"] = it.get("S/W version", "")
            row["H/W version"] = it.get("H/W version", "")
            row["Details"] = it.get("Details", "")
            flat_rows.append(row)
    buf = io.BytesIO()
    pd.DataFrame(flat_rows).to_excel(buf, index=False)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# UI helpers
# ─────────────────────────────────────────────────────────────────────────────

def _inject_css():
    st.markdown(
        """
        <style>
        .imp-hero {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 45%, #ec4899 100%);
            border-radius: 22px;
            padding: 28px 32px;
            margin-bottom: 22px;
            color: white;
            box-shadow: 0 10px 30px rgba(124, 58, 237, 0.25);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
        }
        .imp-hero h1 {
            margin: 0;
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: 0.01em;
        }
        .imp-hero p {
            margin: 4px 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }
        .imp-hero .model-chip {
            background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.35);
            padding: 8px 18px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.95rem;
            backdrop-filter: blur(6px);
        }

        .stat-row { display: flex; gap: 16px; margin-bottom: 22px; flex-wrap: wrap; }
        .stat-card {
            flex: 1 1 160px;
            background: white;
            border-radius: 16px;
            padding: 16px 18px;
            border: 1px solid #eef0f4;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        }
        .stat-card .num { font-size: 1.7rem; font-weight: 800; color: #1e1b4b; }
        .stat-card .lbl { font-size: 0.8rem; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }

        .imp-toolbar {
            background: #f8f9ff;
            border: 1px solid #eceafd;
            border-radius: 16px;
            padding: 14px 18px;
            margin-bottom: 20px;
        }

        .imp-card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 18px; margin-bottom: 26px; }
        .imp-card {
            background: white;
            border-radius: 18px;
            padding: 18px 20px;
            border: 1px solid #eef0f4;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.07);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            border-left: 6px solid var(--accent, #7c3aed);
        }
        .imp-card:hover { transform: translateY(-3px); box-shadow: 0 12px 26px rgba(15, 23, 42, 0.12); }
        .imp-card .imp-card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
        .imp-card .symptom-tag {
            display: inline-block; padding: 4px 12px; border-radius: 999px;
            font-size: 0.72rem; font-weight: 800; color: white; letter-spacing: 0.03em;
            background: var(--accent, #7c3aed);
        }
        .imp-card .sub-symptom { font-size: 1.05rem; font-weight: 750; color: #111827; margin: 8px 0 4px 0; }
        .imp-card .meta-line { font-size: 0.82rem; color: #6b7280; margin-bottom: 4px; }
        .imp-card .status-pill {
            display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.72rem;
            font-weight: 700; color: white; margin-top: 6px;
        }
        .imp-card .items-wrap { margin-top: 12px; border-top: 1px dashed #e5e7eb; padding-top: 10px; }
        .imp-item-chip {
            background: #f4f5ff; border: 1px solid #e6e6fb; border-radius: 12px;
            padding: 8px 10px; margin-bottom: 8px; font-size: 0.82rem; color: #374151;
        }
        .imp-item-chip b { color: #1f2937; }
        .imp-item-chip .pill {
            display: inline-block; background: #ede9fe; color: #5b21b6; font-weight: 700;
            border-radius: 8px; padding: 1px 8px; font-size: 0.7rem; margin-right: 6px;
        }

        .empty-state {
            text-align: center; padding: 46px 20px; border-radius: 18px;
            background: repeating-linear-gradient(135deg, #f8f9ff, #f8f9ff 10px, #f2f1ff 10px, #f2f1ff 20px);
            border: 1px dashed #cdd0f7; color: #4b5563; margin-bottom: 22px;
        }
        .empty-state h3 { color: #4338ca; margin-bottom: 6px; }

        .add-panel {
            background: linear-gradient(180deg, #ffffff 0%, #fbfaff 100%);
            border: 1px solid #ece9ff; border-radius: 20px; padding: 22px 24px; margin-top: 6px;
            box-shadow: 0 8px 24px rgba(76, 29, 149, 0.07);
        }
        .add-panel h2 { margin-top: 0; color: #3730a3; }

        div.stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #7c3aed, #4338ca) !important;
            border: none !important; border-radius: 12px !important;
            padding: 10px 22px !important; font-weight: 700 !important;
            box-shadow: 0 6px 16px rgba(76, 29, 149, 0.28) !important;
            transition: transform 0.15s ease !important;
        }
        div.stButton>button[kind="primary"]:hover { transform: translateY(-2px); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _stat_card(label, value):
    return f"""<div class="stat-card"><div class="num">{value}</div><div class="lbl">{label}</div></div>"""


def _render_card(entry, sno):
    accent = SYMPTOM_COLORS.get(entry.get("Symptom", ""), "#7c3aed")
    status = entry.get("Progr.Stat.", "")
    status_color = STATUS_COLORS.get(status, "#6b7280")
    imp_date = entry.get("Imp. Applied Date", "")
    if isinstance(imp_date, (date, datetime)):
        imp_date = imp_date.strftime("%d %b %Y")

    items_html = ""
    for it in entry.get("Improvement", []):
        items_html += (
            f"<div class='imp-item-chip'>"
            f"<span class='pill'>{it.get('Item','')}</span>"
            f"<b>Details:</b> {it.get('Details','')}"
            f"<br><span style='color:#6b7280;'>S/W: {it.get('S/W version','-')} &nbsp;|&nbsp; "
            f"H/W: {it.get('H/W version','-')}</span>"
            f"</div>"
        )

    html = f"""
    <div class="imp-card" style="--accent:{accent};">
        <div class="imp-card-top">
            <span class="symptom-tag">{entry.get('Symptom','')}</span>
            <span style="color:#9ca3af; font-size:0.75rem; font-weight:700;">#{sno}</span>
        </div>
        <div class="sub-symptom">{entry.get('Sub-Symptom','')}</div>
        <div class="meta-line">🗂️ Case Code: {entry.get('Case Code','')}</div>
        <div class="meta-line">📅 Applied: {imp_date}</div>
        <span class="status-pill" style="background:{status_color};">{status}</span>
        <div class="items-wrap">{items_html}</div>
    </div>
    """
    return html


def _empty_form_item():
    return {"Item": "", "S/W version": "", "H/W version": "", "Details": ""}


# ─────────────────────────────────────────────────────────────────────────────
# Main page
# ─────────────────────────────────────────────────────────────────────────────

def show():
    try:
        st.set_page_config(page_title=f"{getattr(config, 'main', 'QIMS')} Improvement", page_icon=":memo:")
    except Exception:
        pass  # page config already set elsewhere in this run

    _inject_css()

    model_key = st.session_state.get("active_model", "default")
    model_label = model_key
    if hasattr(config, "MODELS") and model_key in getattr(config, "MODELS", {}):
        model_label = config.MODELS[model_key].get("label", model_key)

    # ── Load this model's data (dynamic + empty-by-default) ─────────────────
    if "improvements_store" not in st.session_state:
        st.session_state.improvements_store = {}
    if model_key not in st.session_state.improvements_store:
        st.session_state.improvements_store[model_key] = load_improvements(model_key)

    data = st.session_state.improvements_store[model_key]

    # ── Hero banner ──────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="imp-hero">
            <div>
                <h1>🛠️ Improvements</h1>
                <p>Every fix, upgrade, and process change tracked in one place.</p>
            </div>
            <div class="model-chip">Model: {model_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stats ────────────────────────────────────────────────────────────────
    total = len(data)
    resolved = sum(1 for d in data if str(d.get("Progr.Stat.", "")).startswith("Resolve - Released"))
    sw_count = sum(1 for d in data for it in d.get("Improvement", []) if it.get("Item") == "Software")
    hw_count = sum(1 for d in data for it in d.get("Improvement", []) if it.get("Item") == "Hardware")

    st.markdown(
        f"""
        <div class="stat-row">
            {_stat_card("Total Entries", total)}
            {_stat_card("Fully Released", resolved)}
            {_stat_card("Software Fixes", sw_count)}
            {_stat_card("Hardware Fixes", hw_count)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Toolbar: filter + search ─────────────────────────────────────────────
    st.markdown('<div class="imp-toolbar">', unsafe_allow_html=True)
    tcol1, tcol2 = st.columns([1, 2])
    with tcol1:
        unique_symptoms = sorted({d["Symptom"] for d in data if d.get("Symptom")})
        selected_symptom = st.selectbox("Filter by Symptom", options=["All"] + unique_symptoms, index=0)
    with tcol2:
        search_text = st.text_input(
            "Search", placeholder="Search case code, sub-symptom or details...", label_visibility="visible"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = data
    if selected_symptom != "All":
        filtered = [d for d in filtered if d.get("Symptom") == selected_symptom]
    if search_text:
        q = search_text.lower()
        def _match(d):
            haystack = " ".join(
                [str(d.get("Case Code", "")), str(d.get("Sub-Symptom", ""))]
                + [str(it.get("Details", "")) for it in d.get("Improvement", [])]
            ).lower()
            return q in haystack
        filtered = [d for d in filtered if _match(d)]

    # sort newest first
    def _sort_key(d):
        v = d.get("Imp. Applied Date")
        if isinstance(v, (date, datetime)):
            return v
        return date.min
    filtered = sorted(filtered, key=_sort_key, reverse=True)

    # ── Cards or empty state ─────────────────────────────────────────────────
    if not filtered:
        if not data:
            st.markdown(
                """
                <div class="empty-state">
                    <h3>No improvements logged yet for this model</h3>
                    <p>Click <b>“Add New Improvement”</b> below to record the first one.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No improvements match your current filter/search.")
    else:
        cards_html = '<div class="imp-card-grid">'
        for i, entry in enumerate(filtered, start=1):
            cards_html += _render_card(entry, i)
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

    # ── Export ───────────────────────────────────────────────────────────────
    if data:
        st.download_button(
            "⬇️ Export this model's data to Excel",
            data=export_to_excel_bytes(data),
            file_name=f"improvements_{_safe_key(model_key)}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.divider()

    # ── Add New Improvement ──────────────────────────────────────────────────
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    if "form_improvements" not in st.session_state:
        st.session_state.form_improvements = [_empty_form_item()]

    if st.button("➕ Add New Improvement", type="primary"):
        st.session_state.show_form = not st.session_state.show_form

    if st.session_state.show_form:
        st.markdown('<div class="add-panel">', unsafe_allow_html=True)
        st.markdown("<h2>New Improvement</h2>", unsafe_allow_html=True)

        # Let the user choose how many improvement items to attach,
        # BEFORE opening the form (widgets that resize a list must live
        # outside st.form, since forms only submit once as a whole).
        item_count = st.number_input(
            "How many improvement items does this entry have?",
            min_value=1, max_value=10,
            value=len(st.session_state.form_improvements),
            step=1,
            key="item_count_selector",
        )
        if item_count != len(st.session_state.form_improvements):
            current = st.session_state.form_improvements
            if item_count > len(current):
                current.extend(_empty_form_item() for _ in range(item_count - len(current)))
            else:
                current = current[:item_count]
            st.session_state.form_improvements = current
            st.rerun()

        with st.form(key="improvement_form"):
            col1, col2 = st.columns(2)
            with col1:
                symptom = st.selectbox("Symptom*", options=SYMPTOM_OPTIONS)
                sub_symptom = st.text_input("Sub-Symptom*", placeholder="e.g., Flickering 8K, Dust on Camera")
            with col2:
                case_code = st.text_input("Case Code*", placeholder="e.g., P260302-06393 or Market Voc")
                prog_stat = st.selectbox("Progress Status*", options=PROG_STAT_OPTIONS)
            imp_date = st.date_input("Imp. Applied Date*", value=datetime.today())

            st.markdown(
                "<div style='font-weight:800; font-size:1.05rem; color:#3730a3; margin:14px 0 6px 0;'>Improvement Items</div>",
                unsafe_allow_html=True,
            )

            for i, improvement in enumerate(st.session_state.form_improvements):
                with st.container(border=True):
                    cols = st.columns([2, 2, 2])
                    with cols[0]:
                        item = st.selectbox(
                            "Item*", ["", *ITEM_OPTIONS],
                            index=(ITEM_OPTIONS.index(improvement["Item"]) + 1)
                            if improvement["Item"] in ITEM_OPTIONS else 0,
                            key=f"item_{i}_{model_key}",
                        )
                    with cols[1]:
                        sw_version = st.text_input(
                            "S/W version", improvement["S/W version"],
                            placeholder="Version", key=f"sw_{i}_{model_key}",
                        )
                    with cols[2]:
                        hw_version = st.text_input(
                            "H/W version", improvement["H/W version"],
                            placeholder="Parts", key=f"hw_{i}_{model_key}",
                        )
                    details = st.text_area(
                        "Details*", improvement["Details"],
                        placeholder="Description", key=f"details_{i}_{model_key}",
                    )
                    st.session_state.form_improvements[i] = {
                        "Item": item,
                        "S/W version": sw_version,
                        "H/W version": hw_version,
                        "Details": details,
                    }

            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submit = st.form_submit_button("✅ Submit")
            with col_cancel:
                cancel = st.form_submit_button("✖ Cancel")

            if cancel:
                st.session_state.show_form = False
                st.session_state.form_improvements = [_empty_form_item()]
                st.rerun()

            if submit:
                required_fields = [case_code, prog_stat, symptom, sub_symptom, imp_date]
                valid_improvements = all(
                    imp["Item"] and imp["Details"] for imp in st.session_state.form_improvements
                )
                if not all(required_fields):
                    st.warning("Please fill all required fields (*)!")
                elif not valid_improvements:
                    st.warning("Each improvement item requires at least 'Item' and 'Details'!")
                else:
                    new_entry = {
                        "Imp. Applied Date": imp_date,
                        "Case Code": case_code,
                        "Progr.Stat.": prog_stat,
                        "Symptom": symptom,
                        "Sub-Symptom": sub_symptom,
                        "Improvement": st.session_state.form_improvements.copy(),
                    }
                    # append + persist to this model's own local file
                    st.session_state.improvements_store[model_key].append(new_entry)
                    save_improvements(model_key, st.session_state.improvements_store[model_key])

                    st.success("Submitted Successfully!")
                    st.balloons()

                    st.session_state.show_form = False
                    st.session_state.form_improvements = [_empty_form_item()]
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
