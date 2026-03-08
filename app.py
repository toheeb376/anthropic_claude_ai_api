# =============================================================================
# Claude API Usage Intelligence Dashboard
# Anthropic Claude Brand Theme — Streamlit + Plotly
# =============================================================================
# SETUP INSTRUCTIONS:
#   1. Install dependencies:  pip install streamlit pandas plotly openpyxl
#   2. Place these files in the SAME folder:
#        - app.py
#        - anthropic_claude_ai_api_dataset.xlsx
#        - anthropic_claude_ai_api.jpg
#   3. Run the app:  streamlit run app.py
#   4. Your browser will open automatically at http://localhost:8501
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import base64
from datetime import datetime

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION — Must be the FIRST Streamlit command
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Claude API Intelligence Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ANTHROPIC CLAUDE BRAND COLOR PALETTE
# RGB tuples and hex strings for consistent usage across Plotly & CSS
# -----------------------------------------------------------------------------
COLORS = {
    "cream":      "#F2EFE6",   # App / chart background
    "charcoal":   "#1C1917",   # Sidebar, cards, primary text
    "terracotta": "#CD5C49",   # Primary accent — borders, highlights
    "warm_gray":  "#78746E",   # Secondary labels, axis ticks, dividers
    # Supporting chart accent colors
    "steel":      "#4A90D9",
    "sage":       "#5FAD8E",
    "amber":      "#E8A838",
    "slate":      "#BDC3C7",
}

# Ordered color sequence for multi-series charts
CHART_COLORS = [
    COLORS["terracotta"],
    COLORS["steel"],
    COLORS["sage"],
    COLORS["amber"],
    COLORS["slate"],
    "#9B59B6",
    "#E74C3C",
    "#1ABC9C",
]

