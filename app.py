"""
AccelWealth — Premium Investment Dashboard
Glassmorphism UI · Custom Nav · Advanced Charts
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

from stock_data import (
    fetch_price_history,
    get_technical_indicators,
    get_info,
    format_inr,
)

# ───────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AccelWealth",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────────────────────────────────────────────────
# MASTER CSS
# ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* ────────── Design Tokens ────────── */
:root {
  --bg0:         #050810;
  --bg1:         #090d1a;
  --bg2:         #0d1224;
  --glass:       rgba(255,255,255,0.035);
  --glass-hover: rgba(255,255,255,0.07);
  --glass-active:rgba(91,138,240,0.12);
  --border:      rgba(255,255,255,0.07);
  --border-glow: rgba(91,138,240,0.4);
  --blue:        #5b8af0;
  --purple:      #a78bfa;
  --cyan:        #22d3ee;
  --green:       #34d399;
  --yellow:      #fbbf24;
  --red:         #f87171;
  --text0:       #f8faff;
  --text1:       #c4cee8;
  --text2:       #6b7fa8;
  --r:           16px;
  --r-sm:        10px;
  --font:        'Inter', system-ui, sans-serif;
  --mono:        'JetBrains Mono', monospace;
}

/* ────────── Global Reset ────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: var(--font) !important; }

.stApp {
  background: var(--bg0) !important;
  background-image:
    radial-gradient(ellipse 80% 50% at 20% -10%, rgba(91,138,240,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 100%, rgba(167,139,250,0.06) 0%, transparent 55%);
  min-height: 100vh;
}

/* ────────── Hide Streamlit Chrome ────────── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton { display: none !important; }

/* ────────── Sidebar Shell ────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0a0f1e 0%, #080c18 100%) !important;
  border-right: 1px solid var(--border) !important;
  width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
  overflow-x: hidden;
}
/* Remove all default Streamlit sidebar padding */
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
  padding: 0 !important;
}

/* ────────── Brand Block ────────── */
.sw-brand {
  padding: 26px 20px 18px;
  border-bottom: 1px solid var(--border);
}
.sw-brand-logo {
  font-size: 20px;
  font-weight: 900;
  letter-spacing: -0.8px;
  background: linear-gradient(100deg, #5b8af0 0%, #a78bfa 60%, #22d3ee 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.sw-brand-sub {
  font-size: 9.5px;
  font-weight: 600;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--text2);
  margin-top: 2px;
}

/* ────────── Ticker Search ────────── */
.sw-search { padding: 14px 14px 4px; }
[data-testid="stSidebar"] [data-testid="stTextInput"] label { display: none; }
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text0) !important;
  font-family: var(--mono) !important;
  font-size: 13px !important;
  padding: 9px 14px !important;
  transition: all 0.2s;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px rgba(91,138,240,0.2) !important;
  background: rgba(91,138,240,0.06) !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
  color: var(--text2) !important;
}

/* ────────── Nav Section Labels ────────── */
.sw-nav-section {
  padding: 16px 20px 5px;
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--text2);
}

/* ────────── Nav Item HTML ────────── */
.sw-nav-item {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 10px 16px;
  margin: 2px 10px;
  border-radius: var(--r-sm);
  border: 1px solid transparent;
  transition: all 0.18s ease;
  cursor: pointer;
}
.sw-nav-item:hover {
  background: var(--glass-hover);
  border-color: var(--border);
}
.sw-nav-item.sw-active {
  background: linear-gradient(120deg, rgba(91,138,240,0.18) 0%, rgba(167,139,250,0.10) 100%);
  border-color: rgba(91,138,240,0.35);
  box-shadow: 0 2px 20px rgba(91,138,240,0.15), inset 0 0 12px rgba(91,138,240,0.05);
}
.sw-nav-icon {
  font-size: 17px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}
.sw-nav-label {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text1);
  flex: 1;
}
.sw-nav-item.sw-active .sw-nav-label { color: var(--text0); font-weight: 600; }
.sw-nav-badge {
  font-size: 9.5px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  background: rgba(91,138,240,0.2);
  color: var(--blue);
  border: 1px solid rgba(91,138,240,0.3);
}

/* ────────── Hide / Collapse Nav Buttons ────────── */
[data-testid="stSidebar"] .stButton > button {
  all: unset !important;
  display: block !important;
  width: 100% !important;
  height: 1px !important;
  opacity: 0 !important;
  cursor: pointer !important;
  margin: -1px 0 0 !important;
  padding: 0 !important;
  pointer-events: auto !important;
  position: relative !important;
  z-index: 10 !important;
}

/* ────────── Sidebar Period Pills ────────── */
.sw-period-grid {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 6px;
  padding: 6px 14px 4px;
}
[data-testid="stSidebar"] .stButton.period-btn > button {
  all: unset !important;
  display: block !important;
  width: 100% !important;
  text-align: center !important;
  padding: 6px 4px !important;
  border-radius: 8px !important;
  border: 1px solid var(--border) !important;
  background: rgba(255,255,255,0.03) !important;
  color: var(--text2) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
  opacity: 1 !important;
  height: auto !important;
  margin: 0 !important;
}
[data-testid="stSidebar"] .stButton.period-btn > button:hover {
  background: rgba(91,138,240,0.12) !important;
  border-color: rgba(91,138,240,0.4) !important;
  color: var(--text0) !important;
}

/* ────────── Sidebar Checkboxes (Indicators) ────────── */
[data-testid="stSidebar"] .stCheckbox {
  padding: 2px 14px;
}
[data-testid="stSidebar"] .stCheckbox label {
  font-size: 13px !important;
  color: var(--text2) !important;
  font-weight: 400;
  gap: 8px;
}
[data-testid="stSidebar"] .stCheckbox label:hover { color: var(--text1) !important; }

/* ────────── Main Content ────────── */
.block-container {
  padding: 20px 32px 40px !important;
  max-width: 100% !important;
}

/* ────────── Page Hero ────────── */
.sw-hero {
  padding: 6px 0 22px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}
.sw-hero-eyebrow {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--blue);
  margin-bottom: 6px;
}
.sw-hero-title {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -1px;
  color: var(--text0);
  margin: 0 0 4px;
  line-height: 1;
}
.sw-hero-meta {
  font-size: 13.5px;
  color: var(--text2);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.sw-hero-dot { color: var(--border); }

/* ────────── Metric Cards ────────── */
.sw-metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
  gap: 12px;
  margin-bottom: 28px;
}
.sw-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 18px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
  transition: all 0.22s ease;
}
.sw-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--r);
  background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 60%);
  pointer-events: none;
}
.sw-card:hover {
  border-color: rgba(91,138,240,0.3);
  background: var(--glass-hover);
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(91,138,240,0.1);
}
.sw-card-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--text2);
  margin-bottom: 10px;
}
.sw-card-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text0);
  letter-spacing: -0.5px;
  font-family: var(--mono);
  line-height: 1;
}
.sw-card-sub {
  font-size: 12px;
  font-weight: 500;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.sw-green { color: var(--green); }
.sw-red   { color: var(--red);   }
.sw-muted { color: var(--text2); }

/* ────────── Section Heading ────────── */
.sw-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 28px 0 14px;
}
.sw-section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text0);
  white-space: nowrap;
}
.sw-section-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--border) 0%, transparent 100%);
}

/* ────────── Fundamentals Table ────────── */
.sw-fund-block {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--r);
  overflow: hidden;
  backdrop-filter: blur(12px);
}
.sw-fund-heading {
  padding: 14px 18px 10px;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--text2);
  border-bottom: 1px solid var(--border);
}
.sw-fund-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 18px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  transition: background 0.15s;
}
.sw-fund-row:last-child { border-bottom: none; }
.sw-fund-row:hover { background: var(--glass-hover); }
.sw-fund-key {
  font-size: 13px;
  color: var(--text2);
}
.sw-fund-val {
  font-size: 13px;
  font-weight: 600;
  color: var(--text0);
  font-family: var(--mono);
}

/* ────────── News Cards ────────── */
.sw-news-card {
  display: flex;
  gap: 14px;
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 16px 18px;
  margin-bottom: 10px;
  text-decoration: none !important;
  transition: all 0.18s;
  position: relative;
  overflow: hidden;
}
.sw-news-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, var(--blue), var(--purple));
  opacity: 0;
  transition: opacity 0.2s;
}
.sw-news-card:hover {
  border-color: rgba(91,138,240,0.3);
  background: var(--glass-hover);
  transform: translateX(3px);
}
.sw-news-card:hover::before { opacity: 1; }
.sw-news-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text0);
  line-height: 1.45;
  margin-bottom: 6px;
}
.sw-news-meta {
  font-size: 11.5px;
  color: var(--text2);
  display: flex;
  gap: 8px;
  align-items: center;
}
.sw-news-dot { color: rgba(255,255,255,0.15); }
.sw-news-pub {
  background: rgba(91,138,240,0.12);
  color: var(--blue);
  border-radius: 5px;
  padding: 1px 7px;
  font-weight: 600;
  font-size: 10.5px;
}

/* ────────── Chart container ────────── */
.sw-chart-wrap {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 6px;
  backdrop-filter: blur(12px);
  margin-bottom: 8px;
}

/* ────────── Status chips ────────── */
.sw-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 11px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}
.sw-chip-blue   { background: rgba(91,138,240,0.15); color: var(--blue); border: 1px solid rgba(91,138,240,0.25); }
.sw-chip-green  { background: rgba(52,211,153,0.12); color: var(--green); border: 1px solid rgba(52,211,153,0.25); }
.sw-chip-yellow { background: rgba(251,191,36,0.12); color: var(--yellow); border: 1px solid rgba(251,191,36,0.25); }
.sw-chip-red    { background: rgba(248,113,113,0.12); color: var(--red); border: 1px solid rgba(248,113,113,0.25); }

/* ────────── Info Banner ────────── */
.sw-banner {
  background: rgba(91,138,240,0.08);
  border: 1px solid rgba(91,138,240,0.2);
  border-radius: var(--r-sm);
  padding: 12px 16px;
  font-size: 13px;
  color: var(--text1);
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 16px;
}

/* ────────── Period pill active state ────────── */
.period-active > button {
  background: rgba(91,138,240,0.25) !important;
  border-color: var(--blue) !important;
  color: var(--text0) !important;
  box-shadow: 0 0 10px rgba(91,138,240,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────
# SESSION STATE
# ───────────────────────────────────────────────────────────────────
defaults = {
    "page":       "Dashboard",
    "ticker":     "RELIANCE.NS",
    "period":     "1y",
    "show_ma20":  True,
    "show_ma50":  True,
    "show_ma200": False,
    "show_bb":    False,
    "show_rsi":   True,
    "show_vol":   True,
    "chart_type": "Candlestick",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ───────────────────────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("📊", "Dashboard",    None),
    ("📈", "Price Chart",  "Live"),
    ("🔍", "Fundamentals", None),
    ("📰", "News",         None),
    ("⚙️", "Settings",    None),
]

PERIODS = [
    ("1mo", "1M"), ("3mo", "3M"), ("6mo", "6M"),
    ("1y",  "1Y"), ("2y",  "2Y"), ("5y",  "5Y"),
]

with st.sidebar:
    # ── Brand ──
    st.markdown("""
    <div class="sw-brand">
        <div class="sw-brand-logo">⚡ AccelWealth</div>
        <div class="sw-brand-sub">Smart Wealth Acceleration</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Ticker search ──
    st.markdown('<div class="sw-search">', unsafe_allow_html=True)
    raw = st.text_input(
        "ticker",
        value=st.session_state.ticker,
        placeholder="🔎  e.g. RELIANCE.NS, TSLA",
        key="_ticker_raw",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if raw and raw.strip().upper() != st.session_state.ticker:
        st.session_state.ticker = raw.strip().upper()
        st.rerun()

    # ── Navigation ──
    st.markdown('<div class="sw-nav-section">Navigation</div>', unsafe_allow_html=True)
    for icon, page_id, badge in NAV_ITEMS:
        active_cls = "sw-active" if st.session_state.page == page_id else ""
        badge_html = f'<span class="sw-nav-badge">{badge}</span>' if badge else ""
        st.markdown(f"""
        <div class="sw-nav-item {active_cls}">
            <span class="sw-nav-icon">{icon}</span>
            <span class="sw-nav-label">{page_id}</span>
            {badge_html}
        </div>""", unsafe_allow_html=True)
        if st.button(page_id, key=f"_nav_{page_id}"):
            st.session_state.page = page_id
            st.rerun()

    # ── Period selector ──
    st.markdown('<div class="sw-nav-section">Time Period</div>', unsafe_allow_html=True)
    p_cols = st.columns(3)
    for i, (pkey, plabel) in enumerate(PERIODS):
        active = st.session_state.period == pkey
        with p_cols[i % 3]:
            label = f"• {plabel}" if active else plabel
            if st.button(label, key=f"_p_{pkey}", width='stretch'):
                st.session_state.period = pkey
                st.rerun()

    # ── Indicators ──
    st.markdown('<div class="sw-nav-section">Indicators</div>', unsafe_allow_html=True)
    st.session_state.show_ma20  = st.checkbox("MA 20",       value=st.session_state.show_ma20,  key="_ma20")
    st.session_state.show_ma50  = st.checkbox("MA 50",       value=st.session_state.show_ma50,  key="_ma50")
    st.session_state.show_ma200 = st.checkbox("MA 200",      value=st.session_state.show_ma200, key="_ma200")
    st.session_state.show_bb    = st.checkbox("Bollinger",   value=st.session_state.show_bb,    key="_bb")
    st.session_state.show_rsi   = st.checkbox("RSI Panel",   value=st.session_state.show_rsi,   key="_rsi")
    st.session_state.show_vol   = st.checkbox("Volume Bar",  value=st.session_state.show_vol,   key="_vol")

    # ── Chart style ──
    st.markdown('<div class="sw-nav-section">Chart Style</div>', unsafe_allow_html=True)
    st.session_state.chart_type = st.radio(
        "chart_type",
        ["Candlestick", "Line", "Area"],
        index=["Candlestick", "Line", "Area"].index(st.session_state.chart_type),
        key="_chart_type",
        label_visibility="collapsed",
    )

    # Sidebar footer
    st.markdown("""
    <div style="padding:20px 16px 8px; border-top:1px solid rgba(255,255,255,0.06); margin-top:20px;">
        <div style="font-size:10px;color:#3d4f72;text-align:center;letter-spacing:0.5px;">
            Data via Yahoo Finance · AccelWealth v2
        </div>
    </div>
    """, unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
# DATA
# ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_all(ticker: str, period: str):
    df   = fetch_price_history(ticker, period)
    info = get_info(ticker)
    return df, info

with st.spinner(""):
    df, info = load_all(st.session_state.ticker, st.session_state.period)

has_data  = not df.empty
indicators = get_technical_indicators(df) if has_data else {}


# ───────────────────────────────────────────────────────────────────
# CHART BUILDER
# ───────────────────────────────────────────────────────────────────
PLOT_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#6b7fa8", size=11),
    margin=dict(l=4, r=4, t=10, b=4),
    xaxis_rangeslider_visible=False,
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#111827",
        bordercolor="#374151",
        font_family="JetBrains Mono",
        font_size=12,
    ),
)

