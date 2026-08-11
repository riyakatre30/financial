import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Financial Performance Analysis",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- STYLE ----------
st.markdown("""
<style>
    .main {background-color: #f5f7fb;}
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    .dashboard-title {
        font-size: 38px; font-weight: 800; color: #172033;
        margin-bottom: 0px;
    }
    .dashboard-subtitle {color:#667085; font-size:16px; margin-top:0px;}
    .section-title {
        font-size: 22px; font-weight: 750; color:#172033;
        margin-top: 12px; margin-bottom: 8px;
    }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #e6eaf0;
        padding: 14px 16px; border-radius: 14px;
        box-shadow: 0 2px 8px rgba(20,30,50,.05);
    }
    .insight-box {
        background:white; border-left:5px solid #4f46e5;
        padding:14px 16px; border-radius:10px;
        margin-bottom:10px; color:#344054;
    }
</style>
""", unsafe_allow_html=True)

# ---------- DATA ----------
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
    else:
        # Put the Excel file in the same folder as app.py
        possible = ["Credir_Card_Bank.xlsx", "Credir_Card_Bank(4).xlsx"]
        data = None
        for f in possible:
            try:
                data = pd.read_excel(f)
                break
            except Exception:
                pass
        if data is None:
            return None

    data.columns = data.columns.str.strip()
    numeric_cols = [
        "Age","Monthly_Income","Annual_Income","Credit_Score",
        "Years_With_Bank","Existing_Credit_Cards","Existing_Credit_Limit",
        "Loan_Count","EMI_Per_Month","Debt_To_Income_Ratio",
        "Savings_Balance","Investment_Value","Avg_Monthly_Transactions",
        "Avg_Monthly_Spending","Credit_Utilization","Credit_History_Years",
        "Missed_Payments","Late_Payment_Count","Number_of_Defaults","Credit_Limit"
    ]
    for c in numeric_cols:
        if c in data.columns:
            data[c] = pd.to_numeric(data[c], errors="coerce")

    # Age group only for financial segmentation
    bins = [17,25,35,45,60,100]
    labels = ["18-25","26-35","36-45","46-60","60+"]
    data["Age_Group"] = pd.cut(data["Age"], bins=bins, labels=labels, include_lowest=True)

    return data

# ---------- SIDEBAR ----------
st.sidebar.markdown("## 📊 Financial Filters")
uploaded = st.sidebar.file_uploader("Upload Banking Excel File", type=["xlsx","xls"])
data = load_data(uploaded)

if data is None:
    st.error("Excel file nahi mila. app.py ke same folder me Credir_Card_Bank.xlsx rakho ya sidebar se upload karo.")
    st.stop()

st.sidebar.caption(f"Dataset: {len(data):,} customers | {len(data.columns)} columns")

def multiselect_filter(label, col):
    options = sorted(data[col].dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, options, default=options)

gender = multiselect_filter("Gender", "Gender")
employment = multiselect_filter("Employment Type", "Employment_Type")
occupation = multiselect_filter("Occupation", "Occupation")
residence = multiselect_filter("Residential Status", "Residential_Status")
age_group = multiselect_filter("Age Group", "Age_Group")

# income range
income_min = float(data["Annual_Income"].min())
income_max = float(data["Annual_Income"].max())
income_range = st.sidebar.slider(
    "Annual Income Range",
    min_value=float(np.floor(income_min)),
    max_value=float(np.ceil(income_max)),
    value=(float(np.floor(income_min)), float(np.ceil(income_max))),
    step=50000.0
)

filtered = data[
    data["Gender"].astype(str).isin(gender) &
    data["Employment_Type"].astype(str).isin(employment) &
    data["Occupation"].astype(str).isin(occupation) &
    data["Residential_Status"].astype(str).isin(residence) &
    data["Age_Group"].astype(str).isin(age_group) &
    data["Annual_Income"].between(income_range[0], income_range[1])
].copy()

# ---------- HELPERS ----------
def money(v):
    if pd.isna(v): return "₹0"
    if abs(v) >= 1e7: return f"₹{v/1e7:.2f} Cr"
    if abs(v) >= 1e5: return f"₹{v/1e5:.2f} L"
    if abs(v) >= 1e3: return f"₹{v/1e3:.1f}K"
    return f"₹{v:,.0f}"

def pct(v):
    return f"{v:.1f}%"

# ---------- HEADER ----------
st.markdown('<div class="dashboard-title">💰 Financial Performance Analysis</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-subtitle">Income • Savings • Investments • EMI • Debt • Credit • Loans | Interactive Banking Dashboard</div>',
    unsafe_allow_html=True
)
st.divider()

if filtered.empty:
    st.warning("Selected filters ke according koi customer nahi mila. Filters thode broad karo.")
    st.stop()

# ---------- KPI CARDS ----------
st.markdown('<div class="section-title">Executive Financial KPIs</div>', unsafe_allow_html=True)
c1,c2,c3,c4 = st.columns(4)
c5,c6,c7,c8 = st.columns(4)