# -----------------------------------------------------------------------------
# CUSTOM CSS — Enforces Claude brand theme across all Streamlit elements
# -----------------------------------------------------------------------------
st.markdown(f"""
<style>
    /* ── App background ── */
    .stApp {{
        background-color: {COLORS['cream']};
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}

    /* ── Main content area ── */
    .main .block-container {{
        background-color: {COLORS['cream']};
        padding-top: 1rem;
        padding-bottom: 2rem;
    }}

    /* ── Sidebar background ── */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['charcoal']};
    }}
    section[data-testid="stSidebar"] * {{
        color: {COLORS['cream']} !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label,
    section[data-testid="stSidebar"] .stSlider label {{
        color: {COLORS['cream']} !important;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* ── Sidebar input controls ── */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stMultiSelect > div > div {{
        background-color: #2C2927 !important;
        border: 1px solid {COLORS['warm_gray']} !important;
        color: {COLORS['cream']} !important;
        border-radius: 6px;
    }}

    /* ── KPI Metric cards ── */
    [data-testid="metric-container"] {{
        background-color: {COLORS['charcoal']};
        border: 1px solid {COLORS['terracotta']};
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }}
    [data-testid="metric-container"] > div {{
        color: {COLORS['cream']} !important;
    }}
    [data-testid="metric-container"] label {{
        color: {COLORS['warm_gray']} !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }}
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: {COLORS['cream']} !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }}
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {{
        color: {COLORS['sage']} !important;
    }}

    /* ── Section headings ── */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['charcoal']} !important;
        font-weight: 700;
    }}
    h1 {{ font-size: 1.9rem !important; }}
    h2 {{ font-size: 1.4rem !important; border-bottom: 2px solid {COLORS['terracotta']}; padding-bottom: 6px; }}
    h3 {{ font-size: 1.15rem !important; }}

    /* ── Paragraph and regular text ── */
    p, span, div {{
        color: {COLORS['charcoal']};
    }}

    /* ── Expander (Executive Summary) ── */
    .streamlit-expanderHeader {{
        background-color: {COLORS['charcoal']} !important;
        color: {COLORS['cream']} !important;
        border: 1px solid {COLORS['terracotta']} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }}
    .streamlit-expanderContent {{
        background-color: #F7F5EF !important;
        border: 1px solid {COLORS['warm_gray']} !important;
        border-radius: 0 0 8px 8px !important;
        padding: 20px !important;
    }}

    /* ── Divider styling ── */
    hr {{
        border-color: {COLORS['warm_gray']} !important;
        opacity: 0.4;
    }}

    /* ── Dataframe / table styling ── */
    .stDataFrame {{
        border: 1px solid {COLORS['warm_gray']};
        border-radius: 8px;
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {COLORS['cream']}; }}
    ::-webkit-scrollbar-thumb {{ background: {COLORS['warm_gray']}; border-radius: 3px; }}

    /* ── Section card wrapper ── */
    .chart-card {{
        background-color: white;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 16px;
    }}

    /* ── KPI row label override ── */
    .kpi-label {{
        color: {COLORS['warm_gray']};
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }}

    /* ── Hide Streamlit default menu & footer ── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PLOTLY BASE LAYOUT — Reusable Claude theme settings for all charts
# -----------------------------------------------------------------------------
def claude_chart_layout(title="", height=380, showlegend=True):
    """Returns a dict of Plotly layout kwargs applying the Claude brand theme."""
    return dict(
        title=dict(text=title, font=dict(color=COLORS["charcoal"], size=15, family="Inter, Segoe UI, sans-serif")),
        plot_bgcolor=COLORS["cream"],
        paper_bgcolor=COLORS["cream"],
        font=dict(color=COLORS["charcoal"], family="Inter, Segoe UI, sans-serif", size=12),
        height=height,
        showlegend=showlegend,
        legend=dict(
            font=dict(color=COLORS["charcoal"], size=11),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=COLORS["warm_gray"],
            borderwidth=0.5
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(
            bgcolor=COLORS["charcoal"],
            font_color=COLORS["cream"],
            font_size=12,
            bordercolor=COLORS["terracotta"]
        ),
        xaxis=dict(
            gridcolor="rgba(120,116,110,0.15)",
            linecolor=COLORS["warm_gray"],
            tickfont=dict(color=COLORS["warm_gray"], size=11),
            title_font=dict(color=COLORS["charcoal"])
        ),
        yaxis=dict(
            gridcolor="rgba(120,116,110,0.15)",
            linecolor=COLORS["warm_gray"],
            tickfont=dict(color=COLORS["warm_gray"], size=11),
            title_font=dict(color=COLORS["charcoal"])
        ),
    )


# -----------------------------------------------------------------------------
# DATA LOADING & PREPROCESSING — Cached for performance
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads the Excel dataset, cleans it, and engineers derived features.
    Uses @st.cache_data so it only runs once per session.
    """
    df = pd.read_excel(filepath)

    # ── Strip whitespace from all string columns ──
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # ── Convert Request Timestamp to datetime (safe coercion) ──
    df["Request Timestamp"] = pd.to_datetime(df["Request Timestamp"], errors="coerce")

    # ── Drop rows where timestamp is completely invalid ──
    df = df.dropna(subset=["Request Timestamp"])

    # ── Extract date-only column for time grouping ──
    df["Request Date"] = df["Request Timestamp"].dt.date

    # ── Token Efficiency Ratio = Completion Tokens / Prompt Tokens ──
    df["Token Efficiency Ratio"] = df.apply(
        lambda r: round(r["Completion Tokens"] / r["Prompt Tokens"], 4)
        if r["Prompt Tokens"] > 0 else 0.0, axis=1
    )

    # ── Cost per 1K Tokens = (Cost / Total Tokens) × 1000 ──
    df["Cost per 1K Tokens"] = df.apply(
        lambda r: round((r["Cost (USD)"] / r["Total Tokens"]) * 1000, 6)
        if r["Total Tokens"] > 0 else 0.0, axis=1
    )

    # ── Latency Tier classification ──
    def latency_tier(ms):
        if pd.isna(ms):     return "Unknown"
        if ms < 500:        return "Fast"
        if ms <= 1500:      return "Moderate"
        return "Slow"

    df["Latency Tier"] = df["Latency (ms)"].apply(latency_tier)

    # ── Boolean safety flag ──
    df["Safety Flag Bool"] = df["Safety Flag Triggered"].str.upper() == "YES"

    return df


# -----------------------------------------------------------------------------
# SIDEBAR — Logo, Filters, Branding
# -----------------------------------------------------------------------------
def render_sidebar(df: pd.DataFrame):
    """Renders sidebar logo, title, and all filter widgets. Returns filtered df."""

    with st.sidebar:

        # ── Logo ──
        logo_path = "anthropic_claude_ai_api.jpg"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f'<div style="text-align:center; padding: 12px 0 8px 0;">'
                f'<img src="data:image/jpeg;base64,{img_b64}" '
                f'style="width:160px; border-radius:10px; border:2px solid {COLORS["terracotta"]};" />'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="text-align:center; padding:20px 0; font-size:2rem;"></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div style="text-align:center; font-size:0.78rem; color:{COLORS["warm_gray"]}; '
            f'letter-spacing:0.12em; text-transform:uppercase; padding-bottom:12px;">'
            f'API Intelligence Dashboard</div>',
            unsafe_allow_html=True
        )
        st.markdown(f'<hr style="border-color:{COLORS["warm_gray"]}; opacity:0.3; margin:0 0 16px 0;">', unsafe_allow_html=True)

        # ── Filter: API Tier ──
        all_tiers = sorted(df["API Tier"].dropna().unique().tolist())
        sel_tier = st.multiselect("API Tier", all_tiers, default=all_tiers, key="tier")

        # ── Filter: Use Case ──
        all_usecases = sorted(df["Use Case"].dropna().unique().tolist())
        sel_usecase = st.multiselect("Use Case", all_usecases, default=all_usecases, key="usecase")

        # ── Filter: Region ──
        all_regions = sorted(df["Region"].dropna().unique().tolist())
        sel_region = st.multiselect("Region", all_regions, default=all_regions, key="region")

        # ── Filter: Response Status ──
        all_status = sorted(df["Response Status"].dropna().unique().tolist())
        sel_status = st.multiselect("Response Status", all_status, default=all_status, key="status")

        # ── Filter: Safety Flag ──
        all_flags = sorted(df["Safety Flag Triggered"].dropna().unique().tolist())
        sel_flag = st.multiselect("Safety Flag Triggered", all_flags, default=all_flags, key="flag")

        # ── Filter: Latency Tier ──
        all_lat_tiers = ["Fast", "Moderate", "Slow"]
        sel_lat_tier = st.multiselect("Latency Tier", all_lat_tiers, default=all_lat_tiers, key="lattier")

        # ── Filter: Date Range ──
        min_date = df["Request Timestamp"].min().date()
        max_date = df["Request Timestamp"].max().date()
        date_range = st.date_input(
            "Request Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="daterange"
        )

        st.markdown(f'<hr style="border-color:{COLORS["warm_gray"]}; opacity:0.3; margin:12px 0;">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.7rem; color:{COLORS["warm_gray"]}; text-align:center;">'
            f'Powered by Anthropic Claude API<br>© 2025 Claude Intelligence</div>',
            unsafe_allow_html=True
        )

    # ── Apply all filters to dataframe ──
    filtered = df.copy()
    if sel_tier:
        filtered = filtered[filtered["API Tier"].isin(sel_tier)]
    if sel_usecase:
        filtered = filtered[filtered["Use Case"].isin(sel_usecase)]
    if sel_region:
        filtered = filtered[filtered["Region"].isin(sel_region)]
    if sel_status:
        filtered = filtered[filtered["Response Status"].isin(sel_status)]
    if sel_flag:
        filtered = filtered[filtered["Safety Flag Triggered"].isin(sel_flag)]
    if sel_lat_tier:
        filtered = filtered[filtered["Latency Tier"].isin(sel_lat_tier)]

    # Date range filter — handle both tuple and single date
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            (filtered["Request Timestamp"].dt.date >= start_date) &
            (filtered["Request Timestamp"].dt.date <= end_date)
        ]

    return filtered


