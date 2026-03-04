"""
Multi-Persona Content PDCA Agent — Streamlit UI
"""
import asyncio
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from main import run_pdca  # noqa: E402

st.set_page_config(
    page_title="Multi-Persona Content PDCA Agent",
    page_icon="🤖",
    layout="wide",
)

PERSONA_LABELS = {
    "PersonaAgent_General": "🧑 General",
    "PersonaAgent_SideBiz": "💼 Side Biz",
    "PersonaAgent_Tech": "⚙️ Tech",
}

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    platform = st.selectbox(
        "Platform",
        ["x", "note", "kdp"],
        format_func=lambda x: {"x": "𝕏 (Twitter)", "note": "note.com", "kdp": "KDP / Amazon"}[x],
    )
    st.markdown("---")
    st.markdown("**Evaluation Personas**")
    st.markdown(
        "- 🧑 **General** — casual reader\n"
        "- 💼 **Side Biz** — aspiring entrepreneur\n"
        "- ⚙️ **Tech** — technical audience"
    )
    st.markdown("---")
    language = st.radio("Output Language", ["English", "日本語"], horizontal=True)
    language_code = "en" if language == "English" else "ja"
    st.caption("Pass threshold: 70 / 100")

# ── Main ─────────────────────────────────────────────────
st.title("🤖 Multi-Persona Content PDCA Agent")
st.caption(
    "Generate social media content and auto-refine it through a multi-persona AI evaluation loop "
    "until all personas approve."
)

theme = st.text_input(
    "Content Theme",
    placeholder="e.g. How to start a side hustle using AI",
)
run_btn = st.button("▶ Generate", type="primary", disabled=not theme.strip())

if run_btn and theme.strip():
    with st.spinner("⏳ Running PDCA pipeline..."):
        result = asyncio.run(run_pdca(theme.strip(), platform=platform, language=language_code))

    # ── Status banner ────────────────────────────────────
    if result["all_passed"]:
        st.success(f"✅ All personas passed — {result['iterations']} evaluation loop(s)")
    else:
        st.warning(f"⚠️ Max iterations reached — {result['iterations']} loop(s)")

    # ── Persona scores ───────────────────────────────────
    st.subheader("Persona Scores")
    cols = st.columns(3)
    for i, (persona, score) in enumerate(result["scores"].items()):
        with cols[i]:
            passed = score >= 70
            st.metric(
                PERSONA_LABELS.get(persona, persona),
                f"{score} / 100",
                delta="PASS ✓" if passed else "FAIL ✗",
                delta_color="normal" if passed else "inverse",
            )

    # ── PDCA history (only shown when multiple loops ran) ─
    if result["iterations"] > 1:
        with st.expander(f"📊 PDCA Journey ({result['iterations']} loops)", expanded=False):
            for loop in result["history"]:
                st.markdown(f"**Loop {loop['iteration'] + 1}**")
                for r in loop["results"]:
                    icon = "🟢" if r["score"] >= 70 else "🔴"
                    label = PERSONA_LABELS.get(r["persona"], r["persona"])
                    st.markdown(f"{icon} **{label}**: {r['score']}/100 — {r['feedback']}")
                st.markdown("---")

    # ── Final content ────────────────────────────────────
    st.subheader("📋 Final Content")
    st.markdown(result["final_content"])
    st.code(result["final_content"], language=None)