c1.metric("Customers", f"{len(filtered):,}")
c2.metric("Avg Annual Income", money(filtered["Annual_Income"].mean()))
c3.metric("Avg Savings", money(filtered["Savings_Balance"].mean()))
c4.metric("Avg Investments", money(filtered["Investment_Value"].mean()))
c5.metric("Avg EMI / Month", money(filtered["EMI_Per_Month"].mean()))
c6.metric("Avg DTI", pct(filtered["Debt_To_Income_Ratio"].mean()*100))
c7.metric("Avg Credit Utilization", pct(filtered["Credit_Utilization"].mean()))
c8.metric("Total Loan Accounts", f"{int(filtered['Loan_Count'].sum()):,}")

# ---------- TASK 1 & 2 ----------
st.markdown('<div class="section-title">1 & 2. Income vs Savings / Investments</div>', unsafe_allow_html=True)
a,b = st.columns(2)

with a:
    fig = px.scatter(
        filtered, x="Annual_Income", y="Savings_Balance",
        color="Employment_Type", size="Savings_Balance",
        hover_data=["Customer_ID","Occupation","Debt_To_Income_Ratio"],
        trendline="ols",
        labels={"Annual_Income":"Annual Income (₹)", "Savings_Balance":"Savings Balance (₹)"},
        title="Income vs Savings"
    )
    fig.update_layout(height=420, legend_title="Employment")
    st.plotly_chart(fig, use_container_width=True)

with b:
    fig = px.scatter(
        filtered, x="Annual_Income", y="Investment_Value",
        color="Age_Group", size="Investment_Value",
        hover_data=["Customer_ID","Occupation","Credit_Score"],
        trendline="ols",
        labels={"Annual_Income":"Annual Income (₹)", "Investment_Value":"Investment Value (₹)"},
        title="Income vs Investments"
    )
    fig.update_layout(height=420, legend_title="Age Group")
    st.plotly_chart(fig, use_container_width=True)

# ---------- TASK 3 ----------
st.markdown('<div class="section-title">3. EMI Analysis</div>', unsafe_allow_html=True)
a,b = st.columns([1.2,1])

with a:
    emi_by_emp = filtered.groupby("Employment_Type", as_index=False)["EMI_Per_Month"].mean()
    fig = px.bar(
        emi_by_emp, x="Employment_Type", y="EMI_Per_Month",
        text_auto=".2s", title="Average Monthly EMI by Employment Type",
        labels={"EMI_Per_Month":"Average EMI (₹)", "Employment_Type":"Employment"}
    )
    fig.update_traces(texttemplate="₹%{y:,.0f}", textposition="outside")
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

with b:
    fig = px.box(
        filtered, x="Employment_Type", y="EMI_Per_Month",
        color="Employment_Type", points="outliers",
        title="EMI Distribution"
    )
    fig.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------- TASK 4 ----------
st.markdown('<div class="section-title">4. Debt-to-Income Analysis</div>', unsafe_allow_html=True)
a,b = st.columns(2)

with a:
    fig = px.histogram(
        filtered, x="Debt_To_Income_Ratio", nbins=25,
        marginal="box", title="Debt-to-Income Ratio Distribution",
        labels={"Debt_To_Income_Ratio":"DTI Ratio"}
    )
    fig.update_xaxes(tickformat=".0%")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with b:
    # DTI risk bands for financial interpretation
    temp = filtered.copy()
    temp["DTI_Band"] = pd.cut(
        temp["Debt_To_Income_Ratio"],
        bins=[-np.inf, .20, .35, .50, np.inf],
        labels=["Low (<20%)","Moderate (20–35%)","High (35–50%)","Very High (>50%)"]
    )
    dti = temp["DTI_Band"].value_counts().reindex(
        ["Low (<20%)","Moderate (20–35%)","High (35–50%)","Very High (>50%)"]
    ).fillna(0).reset_index()
    dti.columns = ["DTI_Band","Customers"]
    fig = px.bar(
        dti, x="DTI_Band", y="Customers", text_auto=True,
        title="Customers by DTI Risk Band"
    )
    fig.update_layout(height=400, xaxis_title="", yaxis_title="Customers")
    st.plotly_chart(fig, use_container_width=True)

# ---------- TASK 5 ----------
st.markdown('<div class="section-title">5. Credit Utilization Analysis</div>', unsafe_allow_html=True)
a,b = st.columns([1,1.2])