# -----------------------------------------------------------------------------
# KPI CARDS
# -----------------------------------------------------------------------------
def render_kpis(df: pd.DataFrame):
    """Computes and renders the 8 KPI metric cards."""

    total_requests    = len(df)
    total_tokens      = df["Total Tokens"].sum()
    total_cost        = df["Cost (USD)"].sum()
    avg_latency       = df["Latency (ms)"].mean()

    # Success Rate — guard against empty df
    success_rate = (
        (df["Response Status"].str.lower() == "success").sum() / total_requests * 100
        if total_requests > 0 else 0.0
    )

    # Safety Flag Rate
    flag_rate = (
        df["Safety Flag Bool"].sum() / total_requests * 100
        if total_requests > 0 else 0.0
    )

    # Avg Cost per 1K Tokens
    avg_cost_1k = df["Cost per 1K Tokens"].mean() if total_requests > 0 else 0.0

    # Avg Token Efficiency Ratio
    avg_efficiency = df["Token Efficiency Ratio"].mean() if total_requests > 0 else 0.0

    # Render in 8 columns
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

    with c1:
        st.metric("Total Requests",   f"{total_requests:,}")
    with c2:
        st.metric("Total Tokens",     f"{total_tokens:,.0f}")
    with c3:
        st.metric("Total Cost (USD)", f"${total_cost:,.4f}")
    with c4:
        st.metric("Avg Latency (ms)", f"{avg_latency:,.1f}" if total_requests > 0 else "—")
    with c5:
        st.metric("Success Rate",     f"{success_rate:.1f}%")
    with c6:
        st.metric("Safety Flag Rate", f"{flag_rate:.1f}%")
    with c7:
        st.metric("Avg Cost/1K Tok",  f"${avg_cost_1k:.4f}")
    with c8:
        st.metric("Avg Efficiency",   f"{avg_efficiency:.3f}")


