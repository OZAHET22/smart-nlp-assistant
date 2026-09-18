"""
Smart Reading & Writing Assistant — Enterprise NLP Studio.
A modern, intuitive, and responsive UI/UX built purely in Python with Streamlit.

Stages Covered:
- Stage 1: Levenshtein Edit-Distance & Brown Corpus N-Gram Spell Checking
- Stage 2: spaCy Dependency Parsing & Custom CYK Grammar Syntactic Parsing
- Stage 3: Named Entity Recognition (NER), Semantic Role Labeling (SRL), & Lesk WSD
- Stage 4: Coreference Resolution, Discourse Relations, & Pragmatic Speech Act Inference
"""

from __future__ import annotations

import os
import sys
import json
import time
import html
from dataclasses import asdict
from typing import Any

# Ensure project root is in sys.path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

import streamlit as st
import pandas as pd

from stage1_spellcheck.spellchecker import SpellChecker, SpellCheckResult, SpellCorrection
from pipeline import process, PipelineResult
from stage2_syntax.cyk_parser import build_parse_tree_string


# -----------------------------------------------------------------------------
# 0. Automatic Resource Downloader (for Streamlit Cloud)
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _ensure_resources():
    import download_resources
    download_resources.download_nltk_resources()
    download_resources.download_spacy_model()

_ensure_resources()


# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom Design System (CSS)
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Smart NLP Assistant | Pro Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* --- Typography & Global Theme --- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    letter-spacing: -0.01em;
}

code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* --- Hero Banner --- */
.hero-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(16px);
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: -50px;
    right: -50px;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0) 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #a5b4fc;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 4px 12px;
    border-radius: 9999px;
    margin-bottom: 12px;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 6px 0;
    line-height: 1.2;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1rem;
    color: #94a3b8;
    margin: 0;
    max-width: 800px;
    line-height: 1.5;
}

/* --- Metric Cards --- */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.metric-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.35);
}

.metric-icon {
    font-size: 1.25rem;
    margin-bottom: 6px;
    opacity: 0.9;
}

.metric-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1.1;
}

.metric-label {
    font-size: 0.8rem;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-top: 4px;
}

/* --- Section Container Cards --- */
.content-card {
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 20px;
    backdrop-filter: blur(12px);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.card-header h3 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 700;
    color: #f1f5f9;
}

.card-tag {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 6px;
    text-transform: uppercase;
}

.tag-blue { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
.tag-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
.tag-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.tag-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

/* --- Visual Diff Highlighter --- */
.diff-container {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 18px;
    font-size: 1.05rem;
    line-height: 1.8;
    color: #e2e8f0;
    min-height: 120px;
}

.diff-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    padding: 2px 6px;
    margin: 0 2px;
}

.diff-del {
    color: #fb7185;
    text-decoration: line-through;
    font-size: 0.95em;
}

.diff-arrow {
    color: #64748b;
    font-size: 0.8em;
}

.diff-add {
    color: #34d399;
    font-weight: 700;
}

/* --- Grammatical Tokens / POS Chips --- */
.tokens-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 12px 0;
}

.pos-chip {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid transparent;
    transition: all 0.2s ease;
}

.pos-chip:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

.pos-word {
    font-weight: 700;
    font-size: 0.95rem;
}

.pos-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    opacity: 0.85;
    margin-top: 2px;
}