def _xaxis(): return dict(gridcolor="rgba(255,255,255,0.03)", zeroline=False, showgrid=True)
def _yaxis(): return dict(gridcolor="rgba(255,255,255,0.03)", zeroline=False, showgrid=True, tickformat=",.2f")

def build_chart(df: pd.DataFrame, indicators: dict) -> go.Figure:
    """Full chart: price + optional indicators."""
    close = df["Close"].squeeze()
    n     = len(close)

    # Determine rows
    rows, heights = [1], [1.0]
    row_vol = row_rsi = None
    if st.session_state.show_vol and "Volume" in df.columns:
        rows.append(len(rows)+1)
        row_vol = rows[-1]
        heights.append(0.18)
    if st.session_state.show_rsi:
        rows.append(len(rows)+1)
        row_rsi = rows[-1]
        heights.append(0.18)

    # Normalise heights
    total = sum(heights)
    heights = [h/total for h in heights]

    fig = make_subplots(
        rows=len(rows), cols=1,
        shared_xaxes=True,
        row_heights=heights,
        vertical_spacing=0.018,
    )

    # ── Price trace ──
    ctype = st.session_state.chart_type
    if ctype == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"].squeeze(), high=df["High"].squeeze(),
            low=df["Low"].squeeze(),  close=close,
            name="Price",
            increasing=dict(line_color="#34d399", fillcolor="rgba(52,211,153,0.75)"),
            decreasing=dict(line_color="#f87171", fillcolor="rgba(248,113,113,0.75)"),
            line_width=1,
        ), row=1, col=1)
    elif ctype == "Line":
        fig.add_trace(go.Scatter(
            x=df.index, y=close,
            mode="lines", name="Close",
            line=dict(color="#5b8af0", width=2),
        ), row=1, col=1)
    else:  # Area
        fig.add_trace(go.Scatter(
            x=df.index, y=close,
            mode="lines", name="Close",
            line=dict(color="#5b8af0", width=2),
            fill="tozeroy",
            fillcolor="rgba(91,138,240,0.08)",
        ), row=1, col=1)

    # ── Moving Averages ──
    MA_CFG = [
        ("MA20",  st.session_state.show_ma20,  20,  "#5b8af0", "MA 20"),
        ("MA50",  st.session_state.show_ma50,  50,  "#a78bfa", "MA 50"),
        ("MA200", st.session_state.show_ma200, 200, "#fbbf24", "MA 200"),
    ]
    for key, visible, win, color, label in MA_CFG:
        if not visible or n < 5: continue
        if key in indicators and not indicators[key].isna().all():
            eff   = min(win, n)
            dname = label if eff == win else f"{label} ({eff}d)"
            fig.add_trace(go.Scatter(
                x=df.index, y=indicators[key],
                mode="lines", name=dname,
                line=dict(color=color, width=1.6),
                opacity=0.9,
            ), row=1, col=1)

    # ── Bollinger Bands ──
    if st.session_state.show_bb and n >= 5:
        for band_key, band_name, fill in [
            ("BB_upper", "BB Upper", False),
            ("BB_lower", "BB Lower", True),
        ]:
            if band_key in indicators:
                kw = dict(x=df.index, y=indicators[band_key], mode="lines",
                          name=band_name, line=dict(color="rgba(167,139,250,0.3)", width=1, dash="dot"),
                          showlegend=False)
                if fill:
                    kw["fill"]      = "tonexty"
                    kw["fillcolor"] = "rgba(167,139,250,0.04)"
                fig.add_trace(go.Scatter(**kw), row=1, col=1)

    # ── Volume ──
    if row_vol and "Volume" in df.columns:
        vol    = df["Volume"].squeeze()
        colors = ["#34d399" if (close.iloc[i] >= close.iloc[i-1] if i > 0 else True)
                  else "#f87171" for i in range(n)]
        fig.add_trace(go.Bar(
            x=df.index, y=vol, name="Volume",
            marker_color=colors, opacity=0.55, showlegend=False,
        ), row=row_vol, col=1)
        fig.update_yaxes(title_text="Vol", row=row_vol, col=1,
                         tickformat=".2s", **_yaxis())

    # ── RSI ──
    if row_rsi and "RSI" in indicators and not indicators["RSI"].isna().all():
        rsi = indicators["RSI"]
        fig.add_trace(go.Scatter(
            x=df.index, y=rsi,
            name="RSI", line=dict(color="#fbbf24", width=1.5), showlegend=False,
        ), row=row_rsi, col=1)
        # Overbought / oversold bands
        for level, color in [(70, "rgba(248,113,113,0.35)"), (30, "rgba(52,211,153,0.35)")]:
            fig.add_hline(y=level, line_dash="dot", line_color=color,
                          line_width=1, row=row_rsi, col=1)
        # RSI fill zones
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(248,113,113,0.05)",
                      line_width=0, row=row_rsi, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(52,211,153,0.05)",
                      line_width=0, row=row_rsi, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100],
                         row=row_rsi, col=1, **_yaxis())

    # ── Layout ──
    fig.update_layout(
        template="plotly_dark",
        height=600 + (row_vol is not None)*110 + (row_rsi is not None)*110,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
            bgcolor="rgba(5,8,16,0.7)", bordercolor="rgba(255,255,255,0.08)",
            borderwidth=1, font_size=11,
        ),
        **PLOT_DARK,
    )
    fig.update_xaxes(**_xaxis())
    fig.update_yaxes(row=1, col=1, **_yaxis())

    return fig