# -----------------------------------------------------------------------------
# CHART BUILDERS — Each returns a Plotly Figure
# -----------------------------------------------------------------------------

def chart_response_status(df):
    """Bar chart: Response Status distribution."""
    counts = df["Response Status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    fig = px.bar(
        counts, x="Status", y="Count",
        color="Status",
        color_discrete_map={"Success": COLORS["sage"], "Error": COLORS["terracotta"]},
        text="Count"
    )
    fig.update_traces(textposition="outside", textfont_color=COLORS["charcoal"])
    fig.update_layout(**claude_chart_layout("Response Status Distribution", height=360, showlegend=False))
    return fig


def chart_tokens_by_region(df):
    """Grouped bar: Prompt vs Completion Tokens by Region."""
    grp = df.groupby("Region")[["Prompt Tokens", "Completion Tokens"]].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Prompt Tokens", x=grp["Region"], y=grp["Prompt Tokens"],
        marker_color=COLORS["terracotta"],
        hovertemplate="<b>%{x}</b><br>Avg Prompt Tokens: %{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Completion Tokens", x=grp["Region"], y=grp["Completion Tokens"],
        marker_color=COLORS["steel"],
        hovertemplate="<b>%{x}</b><br>Avg Completion Tokens: %{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(**claude_chart_layout("Avg Token Usage by Region", height=360), barmode="group")
    return fig


def chart_requests_over_time(df):
    """Line chart: API Requests over time."""
    daily = df.groupby("Request Date").size().reset_index(name="Requests")
    daily["Request Date"] = pd.to_datetime(daily["Request Date"])
    fig = px.line(
        daily, x="Request Date", y="Requests",
        markers=True,
        color_discrete_sequence=[COLORS["terracotta"]]
    )
    fig.update_traces(
        line_width=2.5,
        marker=dict(size=6, color=COLORS["terracotta"], line=dict(color=COLORS["charcoal"], width=1))
    )
    fig.update_layout(**claude_chart_layout("API Requests Over Time", height=340))
    return fig


