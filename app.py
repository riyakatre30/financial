import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Financial Performance Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# PROFESSIONAL DASHBOARD STYLE
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

.stApp {
    background: #f4f2ee;
}

.block-container {
    max-width: 1450px;
    padding: 35px 50px 60px 50px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1 {
    color: #1f2d2a !important;
    font-size: 40px !important;
    font-weight: 700 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #263632 !important;
    font-weight: 600 !important;
}

.subtitle {
    color: #6d7773;
    font-size: 14px;
    margin-top: -8px;
    margin-bottom: 25px;
}

.section-text {
    color: #747d79;
    font-size: 13px;
    margin-top: -12px;
    margin-bottom: 16px;
}

.kpi-card {
    background: rgba(255,255,255,0.55);
    border-left: 3px solid #506861;
    border-bottom: 1px solid #d8d4cc;
    padding: 16px 18px;
    min-height: 100px;
}

.kpi-label {
    color: #727a77;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .7px;
    font-weight: 600;
}

.kpi-value {
    color: #1f2d2a;
    font-size: 24px;
    font-weight: 700;
    margin-top: 7px;
}

.kpi-note {
    color: #949b98;
    font-size: 10px;
    margin-top: 3px;
}

.insight {
    color: #59625f;
    font-size: 12px;
    border-top: 1px solid #d8d4cc;
    border-bottom: 1px solid #d8d4cc;
    padding: 11px 2px;
    margin: 5px 0 18px 0;
}

hr {
    border: 0;
    border-top: 1px solid #d8d4cc;
    margin: 34px 0;
}

[data-testid="stSidebar"] {
    background: #253330;
}

[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #f2f1ed !important;
}

div[data-testid="stPlotlyChart"] {
    margin-bottom: 4px;
}

.stDownloadButton button {
    background: #293a36;
    color: white;
    border: 0;
    border-radius: 7px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.markdown("# Financial Performance Analysis")
st.markdown(
    '<div class="subtitle">Income, savings, investments, repayment burden, '
    'credit capacity and loan portfolio analysis</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_excel("../Datasets/Credir_Card_Bank.xlsx")

# --------------------------------------------------
# CALCULATED COLUMNS
# --------------------------------------------------

df["Savings_Percentage"] = (
    df["Savings_Balance"] /
    df["Monthly_Income"]
) * 100

df["Investment_Percentage"] = (
    df["Investment_Value"] /
    df["Monthly_Income"]
) * 100


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.markdown(
    "<h2 style='font-size:20px;margin-bottom:5px;'>Analysis Filters</h2>",
    unsafe_allow_html=True
)
st.sidebar.caption("Select segments to update the complete financial analysis.")

# Gender
gender = st.sidebar.multiselect(
    "Gender",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

# Employment
employment = st.sidebar.multiselect(
    "Employment Type",
    options=df["Employment_Type"].unique(),
    default=df["Employment_Type"].unique()
)

# Occupation
occupation = st.sidebar.multiselect(
    "Occupation",
    options=df["Occupation"].unique(),
    default=df["Occupation"].unique()
)

# Residential Status
residential = st.sidebar.multiselect(
    "Residential Status",
    options=df["Residential_Status"].unique(),
    default=df["Residential_Status"].unique()
)

# Apply filters
filtered_df = df[
    (df["Gender"].isin(gender)) &
    (df["Employment_Type"].isin(employment)) &
    (df["Occupation"].isin(occupation)) &
    (df["Residential_Status"].isin(residential))
]

# ==================================================
# KPI CARDS — ONLY CORE FINANCIAL KPIs
# ==================================================

st.subheader("Financial Overview")

kpi_cards = [
    ("Customers", f"{filtered_df['Customer_ID'].nunique():,}", "Customer base"),
    ("Avg Monthly Income", f"₹{filtered_df['Monthly_Income'].mean():,.0f}", "Income"),
    ("Avg Savings", f"₹{filtered_df['Savings_Balance'].mean():,.0f}", "Savings balance"),
    ("Avg Investment", f"₹{filtered_df['Investment_Value'].mean():,.0f}", "Investment value"),
    ("Avg EMI", f"₹{filtered_df['EMI_Per_Month'].mean():,.0f}", "Monthly repayment")
]

cols = st.columns(5, gap="medium")

for col, (label, value, note) in zip(cols, kpi_cards):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown(
    f'<div class="insight">Showing <b>{len(filtered_df):,}</b> customers '
    f'after applying the selected filters.</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# INTERACTIVE CHART STYLE
# --------------------------------------------------

def chart_style(fig, height=390):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", size=11, color="#505a56"),
        title=dict(font=dict(size=16, color="#263632"), x=0),
        margin=dict(l=55, r=25, t=58, b=50),
        hoverlabel=dict(
            bgcolor="#253330",
            font=dict(family="DM Sans", color="white")
        ),
        legend=dict(
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="#ddd9d1",
        zeroline=False, linecolor="#c7c2b9"
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="#ddd9d1",
        zeroline=False, linecolor="#c7c2b9"
    )
    return fig

PLOTLY_CONFIG = {
    "displaylogo": False,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"]
}

st.markdown("---")

# ==================================================
# 1. INCOME VS SAVINGS
# ==================================================

st.header("01  Income vs Savings Analysis")
st.markdown(
    '<div class="section-text">Understand the relationship between monthly income and savings behaviour.</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2, gap="large")

with col1:
    fig = px.scatter(
        filtered_df,
        x="Monthly_Income",
        y="Savings_Balance",
        color="Employment_Type",
        hover_name="Customer_ID",
        hover_data=["Annual_Income", "Savings_Percentage"],
        trendline="ols",
        title="Income vs Savings"
    )
    fig.update_traces(marker=dict(size=7, opacity=0.65))
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    savings_emp = (
        filtered_df
        .groupby("Employment_Type")[["Annual_Income", "Savings_Balance"]]
        .mean()
        .round(2)
    )

    fig = px.bar(
        savings_emp.reset_index(),
        x="Employment_Type",
        y=["Annual_Income", "Savings_Balance"],
        barmode="group",
        title="Employment-wise Income & Savings"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# ==================================================
# 2. INCOME VS INVESTMENTS
# ==================================================

st.header("02  Income vs Investments")
st.markdown(
    '<div class="section-text">Compare earning capacity with investment value across customers and occupations.</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2, gap="large")

with col1:
    fig = px.scatter(
        filtered_df,
        x="Monthly_Income",
        y="Investment_Value",
        color="Occupation",
        hover_name="Customer_ID",
        hover_data=["Annual_Income", "Investment_Percentage"],
        trendline="ols",
        title="Income vs Investments"
    )
    fig.update_traces(marker=dict(size=7, opacity=0.65))
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    occupation_investment = (
        filtered_df
        .groupby("Occupation")[["Annual_Income", "Investment_Value"]]
        .mean()
        .round(2)
        .sort_values(by="Annual_Income", ascending=False)
        .head(10)
    )

    fig = px.bar(
        occupation_investment.reset_index(),
        x="Annual_Income",
        y="Occupation",
        orientation="h",
        color="Investment_Value",
        title="Top Occupations by Annual Income"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# ==================================================
# 3. EMI ANALYSIS
# ==================================================

st.header("03  EMI Analysis")
st.markdown(
    '<div class="section-text">Analyse monthly repayment distribution and average EMI across employment types.</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2, gap="large")

with col1:
    fig = px.histogram(
        filtered_df,
        x="EMI_Per_Month",
        nbins=30,
        marginal="box",
        title="Monthly EMI Distribution"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    emi_emp = (
        filtered_df
        .groupby("Employment_Type")["EMI_Per_Month"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig = px.bar(
        emi_emp,
        x="Employment_Type",
        y="EMI_Per_Month",
        text_auto=".2s",
        title="Average EMI by Employment Type"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# ==================================================
# 4. DEBT TO INCOME ANALYSIS
# ==================================================

st.header("04  Debt-to-Income Analysis")
st.markdown(
    '<div class="section-text">Measure the proportion of income committed to debt obligations.</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2, gap="large")

with col1:
    fig = px.box(
        filtered_df,
        y="Debt_To_Income_Ratio",
        points="outliers",
        title="Debt-to-Income Ratio"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    dti_emp = (
        filtered_df
        .groupby("Employment_Type")["Debt_To_Income_Ratio"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig = px.bar(
        dti_emp,
        x="Debt_To_Income_Ratio",
        y="Employment_Type",
        orientation="h",
        text_auto=".2f",
        title="Average DTI by Employment Type"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# ==================================================
# 5. CREDIT UTILIZATION
# ==================================================

st.header("05  Credit Utilization Analysis")
st.markdown(
    '<div class="section-text">Understand how heavily customers are using their available credit.</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2, gap="large")

with col1:
    fig = px.histogram(
        filtered_df,
        x="Credit_Utilization",
        nbins=20,
        marginal="box",
        title="Credit Utilization"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    occupation_credit = (
        filtered_df
        .groupby("Occupation")["Credit_Utilization"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
        .reset_index()
    )

    fig = px.bar(
        occupation_credit,
        x="Credit_Utilization",
        y="Occupation",
        orientation="h",
        text_auto=".1f",
        title="Credit Utilization by Occupation"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# ==================================================
# 6. EXISTING CREDIT LIMIT
# ==================================================

st.header("06  Existing Credit Limit Analysis")
st.markdown(
    '<div class="section-text">Analyse credit capacity and compare average limits across employment groups.</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2, gap="large")

with col1:
    fig = px.histogram(
        filtered_df,
        x="Existing_Credit_Limit",
        nbins=30,
        title="Existing Credit Limit"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    credit_emp = (
        filtered_df
        .groupby("Employment_Type")["Existing_Credit_Limit"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig = px.bar(
        credit_emp,
        x="Employment_Type",
        y="Existing_Credit_Limit",
        text_auto=".2s",
        title="Average Credit Limit by Employment Type"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# ==================================================
# 7. LOAN PORTFOLIO
# ==================================================

st.header("07  Loan Portfolio Analysis")
st.markdown(
    '<div class="section-text">See how customers are distributed by number of loans and how their financial profile changes.</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2, gap="large")

with col1:
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
        text="Customers",
        title="Loan Portfolio"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    loan_analysis = (
        filtered_df
        .groupby("Loan_Count")[["Annual_Income", "Credit_Score"]]
        .mean()
        .round(2)
        .reset_index()
    )

    fig = px.line(
        loan_analysis,
        x="Loan_Count",
        y=["Annual_Income", "Credit_Score"],
        markers=True,
        title="Loan Count vs Financial Profile"
    )
    chart_style(fig)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# ==================================================
# CORRELATION ANALYSIS
# ==================================================

st.header("Financial Correlation Analysis")
st.markdown(
    '<div class="section-text">Explore relationships between the major financial variables.</div>',
    unsafe_allow_html=True
)

corr_columns = [
    "Monthly_Income",
    "Annual_Income",
    "Savings_Balance",
    "Investment_Value",
    "EMI_Per_Month",
    "Debt_To_Income_Ratio",
    "Credit_Utilization",
    "Existing_Credit_Limit",
    "Loan_Count",
    "Credit_Score"
]

corr = filtered_df[corr_columns].corr()

fig = px.imshow(
    corr,
    text_auto=".2f",
    aspect="auto",
    color_continuous_scale="Viridis",
    title="Financial Correlation Matrix"
)

fig.update_layout(
    height=620,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", size=11, color="#505a56"),
    margin=dict(l=50, r=30, t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

# ==================================================
# KPI REPORT
# ==================================================

st.header("Financial Performance Report")

kpi = {
    "Total Customers":
        filtered_df["Customer_ID"].nunique(),

    "Average Monthly Income":
        filtered_df["Monthly_Income"].mean(),

    "Total Savings":
        filtered_df["Savings_Balance"].sum(),

    "Average Savings":
        filtered_df["Savings_Balance"].mean(),

    "Total Investments":
        filtered_df["Investment_Value"].sum(),

    "Average EMI":
        filtered_df["EMI_Per_Month"].mean(),

    "Average Debt To Income":
        filtered_df["Debt_To_Income_Ratio"].mean(),

    "Average Credit Utilization":
        filtered_df["Credit_Utilization"].mean(),

    "Average Credit Score":
        filtered_df["Credit_Score"].mean(),

    "Average Existing Credit Limit":
        filtered_df["Existing_Credit_Limit"].mean()
}

kpi_report = pd.DataFrame(
    kpi.items(),
    columns=["KPI", "Value"]
)

st.dataframe(
    kpi_report.round(2),
    use_container_width=True
)


# ==================================================
# DOWNLOAD
# ==================================================

st.header("Download Analysis Data")

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="financial_analysis.csv",
    mime="text/csv"
)