# ───────────────────────────────────────────────────────────────────
# SHARED HELPERS
# ───────────────────────────────────────────────────────────────────
def _hero(title: str, sub: str, eyebrow: str = ""):
    ey = f'<div class="sw-hero-eyebrow">{eyebrow}</div>' if eyebrow else ""
    st.markdown(f"""
    <div class="sw-hero">
        {ey}
        <div class="sw-hero-title">{title}</div>
        <div class="sw-hero-meta">{sub}</div>
    </div>""", unsafe_allow_html=True)

def _section(title: str):
    st.markdown(f"""
    <div class="sw-section">
        <span class="sw-section-title">{title}</span>
        <span class="sw-section-line"></span>
    </div>""", unsafe_allow_html=True)

def _get_info(key, default="N/A", fmt=None):
    val = info.get(key)
    if val is None: return default
    if fmt == "inr": return format_inr(val)
    if fmt == "pct":
        try: return f"{float(val)*100:.2f}%"
        except: return default
    if fmt == "x":
        try: return f"{float(val):.2f}×"
        except: return default
    if fmt == "f":
        try: return f"{float(val):.2f}"
        except: return default
    if fmt == "int":
        try: return f"{int(val):,}"
        except: return default
    return str(val)

def _metric_card(label, value, sub="", sub_cls="sw-muted"):
    return f"""
    <div class="sw-card">
        <div class="sw-card-label">{label}</div>
        <div class="sw-card-value">{value}</div>
        <div class="sw-card-sub {sub_cls}">{sub}</div>
    </div>"""