with a:
    utilization = filtered["Credit_Utilization"].mean()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=utilization,
        number={"suffix":"%"},
        title={"text":"Average Credit Utilization"},
        gauge={
            "axis":{"range":[0,100]},
            "threshold":{"line":{"width":4},"value":80},
            "steps":[
                {"range":[0,30],"name":"Low"},
                {"range":[30,70],"name":"Moderate"},
                {"range":[70,100],"name":"High"}
            ]
        }
    ))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with b:
    fig = px.scatter(
        filtered, x="Credit_Utilization", y="Credit_Score",
        size="Credit_Limit", color="Debt_To_Income_Ratio",
        hover_data=["Customer_ID","Existing_Credit_Limit","Loan_Count"],
        title="Credit Utilization vs Credit Score",
        labels={
            "Credit_Utilization":"Credit Utilization (%)",
            "Credit_Score":"Credit Score",
            "Debt_To_Income_Ratio":"DTI"
        }
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ---------- TASK 6 ----------
st.markdown('<div class="section-title">6. Existing Credit Limit Analysis</div>', unsafe_allow_html=True)
a,b = st.columns(2)

with a:
    fig = px.scatter(
        filtered, x="Existing_Credit_Limit", y="Credit_Limit",
        color="Credit_Score", size="Annual_Income",
        hover_data=["Customer_ID","Occupation","Credit_Utilization"],
        trendline="ols",
        title="Existing Credit Limit vs Current Credit Limit",
        labels={"Existing_Credit_Limit":"Existing Credit Limit (₹)",
                "Credit_Limit":"Credit Limit (₹)"}
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

with b:
    emp_limit = filtered.groupby("Employment_Type", as_index=False).agg(
        Existing_Limit=("Existing_Credit_Limit","mean"),
        Credit_Limit=("Credit_Limit","mean")
    )
    long_limit = emp_limit.melt(
        id_vars="Employment_Type",
        value_vars=["Existing_Limit","Credit_Limit"],
        var_name="Limit_Type", value_name="Average_Limit"
    )
    fig = px.bar(
        long_limit, x="Employment_Type", y="Average_Limit",
        color="Limit_Type", barmode="group",
        text_auto=".2s", title="Average Credit Limits by Employment Type",
        labels={"Average_Limit":"Average Limit (₹)"}
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

# ---------- TASK 7 ----------
st.markdown('<div class="section-title">7. Loan Portfolio Analysis</div>', unsafe_allow_html=True)
a,b = st.columns([1,1.25])

with a:
    loan_portfolio = filtered.groupby("Loan_Count").size().reset_index(name="Customers")
    fig = px.pie(
        loan_portfolio, names="Loan_Count", values="Customers",
        hole=.55, title="Customer Distribution by Loan Count"
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

with b:
    loan_summary = filtered.groupby("Loan_Count", as_index=False).agg(
        Customers=("Customer_ID","count"),
        Avg_EMI=("EMI_Per_Month","mean"),
        Avg_DTI=("Debt_To_Income_Ratio","mean"),
        Avg_Credit_Utilization=("Credit_Utilization","mean")
    )
    fig = px.bar(
        loan_summary, x="Loan_Count", y="Customers",
        color="Avg_DTI", text="Customers",
        title="Loan Count vs Customer Volume",
        labels={"Loan_Count":"Number of Loans","Customers":"Customers","Avg_DTI":"Avg DTI"}
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

# ---------- FINANCIAL INSIGHTS ----------
st.markdown('<div class="section-title">💡 Financial Performance Insights</div>', unsafe_allow_html=True)

avg_income = filtered["Annual_Income"].mean()
avg_savings = filtered["Savings_Balance"].mean()
avg_invest = filtered["Investment_Value"].mean()
avg_emi = filtered["EMI_Per_Month"].mean()
avg_dti = filtered["Debt_To_Income_Ratio"].mean()
avg_util = filtered["Credit_Utilization"].mean()

savings_rate = avg_savings / avg_income if avg_income else 0
investment_rate = avg_invest / avg_income if avg_income else 0

insights = [
    f"**Savings position:** Average savings are {money(avg_savings)}, approximately {savings_rate*100:.1f}% of average annual income.",
    f"**Investment position:** Average investment value is {money(avg_invest)}, around {investment_rate*100:.1f}% of average annual income.",
    f"**Debt burden:** Average DTI is {avg_dti*100:.1f}%. Higher DTI indicates a larger portion of income is committed to debt obligations.",
    f"**Credit usage:** Average credit utilization is {avg_util:.1f}%. Customers with high utilization deserve closer financial monitoring.",
    f"**EMI burden:** Average monthly EMI is {money(avg_emi)}; compare EMI with income when evaluating repayment capacity.",
    f"**Loan portfolio:** Customers hold an average of {filtered['Loan_Count'].mean():.2f} loans, helping identify segments with heavier borrowing exposure."
]
for text in insights:
    st.markdown(f'<div class="insight-box">📌 {text}</div>', unsafe_allow_html=True)

# ---------- DOWNLOAD FILTERED DATA ----------
st.markdown('<div class="section-title">Filtered Financial Data</div>', unsafe_allow_html=True)
st.dataframe(
    filtered[[
        "Customer_ID","Annual_Income","Savings_Balance","Investment_Value",
        "EMI_Per_Month","Debt_To_Income_Ratio","Credit_Utilization",
        "Existing_Credit_Limit","Credit_Limit","Loan_Count"
    ]].reset_index(drop=True),
    use_container_width=True, height=300
)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered Financial Data",
    data=csv,
    file_name="financial_analysis_filtered_data.csv",
    mime="text/csv"
)

st.caption("Financial Performance Analysis Dashboard | Built with Streamlit + Plotly")
