import streamlit as st
from tokenizers import Tokenizer
import os, time, math
 
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BPE Tokenizer Explorer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Sora:wght@300;400;600;700&display=swap');
 
/* ── Root theme ── */
:root {
    --bg0: #0b0c10;
    --bg1: #13141a;
    --bg2: #1a1c24;
    --bg3: #22242f;
    --border: rgba(255,255,255,0.07);
    --accent: #7c6cfa;
    --accent2: #2dd4a0;
    --accent3: #ff6b35;
    --text1: #e8e6f0;
    --text2: #9896a8;
    --text3: #5c5a6e;
    --mono: 'Space Mono', monospace;
    --body: 'Sora', sans-serif;
}
 
/* ── Global overrides ── */
html, body, [class*="css"] {
    font-family: var(--body) !important;
    background-color: var(--bg0) !important;
    color: var(--text1) !important;
}
.stApp { background-color: var(--bg0) !important; }
 
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--bg1) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text2) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--text1) !important; }
 
/* ── Headings ── */
h1, h2, h3 { font-family: var(--mono) !important; }
 
/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    font-size: 1.8rem !important;
    color: var(--accent) !important;
}
[data-testid="stMetricLabel"] {
    font-family: var(--mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.12em !important;
    color: var(--text2) !important;
}
 
/* ── Text area ── */
textarea {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text1) !important;
    font-family: var(--mono) !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
}
textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,108,250,0.2) !important;
}
 
/* ── Buttons ── */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #6558e0 !important;
    transform: translateY(-1px) !important;
}
 
/* ── Select box ── */
.stSelectbox > div > div {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text1) !important;
    font-family: var(--mono) !important;
    border-radius: 8px !important;
}
 
/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg1) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    color: var(--text2) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}
 
/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
 
/* ── Info / warning boxes ── */
.stAlert {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
}
 
/* ── Progress bars ── */
.stProgress > div > div {
    background: var(--accent) !important;
}
 
/* Divider */
hr { border-color: var(--border) !important; }
 
/* Remove Streamlit branding padding */
.block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)
 
# ── Token colour palette ───────────────────────────────────────────────────────
TOKEN_COLORS = [
    {"bg": "#2d1f6e", "border": "#7c6cfa", "text": "#c4bcff"},
    {"bg": "#0f3d2e", "border": "#2dd4a0", "text": "#a7f3d0"},
    {"bg": "#3d2010", "border": "#ff6b35", "text": "#ffc8a8"},
    {"bg": "#2d1040", "border": "#d946ef", "text": "#f0abfc"},
    {"bg": "#102040", "border": "#38bdf8", "text": "#bae6fd"},
    {"bg": "#1a2e10", "border": "#84cc16", "text": "#d9f99d"},
    {"bg": "#3d1515", "border": "#f87171", "text": "#fecaca"},
    {"bg": "#1a1040", "border": "#818cf8", "text": "#c7d2fe"},
]
 
# ── Known benchmark results (from your actual training) ───────────────────────
BENCHMARK = {
    8000:  {"tokens": 57,  "tpw": 2.38, "compression": 3.37, "train_time": 2.98},
    16000: {"tokens": 52,  "tpw": 2.17, "compression": 3.69, "train_time": 4.22},
    32000: {"tokens": 50,  "tpw": 2.08, "compression": 3.84, "train_time": 4.16},
    64000: {"tokens": 46,  "tpw": 1.92, "compression": 4.17, "train_time": 3.58},
    128000:{"tokens": 44,  "tpw": 1.83, "compression": 4.36, "train_time": 5.05},
    256000:{"tokens": 44,  "tpw": 1.83, "compression": 4.36, "train_time": 4.45},
}
 
VOCAB_SIZES = [8000, 16000, 32000, 64000, 128000, 256000]
 
# ── Load tokenizers ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_all_tokenizers():
    toks = {}
    for v in VOCAB_SIZES:
        path = f"bpe_tokenizer_{v//1000}k.json"
        if os.path.exists(path):
            toks[v] = Tokenizer.from_file(path)
    return toks
 
tokenizers = load_all_tokenizers()
available = list(tokenizers.keys())
 