def _fund_block(heading, rows):
    inner = "".join(
        f'<div class="sw-fund-row"><span class="sw-fund-key">{k}</span>'
        f'<span class="sw-fund-val">{v}</span></div>'
        for k, v in rows
    )
    return f"""
    <div class="sw-fund-block">
        <div class="sw-fund-heading">{heading}</div>
        {inner}
    </div>"""


# ───────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ───────────────────────────────────────────────────────────────────
def page_dashboard():
    name   = info.get("longName") or info.get("shortName") or st.session_state.ticker
    exch   = info.get("exchange", "")
    sector = info.get("sector", "")
    cur    = info.get("currency", "INR")
    cur_s  = "₹" if cur == "INR" else "$"

    meta_parts = [
        f'<span class="sw-chip sw-chip-blue">{st.session_state.ticker}</span>',
        exch and f'<span class="sw-chip sw-chip-blue">{exch}</span>' or "",
        sector and f'<span class="sw-chip sw-chip-blue">{sector}</span>' or "",
    ]
    _hero(name, " ".join(filter(None, meta_parts)), eyebrow="Stock Overview")

    if not has_data:
        st.error("⚠️ No price data found. Check the ticker and try again.")
        return

    close      = df["Close"].squeeze()
    price      = float(close.iloc[-1])
    price_prev = float(close.iloc[-2]) if len(close) > 1 else price
    chg        = price - price_prev
    chg_pct    = chg / price_prev * 100 if price_prev else 0
    c_cls      = "sw-green" if chg >= 0 else "sw-red"
    c_sym      = "▲" if chg >= 0 else "▼"

    mktcap   = _get_info("marketCap", fmt="inr")
    pe       = _get_info("trailingPE", fmt="x")
    wk_hi    = _get_info("fiftyTwoWeekHigh", fmt="f") or f"{float(close.max()):.2f}"
    wk_lo    = _get_info("fiftyTwoWeekLow",  fmt="f") or f"{float(close.min()):.2f}"
    div_yld  = _get_info("dividendYield", fmt="pct")
    beta     = _get_info("beta", fmt="f")

    # Score: days above MA50
    score_html = ""
    n_pts = len(close)
    if "MA50" in indicators and n_pts:
        ma50 = indicators["MA50"].dropna()
        if len(ma50):
            ratio = (close[-len(ma50):] > ma50).mean()
            pct   = round(ratio * 100)
            c     = "sw-chip-green" if pct > 60 else "sw-chip-yellow" if pct > 40 else "sw-chip-red"
            score_html = f'&nbsp;<span class="sw-chip {c}">Above MA50: {pct}%</span>'

    cards_html = (
        _metric_card("Current Price", f"{cur_s}{price:,.2f}",
                     f'{c_sym} {abs(chg):.2f} ({abs(chg_pct):.2f}%)', c_cls) +
        _metric_card("Market Cap",    mktcap,       "Total cap",         "sw-muted") +
        _metric_card("P/E Ratio",     pe,           "Trailing",          "sw-muted") +
        _metric_card("52W High",      f"{cur_s}{wk_hi}", "Annual high",  "sw-green") +
        _metric_card("52W Low",       f"{cur_s}{wk_lo}", "Annual low",   "sw-red")   +
        _metric_card("Dividend Yield",div_yld,      "Annual",            "sw-muted") +
        _metric_card("Beta",          beta,         "Volatility vs mkt", "sw-muted")
    )
    st.markdown(f'<div class="sw-metric-grid">{cards_html}</div>', unsafe_allow_html=True)

    _section("📈 Price Chart")
    st.markdown('<div class="sw-chart-wrap">', unsafe_allow_html=True)
    fig = build_chart(df, indicators)
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
# PAGE: PRICE CHART
# ───────────────────────────────────────────────────────────────────
def page_chart():
    cur = info.get("currency", "INR")
    cur_s = "₹" if cur == "INR" else "$"

    _hero(
        f"Price Chart — {st.session_state.ticker}",
        f'<span class="sw-chip sw-chip-blue">{st.session_state.period.upper()}</span>'
        f'&nbsp; {st.session_state.chart_type}',
        eyebrow="Technical Analysis",
    )

    if not has_data:
        st.error("⚠️ No price data available.")
        return

    close = df["Close"].squeeze()
    n     = len(close)

    if n < 5:
        st.markdown(f"""
        <div class="sw-banner">
            ⚠️ Only <strong>{n} data point(s)</strong> available for
            <strong>{st.session_state.ticker}</strong>.
            Moving averages are automatically shortened to fit available history.
            Try selecting a longer period for full indicators.
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sw-chart-wrap">', unsafe_allow_html=True)
    fig = build_chart(df, indicators)
    st.plotly_chart(fig, width='stretch', config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["toImage", "sendDataToCloud", "select2d", "lasso2d"],
        "displaylogo": False,
    })
    st.markdown("</div>", unsafe_allow_html=True)

    # Data stats row
    price_now  = float(close.iloc[-1])
    price_open = float(df["Open"].squeeze().iloc[-1])
    price_hi   = float(df["High"].squeeze().iloc[-1])
    price_lo   = float(df["Low"].squeeze().iloc[-1])

    cards_html = (
        _metric_card("Open",    f"{cur_s}{price_open:,.2f}", df.index[-1].strftime("%d %b %Y"), "sw-muted") +
        _metric_card("High",    f"{cur_s}{price_hi:,.2f}",   "Day high",  "sw-green") +
        _metric_card("Low",     f"{cur_s}{price_lo:,.2f}",   "Day low",   "sw-red")   +
        _metric_card("Close",   f"{cur_s}{price_now:,.2f}",  "Last close","sw-muted") +
        _metric_card("Period",  f"{n} days", f"{df.index[0].strftime('%d %b %Y')} – {df.index[-1].strftime('%d %b %Y')}", "sw-muted")
    )
    st.markdown(f'<div class="sw-metric-grid">{cards_html}</div>', unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
# PAGE: FUNDAMENTALS
# ───────────────────────────────────────────────────────────────────
def page_fundamentals():
    name = info.get("longName") or st.session_state.ticker
    _hero(name, "Fundamental Analysis &amp; Financial Ratios", eyebrow="Fundamentals")

    if not info:
        st.error("Company data unavailable.")
        return

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(_fund_block("📊 Valuation Ratios", [
            ("P/E (Trailing)",  _get_info("trailingPE",                   fmt="x")),
            ("P/E (Forward)",   _get_info("forwardPE",                    fmt="x")),
            ("Price / Book",    _get_info("priceToBook",                  fmt="x")),
            ("Price / Sales",   _get_info("priceToSalesTrailing12Months", fmt="x")),
            ("EV / EBITDA",     _get_info("enterpriseToEbitda",           fmt="x")),
            ("PEG Ratio",       _get_info("pegRatio",                     fmt="f")),
            ("EV / Revenue",    _get_info("enterpriseToRevenue",          fmt="x")),
        ]), unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        st.markdown(_fund_block("💰 Dividends & Returns", [
            ("Dividend Yield",  _get_info("dividendYield",   fmt="pct")),
            ("Payout Ratio",    _get_info("payoutRatio",     fmt="pct")),
            ("Beta",            _get_info("beta",            fmt="f")),
            ("Short Ratio",     _get_info("shortRatio",      fmt="f")),
        ]), unsafe_allow_html=True)

    with col2:
        st.markdown(_fund_block("📈 Profitability", [
            ("Gross Margin",    _get_info("grossMargins",    fmt="pct")),
            ("EBITDA Margin",   _get_info("ebitdaMargins",   fmt="pct")),
            ("Operating Margin",_get_info("operatingMargins",fmt="pct")),
            ("Net Margin",      _get_info("profitMargins",   fmt="pct")),
            ("ROE",             _get_info("returnOnEquity",  fmt="pct")),
            ("ROA",             _get_info("returnOnAssets",  fmt="pct")),
        ]), unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        st.markdown(_fund_block("🏦 Balance Sheet (TTM)", [
            ("Revenue",         _get_info("totalRevenue",       fmt="inr")),
            ("Net Income",      _get_info("netIncomeToCommon",  fmt="inr")),
            ("EBITDA",          _get_info("ebitda",             fmt="inr")),
            ("Total Cash",      _get_info("totalCash",          fmt="inr")),
            ("Total Debt",      _get_info("totalDebt",          fmt="inr")),
            ("Free Cash Flow",  _get_info("freeCashflow",       fmt="inr")),
        ]), unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        st.markdown(_fund_block("📉 Growth", [
            ("Revenue Growth",  _get_info("revenueGrowth",    fmt="pct")),
            ("Earnings Growth", _get_info("earningsGrowth",   fmt="pct")),
            ("Shares Out.",     _get_info("sharesOutstanding", fmt="int")),
        ]), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
# PAGE: NEWS
# ───────────────────────────────────────────────────────────────────
def page_news():
    _hero("News Feed", f"Latest headlines for {st.session_state.ticker}", eyebrow="Market Intelligence")

    try:
        import yfinance as yf
        news = yf.Ticker(st.session_state.ticker).news or []
    except Exception:
        news = []

    if not news:
        st.markdown("""
        <div class="sw-banner">
            📭 No recent news headlines found for this ticker.
            Try a different symbol or check back later.
        </div>""", unsafe_allow_html=True)
        return

    for item in news[:20]:
        title  = item.get("title", "Untitled")
        link   = item.get("link",  "#")
        pub    = item.get("publisher", "Unknown")
        ts     = item.get("providerPublishTime", 0)
        ts_str = datetime.fromtimestamp(ts).strftime("%d %b %Y · %H:%M") if ts else ""

        st.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div class="sw-news-card">
                <div style="flex:1">
                    <div class="sw-news-title">{title}</div>
                    <div class="sw-news-meta">
                        <span class="sw-news-pub">{pub}</span>
                        <span class="sw-news-dot">·</span>
                        <span>{ts_str}</span>
                    </div>
                </div>
                <div style="color:#3d4f72;font-size:18px;align-self:center;">›</div>
            </div>
        </a>""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
# PAGE: SETTINGS
# ───────────────────────────────────────────────────────────────────
def page_settings():
    _hero("Settings", "App preferences and information", eyebrow="Configuration")

    st.markdown(_fund_block("ℹ️ About AccelWealth", [
        ("Version",    "2.0.0"),
        ("Data",       "Yahoo Finance (yfinance)"),
        ("Charts",     "Plotly"),
        ("Framework",  "Streamlit ≥ 1.32"),
        ("Author",     "AccelWealth Team"),
    ]), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    st.markdown(_fund_block("📋 Current Session", [
        ("Ticker",  st.session_state.ticker),
        ("Period",  st.session_state.period.upper()),
        ("Chart",   st.session_state.chart_type),
        ("MA 20",   "On" if st.session_state.show_ma20  else "Off"),
        ("MA 50",   "On" if st.session_state.show_ma50  else "Off"),
        ("MA 200",  "On" if st.session_state.show_ma200 else "Off"),
    ]), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
# ROUTER
# ───────────────────────────────────────────────────────────────────
{
    "Dashboard":    page_dashboard,
    "Price Chart":  page_chart,
    "Fundamentals": page_fundamentals,
    "News":         page_news,
    "Settings":     page_settings,
}.get(st.session_state.page, page_dashboard)()