def chart_cost_by_tier(df):
    """Donut chart: Cost distribution by API Tier."""
    tier_cost = df.groupby("API Tier")["Cost (USD)"].sum().reset_index()
    fig = px.pie(
        tier_cost, names="API Tier", values="Cost (USD)",
        hole=0.52,
        color_discrete_sequence=CHART_COLORS
    )
    fig.update_traces(
        textfont_color=COLORS["charcoal"],
        hovertemplate="<b>%{label}</b><br>Cost: $%{value:,.4f}<br>Share: %{percent}<extra></extra>"
    )
    fig.update_layout(**claude_chart_layout("Cost Distribution by API Tier", height=360))
    return fig


def chart_top_usecases(df):
    """Horizontal bar: Top 10 Use Cases by Total Tokens."""
    uc = df.groupby("Use Case")["Total Tokens"].sum().nlargest(10).reset_index()
    uc = uc.sort_values("Total Tokens", ascending=True)
    fig = px.bar(
        uc, y="Use Case", x="Total Tokens",
        orientation="h",
        text="Total Tokens",
        color="Total Tokens",
        color_continuous_scale=[[0, COLORS["amber"]], [1, COLORS["terracotta"]]]
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont_color=COLORS["charcoal"]
    )
    fig.update_layout(**claude_chart_layout("Top 10 Use Cases by Total Tokens", height=380, showlegend=False))
    fig.update_coloraxes(showscale=False)
    return fig


def chart_safety_flag_by_region(df):
    """Bar chart: Safety Flag Rate (%) by Region."""
    grp = df.groupby("Region").agg(
        Total=("Safety Flag Bool", "count"),
        Flagged=("Safety Flag Bool", "sum")
    ).reset_index()
    grp["Flag Rate (%)"] = (grp["Flagged"] / grp["Total"] * 100).round(2)
    fig = px.bar(
        grp, x="Region", y="Flag Rate (%)",
        color="Flag Rate (%)",
        text="Flag Rate (%)",
        color_continuous_scale=[[0, COLORS["sage"]], [0.5, COLORS["amber"]], [1, COLORS["terracotta"]]]
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        textfont_color=COLORS["charcoal"]
    )
    fig.update_layout(**claude_chart_layout("Safety Flag Rate by Region (%)", height=360, showlegend=False))
    fig.update_coloraxes(showscale=False)
    return fig


def chart_latency_histogram(df):
    """Histogram: Latency distribution."""
    fig = px.histogram(
        df, x="Latency (ms)",
        nbins=40,
        color_discrete_sequence=[COLORS["terracotta"]]
    )
    # Add vertical lines for tier boundaries
    fig.add_vline(x=500,  line_dash="dash", line_color=COLORS["steel"],     annotation_text="Fast/Mod", annotation_font_color=COLORS["steel"])
    fig.add_vline(x=1500, line_dash="dash", line_color=COLORS["warm_gray"], annotation_text="Mod/Slow", annotation_font_color=COLORS["warm_gray"])
    fig.update_layout(**claude_chart_layout("Latency Distribution (ms)", height=360))
    return fig


def chart_cost_vs_latency(df):
    """Scatter plot: Cost vs Latency by Use Case."""
    fig = px.scatter(
        df, x="Latency (ms)", y="Cost (USD)",
        color="Use Case",
        size="Total Tokens",
        size_max=18,
        opacity=0.72,
        color_discrete_sequence=CHART_COLORS,
        hover_data=["API Tier", "Region", "Response Status"]
    )
    fig.update_layout(**claude_chart_layout("Cost vs Latency by Use Case", height=400))
    return fig