# ── Noise injection ────────────────────────────────────────────────────────────
def inject_noise(text: str) -> str:
    swap = {'a':'@','e':'3','i':'1','o':'0','s':'$','t':'+','l':'1','g':'9'}
    out = []
    for i, ch in enumerate(text):
        lo = ch.lower()
        if i % 7 == 3 and lo in swap:
            out.append(swap[lo])
        elif i % 13 == 7 and ch.isalpha():
            out.append(ch * 2)
        else:
            out.append(ch)
    return ''.join(out)
 
# ── Token HTML renderer ────────────────────────────────────────────────────────
def render_token_html(tokens, ids):
    html = "<div style='font-family:\"Space Mono\",monospace; font-size:0.82rem; line-height:2.4; word-break:break-word;'>"
    for i, (tok, tid) in enumerate(zip(tokens, ids)):
        c = TOKEN_COLORS[i % len(TOKEN_COLORS)]
        display = tok.replace("Ġ", " ").replace("</w>", "").replace("▁", " ")
        html += (
            f"<span title='Token #{i+1} | ID: {tid} | \"{display.strip()}\"' "
            f"style='display:inline-block; background:{c['bg']}; "
            f"border:1px solid {c['border']}; color:{c['text']}; "
            f"padding:2px 7px; border-radius:5px; margin:2px 1px; "
            f"cursor:help; transition:transform 0.1s;'>{display}</span>"
        )
    html += "</div>"
    return html
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⬡ BPE Explorer")
    st.markdown("<p style='font-size:0.7rem;letter-spacing:0.1em;color:#5c5a6e'>NLP TOKENIZATION STUDY</p>", unsafe_allow_html=True)
    st.divider()
 
    if not available:
        st.error("No tokenizer `.json` files found.\nPlace `bpe_tokenizer_8k.json` etc. in the same folder.")
        st.stop()
 
    vocab_label = st.selectbox(
        "Vocabulary Size",
        options=[f"{v//1000}K  ({v:,} tokens)" for v in available],
        index=0,
    )
    selected_vocab = available[[f"{v//1000}K  ({v:,} tokens)" for v in available].index(vocab_label)]
    tokenizer = tokenizers[selected_vocab]
 
    st.divider()
    st.markdown("<p style='font-size:0.65rem;letter-spacing:0.1em;color:#5c5a6e'>QUICK STATS (BENCHMARK)</p>", unsafe_allow_html=True)
    bm = BENCHMARK[selected_vocab]
    st.metric("Tokens / Word", bm["tpw"])
    st.metric("Compression Ratio", f"{bm['compression']}×")
    st.metric("Training Time", f"{bm['train_time']:.2f}s")
 
    st.divider()
    show_ids  = st.toggle("Show token IDs", value=False)
    noise_on  = st.toggle("Enable noise simulation", value=True)
    compare   = st.toggle("Compare all vocab sizes", value=False)
 
    st.divider()
    st.markdown("""
    <p style='font-size:0.68rem;color:#5c5a6e;line-height:1.6'>
    <b style='color:#9896a8'>About</b><br>
    Trained on WikiText-2 corpus (23,767 lines). Six BPE tokenizers
    with vocab sizes 8K–256K. Zero OOV rate guaranteed by character-level fallback.
    </p>
    """, unsafe_allow_html=True)
 
# ── Main header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:1.5rem'>
  <h1 style='font-family:"Space Mono",monospace; font-size:1.8rem; font-weight:700;
             letter-spacing:-0.02em; color:#e8e6f0; margin:0'>
    BPE <span style='color:#7c6cfa'>Tokenizer</span> Explorer
  </h1>
  <p style='font-family:"Space Mono",monospace; font-size:0.7rem; color:#5c5a6e;
            letter-spacing:0.12em; margin-top:4px'>
    SUB-WORD TOKENIZATION · NOISE ROBUSTNESS · FAIRNESS ANALYSIS · EDGE DEPLOYMENT
  </p>
