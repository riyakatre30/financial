import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# PAGE
# =========================================================
st.set_page_config(
    page_title="Financial Performance Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# DARK ANALYTICS UI — INSPIRED BY THE SHARED IPL DASHBOARD
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0d1016;
    color: #e8edf0;
}

.block-container {
    max-width: 1500px;
    padding: 22px 38px 35px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #11151d;
    border-right: 1px solid #272d38;
}

[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #dce3e7 !important;
}

[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: #1b202a;
    border: 1px solid #343b48;
}

/* Header */
.dashboard-title {
    font-size: 34px;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -1px;
    color: #f2f5f6;
    margin-bottom: 4px;
}

.dashboard-subtitle {
    font-size: 11px;
    color: #87919c;
    margin-bottom: 16px;
}

.top-line {
    height: 1px;
    background: #2b313c;
    margin: 0 0 12px 0;
}

/* Navigation */
div[role="radiogroup"] {
    gap: 24px;
}

div[role="radiogroup"] label {
    color: #8f99a4 !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    padding-bottom: 7px;
    border-bottom: 2px solid transparent;
}

div[role="radiogroup"] label:has(input:checked) {
    color: #ffffff !important;
    border-bottom-color: #e34b58;
}

/* KPI cards */
.kpi {
    background: #141922;
    border: 1px solid #272e3a;
    border-radius: 6px;
    padding: 12px 15px;
    min-height: 74px;
}

.kpi-label {
    color: #7f8995;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .7px;
    font-weight: 600;
}

.kpi-value {
    color: #edf1f2;
    font-size: 21px;
    font-weight: 700;
    margin-top: 5px;
}

.kpi-note {
    color: #66717d;
    font-size: 9px;
    margin-top: 2px;
}

/* Chart headings */
.chart-title {
    color: #dce2e6;
    font-size: 12px;
    font-weight: 600;
    margin: 6px 0 1px 1px;
}

.chart-note {
    color: #68727e;
    font-size: 9px;
    margin: 0 0 1px 1px;
}

.insight {
    color: #7f8994;
    font-size: 10px;
    border-top: 1px solid #272e39;
    padding-top: 7px;
    margin-top: 2px;
}

.section-gap {
    height: 18px;
}