.pos-noun { background: rgba(56, 189, 248, 0.15); border-color: rgba(56, 189, 248, 0.3); color: #7dd3fc; }
.pos-verb { background: rgba(168, 85, 247, 0.15); border-color: rgba(168, 85, 247, 0.3); color: #d8b4fe; }
.pos-adj  { background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.3); color: #fde047; }
.pos-adv  { background: rgba(52, 211, 153, 0.15); border-color: rgba(52, 211, 153, 0.3); color: #6ee7b7; }
.pos-pron { background: rgba(244, 114, 182, 0.15); border-color: rgba(244, 114, 182, 0.3); color: #f472b6; }
.pos-other { background: rgba(148, 163, 184, 0.12); border-color: rgba(148, 163, 184, 0.2); color: #cbd5e1; }

/* --- Semantic Role Cards (Agent ➔ Action ➔ Patient) --- */
.srl-frame-card {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
}

.srl-sentence {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 12px;
}

.srl-flow {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}

.srl-node {
    display: flex;
    flex-direction: column;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 0.9rem;
}

.srl-node-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-bottom: 2px;
}

.srl-agent { background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); color: #7dd3fc; }
.srl-action { background: rgba(168, 85, 247, 0.18); border: 1px solid rgba(168, 85, 247, 0.35); color: #d8b4fe; }
.srl-patient { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #6ee7b7; }
.srl-arrow { color: #64748b; font-size: 1.1rem; }

/* --- Coreference Mention Chains --- */
.coref-chain-card {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.chain-badge {
    background: rgba(99, 102, 241, 0.2);
    border: 1px solid rgba(99, 102, 241, 0.4);
    color: #a5b4fc;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 6px;
}

.chain-item {
    font-weight: 700;
    color: #f1f5f9;
    padding: 4px 10px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.05);
}

/* --- Pragmatics & Indirect Requests Alert --- */
.pragmatic-alert {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.15) 100%);
    border: 1px solid rgba(245, 158, 11, 0.35);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
    position: relative;
}

.pragmatic-badge {
    display: inline-block;
    background: #f59e0b;
    color: #0f172a;
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 8px;
}

.pragmatic-surface {
    font-size: 1.05rem;
    font-weight: 700;
    color: #fef08a;
    margin-bottom: 4px;
}

.pragmatic-implied {
    font-size: 0.9rem;
    color: #fde047;
    opacity: 0.9;
}

/* --- Word Sense Disambiguation Card --- */
.wsd-card {
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}

.wsd-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.wsd-word {
    font-size: 1.1rem;
    font-weight: 800;
    color: #38bdf8;
}

.wsd-sense {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #c084fc;
    background: rgba(168, 85, 247, 0.15);
    padding: 2px 8px;
    border-radius: 4px;
}

.wsd-def {
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.4;
}

/* --- Custom Scrollbars & Utilities --- */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.5);
}
::-webkit-scrollbar-thumb {
    background: rgba(100, 116, 139, 0.5);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(148, 163, 184, 0.7);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Benchmark Sample Catalog & Caching
# -----------------------------------------------------------------------------

SAMPLE_METADATA = {
    "sample_01.txt": {
        "title": "Sample 01: Student Email",
        "description": "Spelling errors ('assigment', 'freind') + Polite indirect request",
    },
    "sample_02.txt": {
        "title": "Sample 02: River Bank Flooding",
        "description": "River sense disambiguation ('bank') + pronoun coreference",
    },
    "sample_03.txt": {
        "title": "Sample 03: Hallway Light & Landlord",
        "description": "Word sense ('light') + discourse causality",
    },
    "sample_04.txt": {
        "title": "Sample 04: Lecture Notes Request",
        "description": "Slang typos ('plz', 'couldnt') + Polite request speech act",
    },
    "sample_05.txt": {
        "title": "Sample 05: Flying Bat in Gym",
        "description": "Animal sense disambiguation ('bat') + pronoun coreference",
    },
    "sample_06.txt": {
        "title": "Sample 06: Grocery Shopping",
        "description": "Named entity ('John') + coreference chain + typo ('grocerys')",
    },
    "sample_07.txt": {
        "title": "Sample 07: Project Meeting Review",
        "description": "Orthographic errors ('completly') + discourse contrast",
    },
    "sample_08.txt": {
        "title": "Sample 08: Broken Laptop & Library",
        "description": "Typos ('libary') + discourse relation ('so')",
    },
    "sample_09.txt": {
        "title": "Sample 09: Climate Change Lecture",
        "description": "Named entity ('Dr. Smith') + female pronoun coreference",
    },
    "sample_10.txt": {
        "title": "Sample 10: Grading Inquiry",
        "description": "Informal speech ('yo', 'explane') + indirect request",
    },
}


def get_samples_dir() -> str:
    default_path = os.path.join(_CURRENT_DIR, "test_samples")
    if os.path.isdir(default_path):
        return default_path
    fallback = os.path.join(_CURRENT_DIR, "data", "test_samples")
    if os.path.isdir(fallback):
        return fallback
    return default_path


@st.cache_data
def load_all_samples() -> dict[str, str]:
    samples = {}
    sdir = get_samples_dir()
    if os.path.isdir(sdir):
        for fname in sorted(os.listdir(sdir)):
            if fname.endswith(".txt"):
                p = os.path.join(sdir, fname)
                with open(p, "r", encoding="utf-8") as fh:
                    samples[fname] = fh.read().strip()
    return samples


@st.cache_resource
def load_spell_checker() -> SpellChecker:
    return SpellChecker()


checker = load_spell_checker()
all_samples = load_all_samples()


# -----------------------------------------------------------------------------
# 3. Session State Initialization
# -----------------------------------------------------------------------------

if "editor_text" not in st.session_state:
    st.session_state["editor_text"] = all_samples.get(
        "sample_01.txt",
        "hey prof i wanted to ask about the assigment thats due on friday. me and my freind were working on it togehter but we cant figure out the last part. could you send us the rubric again?",
    )

if "pipeline_text" not in st.session_state:
    st.session_state["pipeline_text"] = st.session_state["editor_text"]

if "last_pipeline_result" not in st.session_state:
    st.session_state["last_pipeline_result"] = None


# -----------------------------------------------------------------------------
# 4. Sidebar Controls & Preset Loader
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🎛️ Control Panel")
    st.caption("Load curated test cases or configure pipeline behavior.")

    sample_options = ["Custom Input"] + [
        f"{SAMPLE_METADATA.get(k, {}).get('title', k)}" for k in all_samples.keys()
    ]
    sample_keys = ["custom"] + list(all_samples.keys())

    selected_idx = st.selectbox(
        "📚 Benchmark Test Samples",
        options=range(len(sample_options)),
        format_func=lambda i: sample_options[i],
        help="Instantly load one of the 10 benchmark evaluation samples.",
    )

    selected_key = sample_keys[selected_idx]
    if selected_key != "custom":
        meta = SAMPLE_METADATA.get(selected_key, {})
        st.info(f"💡 **Context:** {meta.get('description', '')}")
        if st.button("📥 Load Sample into Assistant", use_container_width=True):
            st.session_state["editor_text"] = all_samples[selected_key]
            st.session_state["pipeline_text"] = all_samples[selected_key]
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧩 Pipeline Modules")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("**Stage 1**  \n`Levenshtein + Brown`")
        st.markdown("**Stage 2**  \n`CYK + spaCy Dep`")
    with col_s2:
        st.markdown("**Stage 3**  \n`NER + SRL + Lesk`")
        st.markdown("**Stage 4**  \n`Coref + Discourse`")

    st.markdown("---")
    st.markdown("### ⚙️ System Status")
    st.markdown(
        """
        <div style="font-size:0.82rem; color:#94a3b8; line-height:1.6;">
            <div>● <b>N-Gram Vocabulary:</b> 40,234 words</div>
            <div>● <b>Bigram Types:</b> 388,815</div>
            <div>● <b>spaCy Core Model:</b> en_core_web_sm</div>
            <div>● <b>WordNet Synsets:</b> Active</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 5. Executive Hero Banner
# -----------------------------------------------------------------------------

st.markdown(
    """
    <div class="hero-container">
        <div class="hero-pill">
            <span style="display:inline-block; width:8px; height:8px; background:#34d399; border-radius:50%;"></span>
            Enterprise NLP Studio • v2.0
        </div>
        <h1 class="hero-title">Smart Reading & Writing Assistant</h1>
        <p class="hero-subtitle">
            A state-of-the-art multi-stage natural language pipeline that transforms raw, messy text through 
            lexical orthography, syntactic grammar trees, semantic frame parsing, and discourse pragmatics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 6. Main Application Tabs
# -----------------------------------------------------------------------------

tab_editor, tab_pipeline, tab_benchmarks = st.tabs(
    [
        "✍️  Smart Editor & Spell-Check",
        "🔬  Deep Pipeline Studio",
        "📊  Benchmark & Batch Analytics",
    ]
)


# =============================================================================
# TAB 1: SMART EDITOR & SPELL-CHECKER
# =============================================================================

with tab_editor:
    editor_input = st.text_area(
        "Input Draft",
        value=st.session_state["editor_text"],
        height=180,
        placeholder="Type or paste your text here (e.g. i will recieve teh file tommorow)...",
        key="editor_textarea",
        help="Edits are evaluated in real time via Levenshtein edit distance and Brown corpus bigram probability.",
    )
    st.session_state["editor_text"] = editor_input

    # Action Toolbar
    col_tb1, col_tb2, col_tb3 = st.columns([2, 2, 4])
    with col_tb1:
        if st.button("🧹 Clear Input", use_container_width=True):
            st.session_state["editor_text"] = ""
            st.rerun()
    with col_tb2:
        if st.button("🚀 Analyze in Deep Studio", use_container_width=True):
            st.session_state["pipeline_text"] = editor_input
            st.info("Navigating to Deep Studio... please click on the '🔬 Deep Pipeline Studio' tab above.")

    if editor_input.strip():
        start_time = time.perf_counter()
        check_result: SpellCheckResult = checker.correct(editor_input)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        words_count = len(editor_input.split())
        chars_count = len(editor_input)
        typos_count = len(check_result.corrections)

        # Metrics Ribbon
        st.markdown(
            f"""
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-icon">📝</div>
                    <div class="metric-value">{words_count}</div>
                    <div class="metric-label">Total Words</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🔤</div>
                    <div class="metric-value">{chars_count}</div>
                    <div class="metric-label">Characters</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🎯</div>
                    <div class="metric-value" style="color:{'#f43f5e' if typos_count > 0 else '#34d399'}">{typos_count}</div>
                    <div class="metric-label">Typos Corrected</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">⚡</div>
                    <div class="metric-value">{elapsed_ms:.1f}<span style="font-size:1rem; font-weight:500;"> ms</span></div>
                    <div class="metric-label">Processing Time</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Side-by-Side Comparative View
        col_out_left, col_out_right = st.columns(2)

        with col_out_left:
            st.markdown(
                """
                <div class="content-card">
                    <div class="card-header">
                        <h3>✨ Visual Diff Analysis</h3>
                        <span class="card-tag tag-purple">Real-Time</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            # Generate inline HTML diff
            # Build word correction mapping
            corr_map = {c.original.lower(): c.corrected for c in check_result.corrections}
            tokens = editor_input.split()
            diff_fragments = []
            for t in tokens:
                clean_w = t.strip(".,!?:;\"'()[]{}").lower()
                if clean_w in corr_map:
                    corr_w = corr_map[clean_w]
                    # Preserve titlecase if original was capitalized
                    if t and t[0].isupper():
                        corr_w = corr_w.capitalize()
                    diff_fragments.append(
                        f'<span class="diff-chip"><del class="diff-del">{html.escape(t)}</del><span class="diff-arrow">➔</span><ins class="diff-add">{html.escape(corr_w)}</ins></span>'
                    )
                else:
                    diff_fragments.append(html.escape(t))

            diff_html = " ".join(diff_fragments)
            st.markdown(
                f'<div class="diff-container">{diff_html}</div></div>',
                unsafe_allow_html=True,
            )

        with col_out_right:
            st.markdown(
                """
                <div class="content-card">
                    <div class="card-header">
                        <h3>📋 Polished Text</h3>
                        <span class="card-tag tag-emerald">Cleaned</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            st.text_area(
                "Cleaned Output",
                value=check_result.corrected_text,
                height=150,
                disabled=True,
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Detailed Corrections Table
        if check_result.corrections:
            st.markdown("### 🔍 Corrections Breakdown")
            table_records = []
            for c in check_result.corrections:
                table_records.append(
                    {
                        "Original": c.original,
                        "Replacement": c.corrected,
                        "Strategy": c.reason,
                        "Confidence Score": f"{c.score:.4f}",
                    }
                )
            df_corrections = pd.DataFrame(table_records)
            st.dataframe(df_corrections, use_container_width=True, hide_index=True)
        else:
            st.success("🎉 Excellent! No spelling errors or vocabulary anomalies detected.")
    else:
        st.info("💡 Type in the editor above or select a benchmark sample from the sidebar.")


# =============================================================================
# TAB 2: DEEP NLP PIPELINE STUDIO
# =============================================================================

with tab_pipeline:
    st.markdown("### 🔬 Multi-Stage NLP Studio")
    st.caption("Executes Stages 1–4 continuously to yield syntax trees, semantic frames, and pragmatic inferences.")

    pipeline_input = st.text_area(
        "Source Document for Pipeline Execution",
        value=st.session_state["pipeline_text"],
        height=140,
        placeholder="Paste a paragraph to parse syntax, semantic roles, coreference, and pragmatics...",
        key="pipeline_textarea",
    )
    st.session_state["pipeline_text"] = pipeline_input

    btn_run = st.button("⚡ Execute End-to-End Pipeline", type="primary", use_container_width=True)

    if btn_run and pipeline_input.strip():
        with st.spinner("Processing through 4-stage pipeline..."):
            t0 = time.perf_counter()
            pr: PipelineResult = process(pipeline_input)
            t_total = time.perf_counter() - t0
            st.session_state["last_pipeline_result"] = (pr, t_total)

    if st.session_state["last_pipeline_result"] is not None:
        pr, t_total = st.session_state["last_pipeline_result"]

        # Aggregate Statistics Ribbon
        total_sents = len(pr.sentence_parses)
        total_ents = sum(len(f.entities) for f in pr.semantic_frames)
        total_roles = sum(1 for f in pr.semantic_frames if f.agent or f.action or f.patient)
        total_coref = len(pr.coref_chains)
        total_discourse = len(pr.discourse_relations)
        total_pragmatic = len(pr.pragmatic_notes)

        st.markdown(
            f"""
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-icon">📑</div>
                    <div class="metric-value">{total_sents}</div>
                    <div class="metric-label">Sentences</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🏷️</div>
                    <div class="metric-value">{total_ents}</div>
                    <div class="metric-label">Named Entities</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🎯</div>
                    <div class="metric-value">{total_roles}</div>
                    <div class="metric-label">Semantic Frames</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🔗</div>
                    <div class="metric-value">{total_coref}</div>
                    <div class="metric-label">Coref Chains</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">💬</div>
                    <div class="metric-value">{total_pragmatic}</div>
                    <div class="metric-label">Indirect Requests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">⚡</div>
                    <div class="metric-value">{t_total:.2f}<span style="font-size:1rem; font-weight:500;"> s</span></div>
                    <div class="metric-label">Pipeline Runtime</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Stage Sub-Tabs for clean UX
        sub1, sub2, sub3, sub4, sub_export = st.tabs(
            [
                "Stage 1: Orthography & Spelling",
                "Stage 2: Syntax & Parsing",
                "Stage 3: Semantics & Roles",
                "Stage 4: Discourse & Pragmatics",
                "📥 Export Data",
            ]
        )

        # ---------------------------------------------------------------------
        # Stage 1 Sub-Tab
        # ---------------------------------------------------------------------
        with sub1:
            st.markdown(
                """
                <div class="content-card">
                    <div class="card-header">
                        <h3>Stage 1 — Lexical Normalization</h3>
                        <span class="card-tag tag-emerald">Stage 1</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            if pr.corrections:
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown("**Original Cleaned Text**")
                    st.text_area("Corrected Text", value=pr.corrected_text, height=140, disabled=True)
                with c2:
                    st.markdown("**Replacements Made**")
                    corr_df = pd.DataFrame(
                        [
                            {
                                "Original": c.original,
                                "Corrected": c.corrected,
                                "Reason": c.reason,
                                "Score": f"{c.score:.4f}",
                            }
                            for c in pr.corrections
                        ]
                    )
                    st.dataframe(corr_df, use_container_width=True, hide_index=True)
            else:
                st.success("No spelling corrections required. Downstream stages processed original text.")
            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # Stage 2 Sub-Tab
        # ---------------------------------------------------------------------
        with sub2:
            st.markdown("#### Grammatical & Syntactic Analysis")
            st.caption("spaCy dependency parsing with grammatical category badges & CYK Chomsky-normal-form trees.")

            pos_legend = """
            <div style="display:flex; gap:10px; margin-bottom:14px; font-size:0.78rem; flex-wrap:wrap;">
                <span class="pos-chip pos-noun" style="padding:2px 8px;">Noun</span>
                <span class="pos-chip pos-verb" style="padding:2px 8px;">Verb</span>
                <span class="pos-chip pos-adj" style="padding:2px 8px;">Adjective</span>
                <span class="pos-chip pos-adv" style="padding:2px 8px;">Adverb</span>
                <span class="pos-chip pos-pron" style="padding:2px 8px;">Pronoun</span>
                <span class="pos-chip pos-other" style="padding:2px 8px;">Other</span>
            </div>
            """
            st.markdown(pos_legend, unsafe_allow_html=True)

            for i, sp in enumerate(pr.sentence_parses, start=1):
                sent_str = " ".join(t.text for t in sp.tokens)
                with st.expander(f"Sentence {i}: {sent_str[:85]}...", expanded=(i == 1)):
                    # Visual POS Chips
                    token_chips_html = '<div class="tokens-grid">'
                    for t in sp.tokens:
                        pos = t.pos.upper()
                        if pos in {"NOUN", "PROPN"}:
                            css_cls = "pos-noun"
                        elif pos in {"VERB", "AUX"}:
                            css_cls = "pos-verb"
                        elif pos in {"ADJ"}:
                            css_cls = "pos-adj"
                        elif pos in {"ADV"}:
                            css_cls = "pos-adv"
                        elif pos in {"PRON"}:
                            css_cls = "pos-pron"
                        else:
                            css_cls = "pos-other"

                        token_chips_html += f"""
                        <div class="pos-chip {css_cls}" title="Dep: {t.dep} | Head: {t.head}">
                            <span class="pos-word">{html.escape(t.text)}</span>
                            <span class="pos-tag">{t.pos} ({t.dep})</span>
                        </div>
                        """
                    token_chips_html += "</div>"
                    st.markdown(token_chips_html, unsafe_allow_html=True)

                    # CYK Parse Tree Display
                    st.markdown("**CYK Parse Tree** (Hand-built CFG):")
                    tree_str = build_parse_tree_string(sp.custom_parse_tree)
                    st.code(tree_str, language="text")

        # ---------------------------------------------------------------------
        # Stage 3 Sub-Tab
        # ---------------------------------------------------------------------
        with sub3:
            col_ner, col_wsd = st.columns([1, 1])

            # Named Entities
            with col_ner:
                st.markdown(
                    """
                    <div class="content-card">
                        <div class="card-header">
                            <h3>🏷️ Named Entities (NER)</h3>
                            <span class="card-tag tag-blue">spaCy</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                all_ents = [e for f in pr.semantic_frames for e in f.entities]
                if all_ents:
                    ent_html = '<div style="display:flex; flex-wrap:wrap; gap:8px;">'
                    for e in all_ents:
                        ent_html += f"""
                        <span style="background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.3); color:#38bdf8; padding:6px 12px; border-radius:8px; font-weight:600; font-size:0.9rem;">
                            {html.escape(e.text)} <span style="font-size:0.7rem; opacity:0.8; font-weight:800; text-transform:uppercase;">[{e.label}]</span>
                        </span>
                        """
                    ent_html += "</div>"
                    st.markdown(ent_html, unsafe_allow_html=True)
                else:
                    st.info("No named entities identified in this text.")
                st.markdown("</div>", unsafe_allow_html=True)

            # Word Sense Disambiguation
            with col_wsd:
                st.markdown(
                    """
                    <div class="content-card">
                        <div class="card-header">
                            <h3>📖 Word Sense Disambiguation</h3>
                            <span class="card-tag tag-amber">Lesk + WordNet</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                all_senses = {}
                for f in pr.semantic_frames:
                    all_senses.update(f.word_senses)

                if all_senses:
                    for target_word, syn_name in all_senses.items():
                        st.markdown(
                            f"""
                            <div class="wsd-card">
                                <div class="wsd-header">
                                    <span class="wsd-word">🎯 {html.escape(target_word.title())}</span>
                                    <span class="wsd-sense">{html.escape(syn_name)}</span>
                                </div>
                                <div class="wsd-def">Resolved using sentence context gloss overlap via WordNet.</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No target polysemous words (e.g., bank, bat, light) found.")
                st.markdown("</div>", unsafe_allow_html=True)

            # Semantic Role Labeling Frames
            st.markdown("#### 🎭 Semantic Role Frames (Agent ➔ Action ➔ Patient)")
            if pr.semantic_frames:
                for idx, frame in enumerate(pr.semantic_frames, start=1):
                    agent_val = frame.agent if frame.agent else "None"
                    action_val = frame.action if frame.action else "None"
                    patient_val = frame.patient if frame.patient else "None"

                    st.markdown(
                        f"""
                        <div class="srl-frame-card">
                            <div class="srl-sentence"><b>Sentence {idx}:</b> "{html.escape(frame.sentence)}"</div>
                            <div class="srl-flow">
                                <div class="srl-node srl-agent">
                                    <span class="srl-node-label">Agent (Subject)</span>
                                    <b>{html.escape(agent_val)}</b>
                                </div>
                                <span class="srl-arrow">➔</span>
                                <div class="srl-node srl-action">
                                    <span class="srl-node-label">Action (Predicate)</span>
                                    <b>{html.escape(action_val)}</b>
                                </div>
                                <span class="srl-arrow">➔</span>
                                <div class="srl-node srl-patient">
                                    <span class="srl-node-label">Patient (Object)</span>
                                    <b>{html.escape(patient_val)}</b>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No semantic role frames generated.")

        # ---------------------------------------------------------------------
        # Stage 4 Sub-Tab
        # ---------------------------------------------------------------------
        with sub4:
            # Pragmatic Inferences & Indirect Requests (High Impact)
            st.markdown("#### 💡 Pragmatics & Speech Act Inferences")
            if pr.pragmatic_notes:
                for note in pr.pragmatic_notes:
                    st.markdown(
                        f"""
                        <div class="pragmatic-alert">
                            <span class="pragmatic-badge">Polite Indirect Request</span>
                            <div class="pragmatic-surface">"{html.escape(note.surface_form)}"</div>
                            <div class="pragmatic-implied"><b>Inferred Directive:</b> {html.escape(note.paraphrase)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No indirect polite requests detected in this sample.")

            col_disc_left, col_disc_right = st.columns(2)

            # Coreference Chains
            with col_disc_left:
                st.markdown(
                    """
                    <div class="content-card">
                        <div class="card-header">
                            <h3>🔗 Coreference Chains</h3>
                            <span class="card-tag tag-purple">Discourse</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                if pr.coref_chains:
                    for chain in pr.coref_chains:
                        mentions_str = "  ➔  ".join(
                            f'<span class="chain-item">{html.escape(m)}</span>'
                            for m in chain.mentions
                        )
                        st.markdown(
                            f"""
                            <div class="coref-chain-card">
                                <span class="chain-badge">[{html.escape(chain.entity_type)}]</span>
                                <div>{mentions_str}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No coreference chains detected.")
                st.markdown("</div>", unsafe_allow_html=True)

            # Discourse Relations
            with col_disc_right:
                st.markdown(
                    """
                    <div class="content-card">
                        <div class="card-header">
                            <h3>🔄 Discourse Connectives</h3>
                            <span class="card-tag tag-blue">Coherence</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                if pr.discourse_relations:
                    for rel in pr.discourse_relations:
                        st.markdown(
                            f"""
                            <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:12px 16px; margin-bottom:10px;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                    <b style="color:#f8fafc;">Connective: <i>'{html.escape(rel.connective)}'</i></b>
                                    <span class="card-tag tag-amber">{html.escape(rel.relation.upper())}</span>
                                </div>
                                <div style="font-size:0.85rem; color:#94a3b8;">
                                    Sentences {rel.sentence_a} ➔ {rel.sentence_b}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No discourse connectives identified.")
                st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # Export Sub-Tab
        # ---------------------------------------------------------------------
        with sub_export:
            st.markdown("#### 📥 Pipeline Data Export")
            st.caption("Download the complete analysis payload for testing, benchmarking, or integration.")

            result_dict = {
                "corrected_text": pr.corrected_text,
                "corrections": [asdict(c) for c in pr.corrections],
                "sentence_count": len(pr.sentence_parses),
                "semantic_frames": [asdict(f) for f in pr.semantic_frames],
                "coref_chains": [asdict(c) for c in pr.coref_chains],
                "discourse_relations": [asdict(d) for d in pr.discourse_relations],
                "pragmatic_notes": [asdict(p) for p in pr.pragmatic_notes],
            }
            json_str = json.dumps(result_dict, indent=2)

            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                st.download_button(
                    label="💾 Download Structured JSON",
                    data=json_str,
                    file_name="nlp_pipeline_analysis.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with col_ex2:
                st.download_button(
                    label="📄 Download Cleaned Text (.txt)",
                    data=pr.corrected_text,
                    file_name="corrected_text.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            st.markdown("##### Payload Preview")
            st.json(result_dict)


# =============================================================================
# TAB 3: BENCHMARK & BATCH ANALYTICS
# =============================================================================

with tab_benchmarks:
    st.markdown("### 📊 Benchmark & Multi-Sample Evaluation")
    st.caption("Runs the end-to-end NLP pipeline over all standard evaluation samples, plus your active custom text.")

    if st.button("🚀 Run Batch Benchmark (Includes Custom Text)", type="primary", use_container_width=True):
        from summarize import run_on_samples
        from pipeline import process
        import time

        with st.spinner("Processing benchmark samples and custom text..."):
            summary_df, _ = run_on_samples()
            
            custom_text = st.session_state.get("editor_text", "").strip()
            if custom_text:
                t0 = time.perf_counter()
                result = process(custom_text)
                elapsed = time.perf_counter() - t0
                
                custom_row = {
                    "sample_id": "custom_input",
                    "num_spelling_corrections": len(result.corrections),
                    "num_entities": sum(len(f.entities) for f in result.semantic_frames),
                    "num_semantic_frames": len(result.semantic_frames),
                    "num_wsd": sum(len(f.word_senses) for f in result.semantic_frames),
                    "num_coref_chains": len(result.coref_chains),
                    "num_discourse_relations": len(result.discourse_relations),
                    "num_indirect_requests": len(result.pragmatic_notes),
                    "time_s": round(elapsed, 2),
                }
                
                # Append custom row to the top
                import pandas as pd
                custom_df = pd.DataFrame([custom_row])
                summary_df = pd.concat([custom_df, summary_df], ignore_index=True)

        st.success("✅ Batch benchmark completed!")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        csv_data = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Benchmark Results (.csv)",
            data=csv_data,
            file_name="pipeline_benchmark_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("Click the button above to execute the pipeline over all test samples and your custom text simultaneously.")


# -----------------------------------------------------------------------------
# 7. Footer
# -----------------------------------------------------------------------------

st.markdown("---")
st.markdown(
    """
    <div style="display:flex; justify-content:space-between; align-items:center; color:#64748b; font-size:0.85rem; padding:10px 0;">
        <div><b>Smart Reading & Writing Assistant</b> • Enterprise NLP Studio</div>
        <div>Built with Python, Streamlit, spaCy & NLTK</div>
    </div>
    """,
    unsafe_allow_html=True,
)