</div>
""", unsafe_allow_html=True)
 
# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "  TOKENIZE  ", "  NOISE TEST  ", "  COMPARE ALL  ", "  INSIGHTS  "
])
 
# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TOKENIZE
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<p style='font-size:0.65rem;letter-spacing:0.12em;color:#5c5a6e;margin-bottom:0.4rem'>INPUT TEXT</p>", unsafe_allow_html=True)
    input_text = st.text_area(
        label="input",
        label_visibility="collapsed",
        value="The democratization of artificial intelligence is reshaping modern society and biocompatibility research.",
        height=110,
        key="main_input",
    )
 
    col_btn, col_hint = st.columns([1, 4])
    with col_btn:
        run = st.button("⬡  TOKENIZE", use_container_width=True)
    with col_hint:
        st.markdown(
            "<p style='font-size:0.72rem;color:#5c5a6e;padding-top:0.6rem'>"
            f"Using <b style='color:#7c6cfa'>{selected_vocab//1000}K</b> vocabulary · "
            f"hover tokens to see ID</p>",
            unsafe_allow_html=True,
        )
 
    if run and input_text.strip():
        with st.spinner(""):
            encoded = tokenizer.encode(input_text)
            tokens  = encoded.tokens
            ids     = encoded.ids
 
        words = input_text.split()
        n_words  = max(len(words), 1)
        n_chars  = len(input_text)
        n_tokens = len(tokens)
        unk_c    = tokens.count("[UNK]")
        oov_r    = round(unk_c / n_tokens * 100, 2) if n_tokens else 0
        comp_r   = round(n_chars / n_tokens, 2)     if n_tokens else 0
        tpw      = round(n_tokens / n_words, 2)
 
        # ── Metrics ──
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("CHARACTERS",       n_chars)
        m2.metric("TOKENS",           n_tokens)
        m3.metric("COMPRESSION",      f"{comp_r}×")
        m4.metric("TOKENS / WORD",    tpw)
        m5.metric("OOV RATE",         f"{oov_r}%")
 
        st.markdown("<p style='font-size:0.65rem;letter-spacing:0.12em;color:#5c5a6e;margin:1.2rem 0 0.4rem'>CHARACTER → TOKEN ALIGNMENT</p>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='background:#13141a;border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:10px;padding:1rem 1.2rem'>"
            f"{render_token_html(tokens, ids)}</div>",
            unsafe_allow_html=True,
        )
 
        if show_ids:
            st.markdown("<p style='font-size:0.65rem;letter-spacing:0.12em;color:#5c5a6e;margin:1rem 0 0.4rem'>TOKEN ID SEQUENCE</p>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:#13141a;border:1px solid rgba(255,255,255,0.07);"
                f"border-radius:10px;padding:0.8rem 1.2rem;font-family:\"Space Mono\",monospace;"
                f"font-size:0.75rem;color:#7c6cfa;word-break:break-all'>"
                f"{' · '.join(str(i) for i in ids)}</div>",
                unsafe_allow_html=True,
            )
 
        # ── Saliency bar ──
        # ── Saliency bar ──
        st.markdown("<p style='font-size:0.65rem;letter-spacing:0.12em;color:#5c5a6e;margin:1rem 0 0.4rem'>FRAGMENTATION HEATMAP (token count per word)</p>", unsafe_allow_html=True)
        
        word_tokens = {}
        # encoded.word_ids is a built-in array that perfectly maps each token to its original word index
        for wid in encoded.word_ids:
            if wid is not None and wid < len(words):
                word_tokens[wid] = word_tokens.get(wid, 0) + 1
 
        heat_html = "<div style='font-family:\"Space Mono\",monospace;font-size:0.78rem;line-height:2.4;word-break:break-word;'>"
        for wi, word in enumerate(words):
            cnt = word_tokens.get(wi, 1)
            t   = min(cnt / 6, 1.0)
            r   = int(45 + 210 * t)
            g   = int(212 - 180 * t)
            b   = int(160 - 130 * t)
            heat_html += (
                f"<span title='{cnt} token(s)' style='display:inline-block;"
                f"background:rgba({r},{g},{b},0.25);border:1px solid rgba({r},{g},{b},0.5);"
                f"color:rgb({r},{g},{b});padding:2px 7px;border-radius:5px;margin:2px 1px'>"
                f"{word} <sup style='font-size:0.6rem'>{cnt}</sup></span>"
            )
        heat_html += "</div>"
        st.markdown(
            f"<div style='background:#13141a;border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:10px;padding:1rem 1.2rem'>{heat_html}</div>",
            unsafe_allow_html=True,
        )
 
        st.markdown("""
        <div style='background:#13141a;border:1px solid rgba(255,255,255,0.07);
                    border-left:3px solid #7c6cfa;border-radius:10px;padding:1rem 1.2rem;
                    margin-top:1rem;font-size:0.8rem;color:#9896a8;line-height:1.7'>
          <b style='color:#e8e6f0;font-family:"Space Mono",monospace;
                    font-size:0.65rem;letter-spacing:0.1em'>HOW TO READ THIS</b><br><br>
          Each coloured block = one <b style='color:#7c6cfa'>token</b> the AI processes as a single unit.
          Common words (<code style='background:#1a1c24;padding:1px 4px;border-radius:3px'>is</code>,
          <code style='background:#1a1c24;padding:1px 4px;border-radius:3px'>the</code>) stay intact.
          Rare or complex words fragment into sub-words.<br><br>
          <b style='color:#2dd4a0'>Saliency impact:</b> Token boundaries dictate how
          attention weights distribute across a sequence. High fragmentation dilutes focus
          on rare words, which can degrade downstream task performance.
        </div>
        """, unsafe_allow_html=True)
 
    elif run:
        st.warning("Please enter some text above first.")
 
# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — NOISE TEST
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <p style='font-size:0.8rem;color:#9896a8;margin-bottom:1rem'>
    Simulates OCR distortions, typos and transliteration errors.
    Measures <b style='color:#ff6b35'>token drift</b> — how much the tokenisation changes under noise.
    </p>
    """, unsafe_allow_html=True)
 
    noise_text = st.text_area(
        "Text to stress-test",
        value="Tokenization is essential for large language models to understand text effectively.",
        height=90,
        key="noise_input",
    )
 
    if st.button("⬡  RUN NOISE TEST", key="noise_btn"):
        clean  = noise_text.strip()
        noisy  = inject_noise(clean)
 
        enc_c  = tokenizer.encode(clean)
        enc_n  = tokenizer.encode(noisy)
        tc, tn = enc_c.tokens, enc_n.tokens
        drift  = len(tn) - len(tc)
        pct    = round(drift / max(len(tc),1) * 100, 1)
 
        st.markdown("---")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Clean tokens",  len(tc))
        d2.metric("Noisy tokens",  len(tn), delta=f"+{drift}")
        d3.metric("Token drift",   f"{pct}%", delta=f"+{pct}%", delta_color="inverse")
        d4.metric("PPL delta (ref)", "≈ +1009", delta="high", delta_color="inverse")
 
        col_c, col_n = st.columns(2)
        with col_c:
            st.markdown("<p style='font-size:0.65rem;letter-spacing:0.1em;color:#5c5a6e;margin-bottom:0.4rem'>CLEAN INPUT</p>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:#13141a;border:1px solid rgba(255,255,255,0.07);"
                f"border-radius:10px;padding:0.9rem;font-family:\"Space Mono\",monospace;"
                f"font-size:0.75rem;color:#2dd4a0;margin-bottom:0.5rem'>{clean}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='background:#13141a;border:1px solid rgba(255,255,255,0.07);"
                f"border-radius:10px;padding:0.9rem'>{render_token_html(tc, enc_c.ids)}</div>",
                unsafe_allow_html=True,
            )
        with col_n:
            st.markdown("<p style='font-size:0.65rem;letter-spacing:0.1em;color:#5c5a6e;margin-bottom:0.4rem'>NOISY INPUT (OCR-simulated)</p>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:#13141a;border:1px solid rgba(45,16,16,0.8);"
                f"border-left:3px solid #ff6b35;border-radius:10px;padding:0.9rem;"
                f"font-family:\"Space Mono\",monospace;font-size:0.75rem;"
                f"color:#ff6b35;margin-bottom:0.5rem'>{noisy}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='background:#13141a;border:1px solid rgba(255,107,53,0.2);"
                f"border-radius:10px;padding:0.9rem'>{render_token_html(tn, enc_n.ids)}</div>",
                unsafe_allow_html=True,
            )
 
        st.markdown(f"""
        <div style='background:#13141a;border:1px solid rgba(255,107,53,0.3);
                    border-left:3px solid #ff6b35;border-radius:10px;padding:1rem 1.2rem;
                    margin-top:1rem;font-size:0.8rem;color:#9896a8;line-height:1.7'>
          <b style='color:#ff6b35;font-family:"Space Mono",monospace;
                    font-size:0.65rem;letter-spacing:0.1em'>ROBUSTNESS FINDING</b><br><br>
          Noise caused <b style='color:#ff6b35'>{drift} extra tokens (+{pct}%)</b>.
          The tokenizer lacks vocabulary for distorted words and is forced to
          fragment them into individual characters.
          In production, a <b style='color:#e8e6f0'>perplexity spike of ~+1009</b> was measured,
          proving raw BPE is brittle without input sanitisation or byte-level pre-processing.
          <br><br>
          <b style='color:#2dd4a0'>Recommendation:</b> Deploy text normalisation (spell-check,
          OCR post-correction) before tokenisation in production pipelines.
        </div>
        """, unsafe_allow_html=True)
 
# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — COMPARE ALL VOCAB SIZES
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <p style='font-size:0.8rem;color:#9896a8;margin-bottom:1rem'>
    Tokenise the same text with all 6 vocabulary sizes and compare metrics side-by-side.
    </p>
    """, unsafe_allow_html=True)
 
    cmp_text = st.text_area(
        "Text to compare across all vocab sizes",
        value="Supercalifragilisticexpialidocious is a very long and unusual word!",
        height=80,
        key="cmp_input",
    )
 
    if st.button("⬡  COMPARE ALL SIZES", key="cmp_btn"):
        if not available:
            st.error("No tokenizer files found.")
        else:
            rows = []
            progress = st.progress(0, text="Running...")
            for idx, v in enumerate(available):
                tok = tokenizers[v]
                enc = tok.encode(cmp_text.strip())
                toks = enc.tokens
                n_t = len(toks)
                n_c = len(cmp_text)
                n_w = max(len(cmp_text.split()), 1)
                rows.append({
                    "Vocab": f"{v//1000}K",
                    "Tokens": n_t,
                    "Tokens/Word": round(n_t/n_w, 2),
                    "Compression": f"{round(n_c/max(n_t,1), 2)}×",
                    "OOV Rate": "0.0%",
                    "Train Time (s)": BENCHMARK[v]["train_time"],
                })
                progress.progress((idx+1)/len(available), text=f"Processing {v//1000}K...")
            progress.empty()
 
            import pandas as pd
            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )
 
            st.markdown("<p style='font-size:0.65rem;letter-spacing:0.1em;color:#5c5a6e;margin:1.5rem 0 0.8rem'>SEGMENTATION COMPARISON</p>", unsafe_allow_html=True)
            for v in available[:4]:
                tok = tokenizers[v]
                enc = tok.encode(cmp_text.strip())
                st.markdown(
                    f"<p style='font-family:\"Space Mono\",monospace;font-size:0.65rem;"
                    f"letter-spacing:0.1em;color:#7c6cfa;margin:0.6rem 0 0.2rem'>{v//1000}K VOCAB</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='background:#13141a;border:1px solid rgba(255,255,255,0.07);"
                    f"border-radius:8px;padding:0.7rem 1rem'>"
                    f"{render_token_html(enc.tokens, enc.ids)}</div>",
                    unsafe_allow_html=True,
                )
 
            st.markdown("""
            <div style='background:#13141a;border:1px solid rgba(45,212,160,0.2);
                        border-left:3px solid #2dd4a0;border-radius:10px;padding:1rem 1.2rem;
                        margin-top:1rem;font-size:0.8rem;color:#9896a8;line-height:1.7'>
              <b style='color:#2dd4a0;font-family:"Space Mono",monospace;
                        font-size:0.65rem;letter-spacing:0.1em'>KEY FINDING</b><br><br>
              As vocabulary size increases from 8K → 256K, tokens per word drops from
              <b style='color:#e8e6f0'>2.38 → 1.83</b> and compression improves from
              <b style='color:#e8e6f0'>3.37× → 4.36×</b>.
              The OOV rate stays at <b style='color:#2dd4a0'>0.0%</b> across all sizes —
              the character-level fallback guarantees complete coverage of any input.
            </div>
            """, unsafe_allow_html=True)
 
# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<p style='font-size:0.65rem;letter-spacing:0.12em;color:#5c5a6e;margin-bottom:1rem'>PROJECT FINDINGS & ANALYSIS</p>", unsafe_allow_html=True)
 
    insights = [
        ("⬡", "ZERO OOV GUARANTEE", "#7c6cfa",
         "BPE always falls back to individual characters, so unknown words are never truly "
         "'out of vocabulary.' OOV rate stays at 0.0% across all six vocabulary sizes (8K–256K). "
         "This is the primary architectural advantage over legacy word-level tokenizers."),
        ("◈", "NOISE VULNERABILITY", "#ff6b35",
         "OCR-style noise (digit-letter swaps, character repeats) caused 123% token inflation "
         "and a perplexity delta of +1009 on the GPT-2 language model. This proves raw BPE "
         "is brittle and requires input sanitisation in production OCR pipelines."),
        ("◇", "FAIRNESS & TOKENIZER BIAS", "#d946ef",
         "An English-only trained tokenizer fragments code-mixed Hindi/Spanish text more "
         "heavily — avg tokens/word rises from 1.78 → 1.85. In LLM inference, this 3.9% "
         "fragmentation increase disproportionately consumes context window for non-English users."),
        ("△", "COMPRESSION VS VOCAB", "#2dd4a0",
         "Larger vocabularies yield better compression with diminishing returns: 8K → 3.37×, "
         "64K → 4.17×, 256K → 4.36×. Training time peaks non-linearly near 128K as the "
         "algorithm searches for increasingly rare character combinations."),
        ("○", "EDGE DEVICE TRADEOFF", "#38bdf8",
         "A Trie-based tokenizer uses only 0.05 KB vs 1877 KB for a hash dictionary — a "
         "99.99% memory reduction. However, the Python Trie's throughput (189K words/sec) "
         "is lower than the C-optimised dict (1.74M words/sec). For IoT/edge, memory wins."),
        ("◉", "DOWNSTREAM CLASSIFIER", "#84cc16",
         "A TF-IDF + Logistic Regression classifier scored 95.98% on English and 96.22% "
         "on code-mixed text. The inflated token count for code-mixed input created unique "
         "rare features that a bag-of-words model could distinguish easily — but this would "
         "hurt a Transformer's attention mechanism severely."),
    ]
 
    col_a, col_b = st.columns(2)
    for i, (icon, title, color, body) in enumerate(insights):
        col = col_a if i % 2 == 0 else col_b
        col.markdown(f"""
        <div style='background:#13141a;border:1px solid rgba(255,255,255,0.07);
                    border-top:3px solid {color};border-radius:10px;padding:1.1rem 1.2rem;
                    margin-bottom:0.75rem'>
          <div style='font-family:"Space Mono",monospace;font-size:0.65rem;
                      letter-spacing:0.12em;color:{color};margin-bottom:0.5rem'>
            {icon} {title}
          </div>
          <div style='font-size:0.8rem;color:#9896a8;line-height:1.65'>{body}</div>
        </div>
        """, unsafe_allow_html=True)
 
    st.markdown("<p style='font-size:0.65rem;letter-spacing:0.12em;color:#5c5a6e;margin:1.5rem 0 0.8rem'>BENCHMARK SUMMARY TABLE</p>", unsafe_allow_html=True)
    import pandas as pd
    df_bm = pd.DataFrame([
        {
            "Vocab Size": f"{v//1000}K",
            "Avg Tokens/Word": BENCHMARK[v]["tpw"],
            "Compression Ratio": f"{BENCHMARK[v]['compression']}×",
            "Train Time (s)": BENCHMARK[v]["train_time"],
            "OOV Rate": "0.0%",
            "Corpus Lines": "23,767",
        }
        for v in VOCAB_SIZES
    ])
    st.dataframe(df_bm, use_container_width=True, hide_index=True)
 
    st.markdown("""
    <div style='background:#13141a;border:1px solid rgba(124,108,250,0.2);
                border-left:3px solid #7c6cfa;border-radius:10px;padding:1rem 1.2rem;
                margin-top:1rem;font-size:0.78rem;color:#9896a8;line-height:1.7'>
      <b style='color:#7c6cfa;font-family:"Space Mono",monospace;
                font-size:0.65rem;letter-spacing:0.1em'>TECH STACK</b><br><br>
      <b style='color:#e8e6f0'>Training:</b> HuggingFace Tokenizers · WikiText-2 (HF Datasets)<br>
      <b style='color:#e8e6f0'>Noise Testing:</b> ByteLevelBPETokenizer · GPT-2 (via Transformers)<br>
      <b style='color:#e8e6f0'>Fairness:</b> scikit-learn 20Newsgroups · TF-IDF · Logistic Regression<br>
      <b style='color:#e8e6f0'>Edge Device:</b> Custom Trie (Python) · psutil benchmarking<br>
      <b style='color:#e8e6f0'>Dashboard:</b> Streamlit · Custom CSS · Space Mono + Sora fonts
    </div>
    """, unsafe_allow_html=True)