.stPlotlyChart {
    margin: 0 !important;
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA
# =========================================================
@st.cache_data
def load_data():
    return pd.read_excel("Credir_Card_Bank.xlsx")

df = load_data()

required = [
    "Customer_ID", "Monthly_Income", "Annual_Income",
    "Savings_Balance", "Investment_Value", "EMI_Per_Month",
    "Debt_To_Income_Ratio", "Credit_Utilization",
    "Existing_Credit_Limit", "Loan_Count", "Credit_Score"
]

missing = [c for c in required if c not in df.columns]
if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.stop()

for col in required:
    if col != "Customer_ID":
        df[col] = pd.to_numeric(df[col], errors="coerce")

df["Savings_Percentage"] = (
    df["Savings_Balance"] /
    df["Monthly_Income"].replace(0, np.nan)
) * 100

df["Investment_Percentage"] = (
    df["Investment_Value"] /
    df["Monthly_Income"].replace(0, np.nan)
) * 100


# =========================================================
# FILTERS
# =========================================================

st.sidebar.markdown(
    """
    <div style="
        font-family: 'DM Sans', sans-serif;
        font-size:18px;
        font-weight:600;
        color:#eef3f5;
        margin-bottom:4px;
    ">
        Financial Filters
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.caption(
    "Filter the customer portfolio to explore financial behaviour."
)


# ==================================================
# MULTISELECT UI FIX
# ==================================================

st.sidebar.markdown(
    """
    <style>

    /* ----------------------------------------------
       IMPORTANT:
       Do NOT use [class*="css"] here.
       It breaks Streamlit internal icons.
    ---------------------------------------------- */

    /* Keep Streamlit icons as icons */
    .material-icons,
    .material-symbols-rounded,
    .material-symbols-outlined,
    [data-testid="stIconMaterial"] {
        font-family:
            "Material Symbols Rounded",
            "Material Symbols Outlined",
            "Material Icons" !important;

        font-weight: normal !important;
        font-style: normal !important;
        font-size: 20px !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        direction: ltr !important;
    }


    /* ----------------------------------------------
       HIDE SELECTED RED CHIPS
       Female / Male / Salaried etc.
       will NOT be displayed in the closed box.
    ---------------------------------------------- */

    section[data-testid="stSidebar"]
    div[data-baseweb="select"]
    [data-baseweb="tag"] {
        display: none !important;
    }


    /* ----------------------------------------------
       CLEAN MULTISELECT BOX
    ---------------------------------------------- */

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] {
        min-height: 42px !important;
        background: #191e28 !important;
        border: 1px solid #343b46 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }


    /* ----------------------------------------------
       HIDE SELECTED TEXT FROM INPUT
    ---------------------------------------------- */

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] input {
        color: transparent !important;
        caret-color: transparent !important;
        width: 5px !important;
        min-width: 5px !important;
    }


    /* ----------------------------------------------
       DROPDOWN MENU
    ---------------------------------------------- */

    div[data-baseweb="menu"] {
        background: #191e28 !important;
        border: 1px solid #343b46 !important;
        border-radius: 8px !important;
    }


    /* Dropdown options */
    div[data-baseweb="menu"] li {
        color: #e8edf2 !important;
        font-family: 'DM Sans', sans-serif !important;
    }


    /* Hover */
    div[data-baseweb="menu"] li:hover {
        background: #29313c !important;
    }


    /* ----------------------------------------------
       SIDEBAR LABEL
    ---------------------------------------------- */

    section[data-testid="stSidebar"] label {
        font-family: 'DM Sans', sans-serif;
        color: #dfe6eb;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# FILTER FUNCTION
# ==================================================

def add_filter(label, column):

    if column not in df.columns:
        return []

    values = sorted(
        df[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return st.sidebar.multiselect(
        label,
        options=values,
        default=values,
        placeholder="Select..."
    )


# ==================================================
# FILTERS
# ==================================================

gender = add_filter(
    "Gender",
    "Gender"
)

employment = add_filter(
    "Employment Type",
    "Employment_Type"
)

occupation = add_filter(
    "Occupation",
    "Occupation"
)


# ==================================================
# APPLY FILTERS
# ==================================================

filtered_df = df.copy()


if gender:
    filtered_df = filtered_df[
        filtered_df["Gender"]
        .astype(str)
        .isin(gender)
    ]


if employment:
    filtered_df = filtered_df[
        filtered_df["Employment_Type"]
        .astype(str)
        .isin(employment)
    ]


if occupation:
    filtered_df = filtered_df[
        filtered_df["Occupation"]
        .astype(str)
        .isin(occupation)
    ]


# ==================================================
# EMPTY DATA CHECK
# ==================================================

if filtered_df.empty:

    st.warning(
        "No customers match the selected filters."
    )

    st.stop()
# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<div class="dashboard-title">Financial Performance Analysis</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="dashboard-subtitle">'
    'Customer income, savings, investments, debt burden, credit usage and loan portfolio'
    '</div>',
    unsafe_allow_html=True
)
st.markdown('<div class="top-line"></div>', unsafe_allow_html=True)

# Screenshot-style navigation, without numbered sections.
view = st.radio(
    "Dashboard View",
    ["Financial Overview", "Income & Wealth", "Credit & Debt"],
    horizontal=True,
    label_visibility="collapsed"
)


# =========================================================
# KPI STRIP — LIMITED TO 4
# =========================================================
kpis = [
    (
        "CUSTOMERS",
        f"{filtered_df['Customer_ID'].nunique():,}",
        "Filtered portfolio"
    ),
    (
        "AVG MONTHLY INCOME",
        f"₹{filtered_df['Monthly_Income'].mean():,.0f}",
        "Average customer income"
    ),
    (
        "AVG SAVINGS",
        f"₹{filtered_df['Savings_Balance'].mean():,.0f}",
        "Average savings balance"
    ),
    (
        "AVG EMI",
        f"₹{filtered_df['EMI_Per_Month'].mean():,.0f}",
        "Average monthly repayment"
    )
]

cols = st.columns(4, gap="medium")

for col, (label, value, note) in zip(cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# PLOTLY THEME
# =========================================================
def dark_chart(fig, height=285):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter",
            size=9,
            color="#87919d"
        ),
        margin=dict(l=42, r=25, t=30, b=42),
        hoverlabel=dict(
            bgcolor="#171d27",
            bordercolor="#4a5360",
            font=dict(
                family="Inter",
                size=10,
                color="#f3f5f6"
            )
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=8, color="#9aa3ad"),
            orientation="h",
            y=1.10,
            x=0
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#242a34",
        zeroline=False,
        linecolor="#303743",
        tickfont=dict(size=8, color="#7e8995"),
        title_font=dict(size=8, color="#8b949e")
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#242a34",
        zeroline=False,
        linecolor="#303743",
        tickfont=dict(size=8, color="#7e8995"),
        title_font=dict(size=8, color="#8b949e")
    )

    return fig


CONFIG = {
    "displaylogo": False,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"]
}


# =========================================================
# FINANCIAL OVERVIEW
# =========================================================
if view == "Financial Overview":

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

   # Income vs Savings

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(
        '<div class="chart-title">Income vs Savings</div>'
        '<div class="chart-note">Savings behaviour relative to monthly income</div>',
        unsafe_allow_html=True
    )

    fig = px.scatter(
        filtered_df,
        x="Monthly_Income",
        y="Savings_Balance",
        color="Employment_Type",
        hover_name="Customer_ID",
        hover_data={
            "Monthly_Income": ":,.0f",
            "Savings_Balance": ":,.0f",
            "Savings_Percentage": ":.1f",
            "Employment_Type": True
        }
    )

    fig.update_traces(
        marker=dict(
            size=6,
            opacity=0.72
        )
    )

    # Legend on RIGHT side
    fig.update_layout(
        legend=dict(
            orientation="v",
            x=1.02,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            bgcolor="rgba(20,25,32,0.95)",
            bordercolor="#343b46",
            borderwidth=1,
            font=dict(
                family="DM Sans",
                size=9,
                color="#cbd3d9"
            )
        ),
        margin=dict(
            l=50,
            r=130,
            t=25,
            b=45
        )
    )

    dark_chart(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=CONFIG
    )


# Income vs Investments

with c2:

    st.markdown(
        '<div class="chart-title">Income vs Investments</div>'
        '<div class="chart-note">Investment value compared with earning capacity</div>',
        unsafe_allow_html=True
    )

    fig = px.scatter(
        filtered_df,
        x="Monthly_Income",
        y="Investment_Value",
        color="Occupation",
        hover_name="Customer_ID",
        hover_data={
            "Monthly_Income": ":,.0f",
            "Investment_Value": ":,.0f",
            "Investment_Percentage": ":.1f"
        }
    )

    fig.update_traces(
        marker=dict(
            size=6,
            opacity=0.65
        )
    )

    # Legend on RIGHT side
    fig.update_layout(
        legend=dict(
            orientation="v",
            x=1.02,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            bgcolor="rgba(20,25,32,0.95)",
            bordercolor="#343b46",
            borderwidth=1,
            font=dict(
                family="DM Sans",
                size=8,
                color="#cbd3d9"
            )
        ),
        margin=dict(
            l=50,
            r=145,
            t=25,
            b=45
        )
    )

    dark_chart(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=CONFIG
    )

    # Loan Portfolio
    with c3:
        st.markdown(
            '<div class="chart-title">Loan Portfolio</div>'
            '<div class="chart-note">Customers by number of active loans</div>',
            unsafe_allow_html=True
        )

        loan_counts = (
            filtered_df["Loan_Count"]
            .value_counts()
            .sort_index()
            .reset_index()
        )
        loan_counts.columns = ["Loan_Count", "Customers"]

        fig = px.bar(
            loan_counts,
            x="Loan_Count",
            y="Customers",
            text="Customers"
        )
        fig.update_traces(
            textposition="outside",
            textfont=dict(size=8, color="#aeb7bf")
        )
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # EMI
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            '<div class="chart-title">Monthly EMI Distribution</div>'
            '<div class="chart-note">Repayment burden across customers</div>',
            unsafe_allow_html=True
        )

        fig = px.histogram(
            filtered_df,
            x="EMI_Per_Month",
            nbins=24
        )
        fig.update_traces(opacity=.85)
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c2:
        st.markdown(
            '<div class="chart-title">Debt-to-Income Ratio</div>'
            '<div class="chart-note">Distribution of debt burden</div>',
            unsafe_allow_html=True
        )

        fig = px.box(
            filtered_df,
            y="Debt_To_Income_Ratio",
            points="outliers"
        )
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c3:
        st.markdown(
            '<div class="chart-title">Credit Utilization</div>'
            '<div class="chart-note">How much available credit customers use</div>',
            unsafe_allow_html=True
        )

        fig = px.histogram(
            filtered_df,
            x="Credit_Utilization",
            nbins=20
        )
        fig.update_traces(opacity=.85)
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)