def chart_token_efficiency_by_tier(df):
    """Bar chart: Avg Token Efficiency Ratio by API Tier."""
    grp = df.groupby("API Tier")["Token Efficiency Ratio"].mean().reset_index()
    fig = px.bar(
        grp, x="API Tier", y="Token Efficiency Ratio",
        color="API Tier",
        text="Token Efficiency Ratio",
        color_discrete_sequence=CHART_COLORS
    )
    fig.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside",
        textfont_color=COLORS["charcoal"]
    )
    fig.update_layout(**claude_chart_layout("Token Efficiency Ratio by API Tier", height=360, showlegend=False))
    return fig


def chart_3d_scatter(df):
    """
    Advanced 3D Intelligence Scatter:
    X = Request Timestamp (ordinal numeric)
    Y = Total Tokens
    Z = Cost (USD)
    Color = Response Status
    """
    plot_df = df.dropna(subset=["Request Timestamp", "Total Tokens", "Cost (USD)"]).copy()
    # Convert datetime to numeric ordinal (seconds since epoch)
    plot_df["Timestamp Ordinal"] = plot_df["Request Timestamp"].astype("int64") // 10**9

    color_map = {"Success": COLORS["sage"], "Error": COLORS["terracotta"]}

    fig = px.scatter_3d(
        plot_df,
        x="Timestamp Ordinal",
        y="Total Tokens",
        z="Cost (USD)",
        color="Response Status",
        color_discrete_map=color_map,
        opacity=0.75,
        hover_data=["Use Case", "Region", "API Tier", "Latency (ms)"],
        size_max=8,
    )
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(
        title=dict(
            text="3D API Intelligence Scatter — Timestamp × Tokens × Cost",
            font=dict(color=COLORS["charcoal"], size=14)
        ),
        scene=dict(
            xaxis=dict(
                title="Timestamp (ordinal)",
                backgroundcolor=COLORS["cream"],
                gridcolor=COLORS["warm_gray"],
                showbackground=True,
                tickfont=dict(color=COLORS["warm_gray"], size=9),
                title_font=dict(color=COLORS["charcoal"])
            ),
            yaxis=dict(
                title="Total Tokens",
                backgroundcolor=COLORS["cream"],
                gridcolor=COLORS["warm_gray"],
                showbackground=True,
                tickfont=dict(color=COLORS["warm_gray"], size=9),
                title_font=dict(color=COLORS["charcoal"])
            ),
            zaxis=dict(
                title="Cost (USD)",
                backgroundcolor=COLORS["cream"],
                gridcolor=COLORS["warm_gray"],
                showbackground=True,
                tickfont=dict(color=COLORS["warm_gray"], size=9),
                title_font=dict(color=COLORS["charcoal"])
            ),
            bgcolor=COLORS["cream"]
        ),
        paper_bgcolor=COLORS["cream"],
        height=550,
        margin=dict(l=0, r=0, t=50, b=0),
        legend=dict(font=dict(color=COLORS["charcoal"])),
        hoverlabel=dict(bgcolor=COLORS["charcoal"], font_color=COLORS["cream"], font_size=11)
    )
    return fig