# =========================================================
# INCOME & WEALTH
# =========================================================
elif view == "Income & Wealth":

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            '<div class="chart-title">Income vs Savings</div>'
            '<div class="chart-note">Customer-level savings relationship</div>',
            unsafe_allow_html=True
        )
        fig = px.scatter(
            filtered_df,
            x="Monthly_Income",
            y="Savings_Balance",
            color="Gender",
            hover_name="Customer_ID",
            hover_data=["Annual_Income", "Savings_Percentage"]
        )
        fig.update_traces(marker=dict(size=6, opacity=.72))
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c2:
        st.markdown(
            '<div class="chart-title">Income vs Investments</div>'
            '<div class="chart-note">Investment capacity across customers</div>',
            unsafe_allow_html=True
        )
        fig = px.scatter(
            filtered_df,
            x="Monthly_Income",
            y="Investment_Value",
            color="Employment_Type",
            hover_name="Customer_ID",
            hover_data=["Annual_Income", "Investment_Percentage"]
        )
        fig.update_traces(marker=dict(size=6, opacity=.68))
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c3:
        st.markdown(
            '<div class="chart-title">Savings by Employment</div>'
            '<div class="chart-note">Average savings balance by employment type</div>',
            unsafe_allow_html=True
        )
        x = (
            filtered_df.groupby("Employment_Type", as_index=False)
            ["Savings_Balance"].mean()
            .sort_values("Savings_Balance", ascending=False)
        )
        fig = px.bar(x, x="Employment_Type", y="Savings_Balance")
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            '<div class="chart-title">Investment by Occupation</div>'
            '<div class="chart-note">Average investment value across occupations</div>',
            unsafe_allow_html=True
        )
        x = (
            filtered_df.groupby("Occupation", as_index=False)
            ["Investment_Value"].mean()
            .sort_values("Investment_Value", ascending=False)
            .head(10)
        )
        fig = px.bar(
            x.sort_values("Investment_Value"),
            x="Investment_Value",
            y="Occupation",
            orientation="h"
        )
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c2:
        st.markdown(
            '<div class="chart-title">Annual Income Distribution</div>'
            '<div class="chart-note">Overall earning profile</div>',
            unsafe_allow_html=True
        )
        fig = px.histogram(filtered_df, x="Annual_Income", nbins=25)
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c3:
        st.markdown(
            '<div class="chart-title">Savings Percentage</div>'
            '<div class="chart-note">Savings relative to monthly income</div>',
            unsafe_allow_html=True
        )
        fig = px.histogram(
            filtered_df,
            x="Savings_Percentage",
            nbins=20
        )
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)