# -----------------------------------------------------------------------------
# EXECUTIVE INSIGHT PANEL
# -----------------------------------------------------------------------------
def render_executive_insights(df):
    """Collapsible executive summary with actionable AI/API insights."""

    with st.expander(" Executive Insight Summary — Click to Expand", expanded=False):

        total = len(df)
        flag_rate   = df["Safety Flag Bool"].sum() / total * 100 if total > 0 else 0
        success_rt  = (df["Response Status"].str.lower() == "success").sum() / total * 100 if total > 0 else 0
        avg_eff     = df["Token Efficiency Ratio"].mean()
        avg_c1k     = df["Cost per 1K Tokens"].mean()
        slow_pct    = (df["Latency Tier"] == "Slow").sum() / total * 100 if total > 0 else 0
        fast_pct    = (df["Latency Tier"] == "Fast").sum() / total * 100 if total > 0 else 0

        st.markdown(f"""
###  Token Efficiency & Prompt Engineering
The **average Token Efficiency Ratio** across the selected dataset is **{avg_eff:.3f}**, meaning the model
generates approximately **{avg_eff:.2f} completion tokens per prompt token**. Ratios below 1.0 suggest that
outputs are shorter than inputs — potentially indicating overly long prompts or system instructions that could
be compressed. Engineering teams should audit prompts where the ratio consistently falls below 0.5, as this
represents cost inefficiency in prompt design. A ratio above 2.0 signals high generative output, common in
code generation and document summarisation use cases.

---

###  Latency Patterns by Region & Use Case
Currently, **{fast_pct:.1f}% of requests** are in the *Fast* tier (<500ms) and **{slow_pct:.1f}%** fall into
the *Slow* tier (>1500ms). Latency spikes are often correlated with specific use cases such as
**Legal Document Review** and **Financial Report Summarisation**, which process larger token volumes.
Product teams should consider implementing asynchronous request patterns or streaming responses for high-latency
use cases. Regional latency outliers should trigger infrastructure review with the platform team.

---

###  Safety Flag Analysis
The current **Safety Flag Rate is {flag_rate:.1f}%** of total requests. A rate above 10% warrants immediate
review of the content flowing through the API — particularly in use cases like **Content Moderation** and
**Marketing Content Generation**. High flag rates in specific regions may indicate content policy misalignment
with regional regulatory requirements. The product safety team should correlate flagged requests with
specific Client Companies and Use Cases to prioritize guardrail refinements.

---

###  Cost Optimisation via API Tier
At an average of **${avg_c1k:.5f} per 1,000 tokens**, cost scaling is directly tied to token volumes and
API tier selection. Enterprise tier users typically log longer prompts and higher completion volumes.
Teams should evaluate whether **Startup-tier workloads** using short, repetitive prompts could migrate to
batch processing to reduce per-request overhead. Monthly cost forecasting should be benchmarked against
the rolling 7-day average cost trend visible in the requests-over-time chart.

---

###  Current System Health
- **Success Rate:** {success_rt:.1f}% — {'🟢 Healthy' if success_rt >= 95 else '🟡 Monitor' if success_rt >= 85 else '🔴 Critical — investigate error patterns immediately'}
- **Safety Flag Rate:** {flag_rate:.1f}% — {'🟢 Normal' if flag_rate < 5 else '🟡 Elevated — audit flagged use cases' if flag_rate < 15 else '🔴 High — immediate content review required'}
- **Slow Latency Rate:** {slow_pct:.1f}% — {'🟢 Acceptable' if slow_pct < 10 else '🟡 Investigate heavy use cases' if slow_pct < 25 else '🔴 Significant degradation — check infrastructure'}

---

###  Daily Actions for Engineering & Product Teams
1. **Engineering:** Filter to *Error* response status and identify which Use Cases and Regions have elevated error rates.
2. **Product:** Use the Cost vs Latency scatter to identify high-cost, high-latency use cases for optimisation.
3. **Safety:** Review the Safety Flag Rate by Region chart daily — flag spikes may indicate new content risks.
4. **Finance:** Track Total Cost and Avg Cost/1K Tokens against monthly budget using the date range filter.
5. **Infrastructure:** Use the 3D Intelligence Scatter to identify temporal clusters of slow or expensive requests.
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# MAIN DASHBOARD RENDERER
# -----------------------------------------------------------------------------
def main():

    # ── Load data ──
    data_path = "anthropic_claude_ai_api_dataset.xlsx"
    if not os.path.exists(data_path):
        st.error(
            f"❌ Dataset not found: `{data_path}`\n\n"
            "Please place `anthropic_claude_ai_api_dataset.xlsx` in the same folder as `app.py`."
        )
        st.stop()

    df_raw = load_data(data_path)

    # ── Sidebar filters — returns filtered df ──
    df = render_sidebar(df_raw)

    # ── Dashboard Header ──
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">'
        f'<span style="font-size:2.2rem; color:{COLORS["terracotta"]};">✦</span>'
        f'<h1 style="margin:0; font-size:1.9rem; color:{COLORS["charcoal"]}; font-weight:800; letter-spacing:-0.02em;">'
        f'Claude API Usage Intelligence Dashboard</h1></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p style="color:{COLORS["warm_gray"]}; font-size:0.88rem; margin:0 0 20px 48px;">'
        f'Real-time monitoring · {len(df):,} requests shown of {len(df_raw):,} total · '
        f'Data range: {df_raw["Request Timestamp"].min().strftime("%b %d, %Y")} — '
        f'{df_raw["Request Timestamp"].max().strftime("%b %d, %Y")}</p>',
        unsafe_allow_html=True
    )

    # ── KPI Cards ──
    st.markdown("---")
    render_kpis(df)
    st.markdown("---")

    # ── Guard: empty data after filters ──
    if df.empty:
        st.warning("⚠️ No data matches the current filter selection. Please adjust the sidebar filters.")
        return

    # ================================================================
    # ROW 1: Response Status + Token Usage by Region + Requests Over Time
    # ================================================================
    st.markdown("##  Traffic & Token Intelligence")
    col1, col2, col3 = st.columns([1, 1.5, 2])
    with col1:
        st.plotly_chart(chart_response_status(df), use_container_width=True)
    with col2:
        st.plotly_chart(chart_tokens_by_region(df), use_container_width=True)
    with col3:
        st.plotly_chart(chart_requests_over_time(df), use_container_width=True)

    # ================================================================
    # ROW 2: Cost by Tier + Top Use Cases + Safety Flag by Region
    # ================================================================
    st.markdown("##  Cost & Safety Analytics")
    col4, col5, col6 = st.columns([1, 1.5, 1.2])
    with col4:
        st.plotly_chart(chart_cost_by_tier(df), use_container_width=True)
    with col5:
        st.plotly_chart(chart_top_usecases(df), use_container_width=True)
    with col6:
        st.plotly_chart(chart_safety_flag_by_region(df), use_container_width=True)

    # ================================================================
    # ROW 3: Latency Distribution + Cost vs Latency + Efficiency by Tier
    # ================================================================
    st.markdown("##  Performance & Efficiency")
    col7, col8, col9 = st.columns([1.2, 1.8, 1])
    with col7:
        st.plotly_chart(chart_latency_histogram(df), use_container_width=True)
    with col8:
        st.plotly_chart(chart_cost_vs_latency(df), use_container_width=True)
    with col9:
        st.plotly_chart(chart_token_efficiency_by_tier(df), use_container_width=True)

    # ================================================================
    # ROW 4: Advanced 3D Intelligence Scatter (full width)
    # ================================================================
    st.markdown("##  3D API Intelligence Scatter")
    st.plotly_chart(chart_3d_scatter(df), use_container_width=True)
    st.caption(
        "Rotate · Zoom · Hover to explore. "
        "X = Request Timestamp (ordinal) · Y = Total Tokens · Z = Cost (USD) · Color = Response Status"
    )

    # ================================================================
    # ROW 5: Executive Insights (collapsible)
    # ================================================================
    st.markdown("---")
    render_executive_insights(df)

    # ================================================================
    # ROW 6: Raw Data Preview (optional, collapsible)
    # ================================================================
    with st.expander(" Raw Data Preview (filtered)", expanded=False):
        display_cols = [
            "Request ID", "Client Company", "API Tier", "Use Case", "Region",
            "Request Timestamp", "Total Tokens", "Latency (ms)", "Cost (USD)",
            "Response Status", "Safety Flag Triggered", "Token Efficiency Ratio",
            "Cost per 1K Tokens", "Latency Tier"
        ]
        st.dataframe(
            df[display_cols].reset_index(drop=True),
            use_container_width=True,
            height=320
        )
        st.caption(f"Showing {len(df):,} rows × {len(display_cols)} columns")


# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()