# =========================================================
# CREDIT & DEBT
# =========================================================
else:

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            '<div class="chart-title">Credit Utilization vs Credit Limit</div>'
            '<div class="chart-note">Credit usage against available capacity</div>',
            unsafe_allow_html=True
        )
        fig = px.scatter(
            filtered_df,
            x="Existing_Credit_Limit",
            y="Credit_Utilization",
            color="Credit_Score",
            hover_name="Customer_ID",
            hover_data=["Credit_Score", "Loan_Count"]
        )
        fig.update_traces(marker=dict(size=6, opacity=.7))
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c2:
        st.markdown(
            '<div class="chart-title">Debt-to-Income by Employment</div>'
            '<div class="chart-note">Average debt burden across employment types</div>',
            unsafe_allow_html=True
        )
        x = (
            filtered_df.groupby("Employment_Type", as_index=False)
            ["Debt_To_Income_Ratio"].mean()
            .sort_values("Debt_To_Income_Ratio", ascending=False)
        )
        fig = px.bar(
            x,
            x="Debt_To_Income_Ratio",
            y="Employment_Type",
            orientation="h"
        )
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c3:
        st.markdown(
            '<div class="chart-title">Existing Credit Limit</div>'
            '<div class="chart-note">Distribution of available credit capacity</div>',
            unsafe_allow_html=True
        )
        fig = px.histogram(
            filtered_df,
            x="Existing_Credit_Limit",
            nbins=25
        )
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            '<div class="chart-title">EMI vs Monthly Income</div>'
            '<div class="chart-note">Repayment level relative to income</div>',
            unsafe_allow_html=True
        )
        fig = px.scatter(
            filtered_df,
            x="Monthly_Income",
            y="EMI_Per_Month",
            color="Loan_Count",
            hover_name="Customer_ID",
            hover_data=["Debt_To_Income_Ratio"]
        )
        fig.update_traces(marker=dict(size=6, opacity=.68))
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c2:
        st.markdown(
            '<div class="chart-title">Loan Count vs Credit Score</div>'
            '<div class="chart-note">Credit profile across loan levels</div>',
            unsafe_allow_html=True
        )
        x = (
            filtered_df.groupby("Loan_Count", as_index=False)
            ["Credit_Score"].mean()
        )
        fig = px.line(
            x,
            x="Loan_Count",
            y="Credit_Score",
            markers=True
        )
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)

    with c3:
        st.markdown(
            '<div class="chart-title">Credit Score Distribution</div>'
            '<div class="chart-note">Overall customer credit profile</div>',
            unsafe_allow_html=True
        )
        fig = px.histogram(
            filtered_df,
            x="Credit_Score",
            nbins=25
        )
        dark_chart(fig)
        st.plotly_chart(fig, use_container_width=True, config=CONFIG)


# =========================================================
# FOOTER SUMMARY
# =========================================================
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="insight">'
    f'Current portfolio: {filtered_df["Customer_ID"].nunique():,} customers '
    f'| Avg DTI: {filtered_df["Debt_To_Income_Ratio"].mean():.2f} '
    f'| Avg Credit Utilization: {filtered_df["Credit_Utilization"].mean():.1f}% '
    f'| Avg Credit Score: {filtered_df["Credit_Score"].mean():.0f}'
    f'</div>',
    unsafe_allow_html=True
)
