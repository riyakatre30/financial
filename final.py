import io
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# FINELITE — FINAL CUSTOMER CREDIT & RISK INTELLIGENCE
# ============================================================

st.set_page_config(
    page_title="FinElite | Customer Credit Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- STYLE --------------------------
st.markdown("""
<style>
.stApp { background: #f6f8fc; }
.block-container { max-width: 1500px; padding-top: 1.2rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] { background: #eef2ff; }
.hero {
    background: linear-gradient(120deg,#172554,#2563eb);
    padding: 24px 28px; border-radius: 18px; color: white;
    margin-bottom: 18px; box-shadow: 0 8px 24px rgba(37,99,235,.18);
}
.hero h1 { margin: 0; font-size: 2.25rem; }
.hero p { margin: 7px 0 0; opacity: .88; }
.section {
    background: linear-gradient(90deg,#172554,#2563eb);
    color: white; padding: 10px 15px; border-radius: 10px;
    margin: 18px 0 12px; font-weight: 700;
}
[data-testid="stMetric"] {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 14px;
    box-shadow: 0 3px 12px rgba(15,23,42,.06);
}
[data-testid="stMetricLabel"] { color:#475569; }
[data-testid="stMetricValue"] { color:#172554; }
.risk-high { background:#fee2e2; border-left:5px solid #dc2626; padding:12px 15px; border-radius:8px; }
.risk-med { background:#ffedd5; border-left:5px solid #ea580c; padding:12px 15px; border-radius:8px; }
.risk-low { background:#dcfce7; border-left:5px solid #059669; padding:12px 15px; border-radius:8px; }
.insight { background:#eff6ff; border-left:5px solid #2563eb; padding:12px 15px; border-radius:8px; }
.small-note { color:#64748b; font-size:.88rem; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- DATA ---------------------------
EXPECTED_NUMERIC = [
    "Age","Monthly_Income","Annual_Income","Credit_Score","Years_With_Bank",
    "Existing_Credit_Cards","Existing_Credit_Limit","Loan_Count","EMI_Per_Month",
    "Debt_To_Income_Ratio","Savings_Balance","Investment_Value",
    "Avg_Monthly_Transactions","Avg_Monthly_Spending","Credit_Utilization",
    "Credit_History_Years","Missed_Payments","Late_Payment_Count",
    "Number_of_Defaults","Credit_Limit"
]

@st.cache_data
def read_excel(file_bytes=None, filename="Credir_Card_Bank.xlsx"):
    if file_bytes is not None:
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        candidates = [
            filename, "Credir_Card_Bank.xlsx", "Credir_Card_Bank(4).xlsx",
            "../DataSets/Credir_Card_Bank.xlsx"
        ]
        path = next((p for p in candidates if os.path.exists(p)), None)
        if path is None:
            raise FileNotFoundError("Dataset not found. Upload the Excel file from the sidebar.")
        df = pd.read_excel(path)

    df.columns = df.columns.astype(str).str.strip().str.replace(" ", "_", regex=False)

    for c in EXPECTED_NUMERIC:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Target and analytical features used by the existing dashboards.
    if "Number_of_Defaults" in df.columns:
        df["Default_Next_Month"] = (df["Number_of_Defaults"] > 0).astype(int)
    else:
        df["Default_Next_Month"] = 0

    if "Age" in df.columns:
        df["Age_Group"] = pd.cut(
            df["Age"], [18,25,35,50,65,100],
            labels=["18-25","26-35","36-50","51-65","65+"],
            include_lowest=True
        )

    if "Credit_Score" in df.columns:
        def credit_band(x):
            if pd.isna(x): return "Unknown"
            if x < 580: return "Poor"
            if x < 670: return "Fair"
            if x < 740: return "Good"
            if x < 800: return "Very Good"
            return "Excellent"
        df["Credit_Band"] = df["Credit_Score"].apply(credit_band)

    # Existing risk logic from the supplied risk dashboard.
    if all(c in df.columns for c in ["Credit_Score","Credit_Utilization","Missed_Payments"]):
        high = (
            (df["Credit_Score"] < 600) |
            (df["Credit_Utilization"] > 75) |
            (df["Missed_Payments"] >= 3)
        )
        df["High_Risk_Flag"] = np.where(high, "High Risk", "Standard")
    else:
        df["High_Risk_Flag"] = "Standard"

    risk_cols = [
        "Debt_To_Income_Ratio","Credit_Utilization","Missed_Payments",
        "Late_Payment_Count","Number_of_Defaults"
    ]
    if all(c in df.columns for c in risk_cols):
        df["Risk_Indicator"] = (
            df["Debt_To_Income_Ratio"] * 35
            + (df["Credit_Utilization"] / 100) * 25
            + df["Missed_Payments"] * 4
            + df["Late_Payment_Count"] * 1.5
            + df["Number_of_Defaults"] * 12
        )
        df["Risk_Level"] = pd.cut(
            df["Risk_Indicator"],
            [-np.inf,25,50,np.inf],
            labels=["Lower","Moderate","Higher"]
        )
    else:
        df["Risk_Indicator"] = 0.0
        df["Risk_Level"] = "Lower"

    return df

def money(v):
    if pd.isna(v): return "₹0"
    v = float(v)
    if abs(v) >= 1e7: return f"₹{v/1e7:.2f} Cr"
    if abs(v) >= 1e5: return f"₹{v/1e5:.2f} L"
    return f"₹{v:,.0f}"

def safe_mean(d, c):
    return float(d[c].mean()) if c in d and len(d) else 0.0

def fig_clean(fig, height=380):
    fig.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=10,r=10,t=55,b=10),
        legend_title_text=""
    )
    return fig

# ----------------------------- SIDEBAR ------------------------
st.sidebar.markdown("## 💳 FinElite")
st.sidebar.caption("Customer Credit & Risk Intelligence")

uploaded = st.sidebar.file_uploader("📁 Upload Customer Excel", type=["xlsx","xls"])

try:
    file_bytes = uploaded.getvalue() if uploaded else None
    df = read_excel(file_bytes)
except Exception as e:
    st.error(f"Unable to load the customer dataset: {e}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Portfolio Filters")

def opts(col):
    return sorted(df[col].dropna().astype(str).unique().tolist()) if col in df.columns else []

def multi(label, col):
    values = opts(col)
    return st.sidebar.multiselect(label, values, default=values) if values else []

gender = multi("Gender", "Gender")
employment = multi("Employment Type", "Employment_Type")
residential = multi("Residential Status", "Residential_Status")
kyc = multi("KYC Status", "KYC_Status")
fraud = multi("Fraud Flag", "Fraud_Flag")

age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

score_min, score_max = int(df["Credit_Score"].min()), int(df["Credit_Score"].max())
score_range = st.sidebar.slider("Credit Score", score_min, score_max, (score_min, score_max))

income_min, income_max = float(df["Annual_Income"].min()), float(df["Annual_Income"].max())
income_range = st.sidebar.slider(
    "Annual Income", income_min, income_max, (income_min, income_max),
    format="₹%.0f"
)

risk_filter = st.sidebar.radio(
    "Risk Segment", ["All Customers","Higher Risk Only","Moderate Risk Only","Lower Risk Only"],
    index=0
)
util_max = st.sidebar.slider("Maximum Credit Utilization (%)", 0, 100, 100)

filtered = df.copy()
if gender: filtered = filtered[filtered["Gender"].astype(str).isin(gender)]
if employment: filtered = filtered[filtered["Employment_Type"].astype(str).isin(employment)]
if residential: filtered = filtered[filtered["Residential_Status"].astype(str).isin(residential)]
if kyc: filtered = filtered[filtered["KYC_Status"].astype(str).isin(kyc)]
if fraud: filtered = filtered[filtered["Fraud_Flag"].astype(str).isin(fraud)]
filtered = filtered[filtered["Age"].between(*age_range)]
filtered = filtered[filtered["Credit_Score"].between(*score_range)]
filtered = filtered[filtered["Annual_Income"].between(*income_range)]
filtered = filtered[filtered["Credit_Utilization"] <= util_max]

if risk_filter == "Higher Risk Only":
    filtered = filtered[filtered["Risk_Level"].astype(str) == "Higher"]
elif risk_filter == "Moderate Risk Only":
    filtered = filtered[filtered["Risk_Level"].astype(str) == "Moderate"]
elif risk_filter == "Lower Risk Only":
    filtered = filtered[filtered["Risk_Level"].astype(str) == "Lower"]

st.sidebar.info(f"Showing **{len(filtered):,}** of **{len(df):,}** customers")

# ----------------------------- HEADER -------------------------
st.markdown("""
<div class="hero">
<h1>💳 FinElite — Customer Credit Intelligence</h1>
<p>Unified customer profiling, credit health, financial behaviour, default risk, fraud & compliance analytics.</p>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No customers match the selected filters. Please widen the filters.")
    st.stop()

# ----------------------------- KPIs ---------------------------
customers = len(filtered)
defaults = int(filtered["Default_Next_Month"].sum())
default_rate = defaults / customers * 100
high_risk = int((filtered["High_Risk_Flag"] == "High Risk").sum())
higher_level = int((filtered["Risk_Level"].astype(str) == "Higher").sum())
avg_score = safe_mean(filtered,"Credit_Score")
avg_util = safe_mean(filtered,"Credit_Utilization")
avg_dti = safe_mean(filtered,"Debt_To_Income_Ratio")
total_limit = filtered["Credit_Limit"].sum() if "Credit_Limit" in filtered else 0

k = st.columns(7)
k[0].metric("Customers", f"{customers:,}")
k[1].metric("Avg Credit Score", f"{avg_score:,.0f}")
k[2].metric("Default Rate", f"{default_rate:.2f}%")
k[3].metric("High-Risk Customers", f"{high_risk:,}")
k[4].metric("Higher Risk Level", f"{higher_level:,}")
k[5].metric("Avg Utilization", f"{avg_util:.1f}%")
k[6].metric("Credit Exposure", money(total_limit))

# ----------------------------- TABS ---------------------------
tabs = st.tabs([
    "🏠 Executive Overview",
    "👤 Customer 360",
    "💳 Credit Health",
    "⚠️ Risk & Defaults",
    "💰 Financial Behaviour",
    "🛡️ Fraud & Compliance",
    "📋 Customer Data"
])

# ========================= OVERVIEW ===========================
with tabs[0]:
    st.markdown('<div class="section">📊 Portfolio Overview</div>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)

    with c1:
        band = filtered["Credit_Band"].value_counts().reset_index()
        band.columns = ["Credit Band","Customers"]
        st.plotly_chart(fig_clean(px.bar(
            band, x="Credit Band", y="Customers", color="Credit Band",
            title="Credit Score Distribution"
        )), use_container_width=True)

    with c2:
        risk = filtered["Risk_Level"].astype(str).value_counts().reset_index()
        risk.columns = ["Risk Level","Customers"]
        st.plotly_chart(fig_clean(px.pie(
            risk, names="Risk Level", values="Customers", hole=.55,
            title="Portfolio Risk Mix"
        )), use_container_width=True)

    with c3:
        default = filtered["Default_Next_Month"].map({0:"Non-Defaulter",1:"Defaulter"}).value_counts().reset_index()
        default.columns = ["Status","Customers"]
        st.plotly_chart(fig_clean(px.bar(
            default, x="Status", y="Customers", color="Status",
            title="Default Portfolio"
        )), use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        if all(c in filtered.columns for c in ["Annual_Income","Savings_Balance"]):
            st.plotly_chart(fig_clean(px.scatter(
                filtered, x="Annual_Income", y="Savings_Balance",
                color="Credit_Band", size="Credit_Limit" if "Credit_Limit" in filtered else None,
                hover_data=[c for c in ["Customer_ID","Credit_Score","Risk_Level"] if c in filtered],
                title="Income vs Savings"
            )), use_container_width=True)

    with c2:
        if all(c in filtered.columns for c in ["Annual_Income","Investment_Value"]):
            st.plotly_chart(fig_clean(px.scatter(
                filtered, x="Annual_Income", y="Investment_Value",
                color="Risk_Level", size="Credit_Limit" if "Credit_Limit" in filtered else None,
                hover_data=[c for c in ["Customer_ID","Credit_Score","Credit_Utilization"] if c in filtered],
                title="Income vs Investment"
            )), use_container_width=True)

    st.markdown('<div class="section">💡 Automated Portfolio Insights</div>', unsafe_allow_html=True)
    avg_income = safe_mean(filtered,"Annual_Income")
    st.markdown(f'<div class="insight"><b>Portfolio:</b> {customers:,} customers are currently selected. Average annual income is {money(avg_income)} and average credit score is {avg_score:,.0f}.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="risk-high"><b>Risk exposure:</b> {high_risk:,} customers meet the dashboard high-risk rule, while the calculated higher-risk segment contains {higher_level:,} customers.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="risk-med"><b>Credit pressure:</b> Average credit utilization is {avg_util:.1f}% and average DTI is {avg_dti:.2f}. These metrics should be reviewed together with repayment history.</div>', unsafe_allow_html=True)

# ========================= CUSTOMER 360 =======================
with tabs[1]:
    st.markdown('<div class="section">👤 Customer 360 — Individual Credit Profile</div>', unsafe_allow_html=True)
    id_col = "Customer_ID" if "Customer_ID" in filtered.columns else filtered.columns[0]
    customer_ids = filtered[id_col].astype(str).tolist()
    selected_id = st.selectbox("Search / Select Customer", customer_ids)

    customer = filtered[filtered[id_col].astype(str) == selected_id].iloc[0]

    r = st.columns(5)
    r[0].metric("Credit Score", f"{customer.get('Credit_Score',0):,.0f}")
    r[1].metric("Credit Limit", money(customer.get("Credit_Limit",0)))
    r[2].metric("Utilization", f"{customer.get('Credit_Utilization',0):.1f}%")
    r[3].metric("DTI", f"{customer.get('Debt_To_Income_Ratio',0):.2f}")
    r[4].metric("Risk Indicator", f"{customer.get('Risk_Indicator',0):.1f}")

    level = str(customer.get("Risk_Level","Lower"))
    if level == "Higher":
        st.markdown('<div class="risk-high"><b>⚠️ HIGHER RISK PROFILE</b><br>Review repayment capacity, utilization, DTI and defaults before extending additional exposure.</div>', unsafe_allow_html=True)
    elif level == "Moderate":
        st.markdown('<div class="risk-med"><b>🟠 MODERATE RISK PROFILE</b><br>Monitor repayment behaviour and credit utilization.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="risk-low"><b>🟢 LOWER RISK PROFILE</b><br>Current calculated indicators are comparatively lower.</div>', unsafe_allow_html=True)

    a,b,c = st.columns(3)
    with a:
        st.markdown("#### Personal & Banking")
        fields = ["Customer_ID","Age","Gender","Employment_Type","Occupation","Residential_Status","Years_With_Bank"]
        st.dataframe(pd.DataFrame({
            "Metric":[x.replace("_"," ") for x in fields if x in customer.index],
            "Value":[customer[x] for x in fields if x in customer.index]
        }), hide_index=True, use_container_width=True)
    with b:
        st.markdown("#### Credit & Loan")
        fields = ["Credit_Score","Credit_Band","Credit_Limit","Existing_Credit_Limit","Existing_Credit_Cards","Loan_Count","EMI_Per_Month"]
        st.dataframe(pd.DataFrame({
            "Metric":[x.replace("_"," ") for x in fields if x in customer.index],
            "Value":[customer[x] for x in fields if x in customer.index]
        }), hide_index=True, use_container_width=True)
    with c:
        st.markdown("#### Repayment & Risk")
        fields = ["Credit_Utilization","Debt_To_Income_Ratio","Missed_Payments","Late_Payment_Count","Number_of_Defaults","Fraud_Flag","KYC_Status","PAN_Verified"]
        st.dataframe(pd.DataFrame({
            "Metric":[x.replace("_"," ") for x in fields if x in customer.index],
            "Value":[customer[x] for x in fields if x in customer.index]
        }), hide_index=True, use_container_width=True)

    numeric_profile = ["Credit_Score","Credit_Utilization","Debt_To_Income_Ratio","Savings_Balance","Investment_Value","Avg_Monthly_Spending","EMI_Per_Month"]
    profile = pd.DataFrame({
        "Metric":[x.replace("_"," ") for x in numeric_profile if x in customer.index],
        "Value":[float(customer[x]) for x in numeric_profile if x in customer.index]
    })
    st.plotly_chart(fig_clean(px.bar(profile, x="Metric", y="Value", title="Customer Financial & Credit Indicators"), 360), use_container_width=True)

# ========================= CREDIT HEALTH =====================
with tabs[2]:
    st.markdown('<div class="section">💳 Credit Health & Exposure</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_clean(px.histogram(
            filtered, x="Credit_Score", color="Credit_Band", nbins=30,
            title="Credit Score Distribution"
        )), use_container_width=True)
    with c2:
        st.plotly_chart(fig_clean(px.scatter(
            filtered, x="Credit_Score", y="Credit_Utilization",
            color="Default_Next_Month",
            hover_data=[c for c in ["Customer_ID","Risk_Level","Debt_To_Income_Ratio"] if c in filtered],
            title="Credit Score vs Utilization"
        )), use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        if "Debt_To_Income_Ratio" in filtered:
            st.plotly_chart(fig_clean(px.scatter(
                filtered, x="Debt_To_Income_Ratio", y="Credit_Score",
                color="Risk_Level", size="Loan_Count" if "Loan_Count" in filtered else None,
                title="DTI vs Credit Score"
            )), use_container_width=True)
    with c2:
        if "Credit_Utilization" in filtered:
            box = px.box(filtered, x="Default_Next_Month", y="Credit_Utilization",
                         color="Default_Next_Month", title="Utilization by Default Status")
            box.update_xaxes(ticktext=["Non-Defaulter","Defaulter"], tickvals=[0,1])
            st.plotly_chart(fig_clean(box), use_container_width=True)

    if "Employment_Type" in filtered:
        emp = filtered.groupby("Employment_Type", observed=True).agg(
            Avg_Credit_Score=("Credit_Score","mean"),
            Avg_Utilization=("Credit_Utilization","mean"),
            Customers=(id_col,"count")
        ).reset_index()
        st.plotly_chart(fig_clean(px.bar(
            emp.sort_values("Avg_Credit_Score"),
            x="Employment_Type", y="Avg_Credit_Score", color="Avg_Utilization",
            title="Credit Health by Employment Type"
        )), use_container_width=True)

# ========================= RISK & DEFAULTS ====================
with tabs[3]:
    st.markdown('<div class="section">⚠️ Risk, Defaults & Early Warning</div>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    c1.metric("Defaulters", f"{defaults:,}")
    c2.metric("Default Rate", f"{default_rate:.2f}%")
    c3.metric("Avg Late Payments", f"{safe_mean(filtered,'Late_Payment_Count'):.2f}")

    c1,c2 = st.columns(2)
    with c1:
        if "Age_Group" in filtered:
            age_risk = filtered.groupby("Age_Group", observed=False)["Default_Next_Month"].mean().reset_index()
            age_risk["Default Rate (%)"] = age_risk["Default_Next_Month"] * 100
            st.plotly_chart(fig_clean(px.bar(age_risk, x="Age_Group", y="Default Rate (%)",
                                              title="Default Rate by Age Group")), use_container_width=True)
    with c2:
        if "Occupation" in filtered:
            occ = filtered.groupby("Occupation")["Default_Next_Month"].mean().mul(100).sort_values().reset_index(name="Default Rate (%)")
            st.plotly_chart(fig_clean(px.bar(occ, y="Occupation", x="Default Rate (%)", orientation="h",
                                              title="Default Rate by Occupation")), use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        corr_cols = filtered.select_dtypes(include=np.number)
        if "Default_Next_Month" in corr_cols and len(corr_cols.columns) > 1:
            corr = corr_cols.corr()["Default_Next_Month"].drop("Default_Next_Month", errors="ignore").sort_values()
            corr_df = corr.reset_index()
            corr_df.columns = ["Feature","Correlation"]
            st.plotly_chart(fig_clean(px.bar(
                corr_df, y="Feature", x="Correlation", orientation="h",
                color="Correlation", color_continuous_scale="RdBu_r",
                title="Features Associated with Default"
            )), use_container_width=True)
    with c2:
        risk_counts = filtered["Risk_Level"].astype(str).value_counts().reset_index()
        risk_counts.columns = ["Risk Level","Customers"]
        st.plotly_chart(fig_clean(px.bar(
            risk_counts, x="Risk Level", y="Customers", color="Risk Level",
            title="Calculated Risk Level"
        )), use_container_width=True)

    st.markdown("#### 🚨 Highest Priority Customers")
    priority_cols = [c for c in [
        "Customer_ID","Credit_Score","Credit_Utilization","Debt_To_Income_Ratio",
        "Missed_Payments","Late_Payment_Count","Number_of_Defaults",
        "Risk_Indicator","Risk_Level","Default_Next_Month"
    ] if c in filtered.columns]
    priority = filtered.sort_values(["Risk_Indicator","Credit_Utilization"], ascending=False)[priority_cols].head(25)
    st.dataframe(priority, hide_index=True, use_container_width=True)

    csv = priority.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download High-Risk Customer List", csv, "finelite_high_risk_customers.csv", "text/csv")

    st.markdown('<div class="small-note">Risk indicators are analytical rules derived from the supplied dashboards; they are intended for portfolio analysis, not an automated lending decision.</div>', unsafe_allow_html=True)

# ========================= FINANCIAL ==========================
with tabs[4]:
    st.markdown('<div class="section">💰 Financial Behaviour & Customer Capacity</div>', unsafe_allow_html=True)

    metric_map = {
        "Savings Balance":"Savings_Balance",
        "Investment Value":"Investment_Value",
        "Monthly Spending":"Avg_Monthly_Spending",
        "Monthly EMI":"EMI_Per_Month",
        "Monthly Transactions":"Avg_Monthly_Transactions"
    }
    label = st.selectbox("Analyze Financial Metric", list(metric_map))
    metric = metric_map[label]

    c1,c2 = st.columns(2)
    with c1:
        if "Annual_Income" in filtered and metric in filtered:
            st.plotly_chart(fig_clean(px.scatter(
                filtered, x="Annual_Income", y=metric,
                color="Credit_Band",
                hover_data=[c for c in ["Customer_ID","Credit_Score","Risk_Level"] if c in filtered],
                title=f"Annual Income vs {label}"
            )), use_container_width=True)
    with c2:
        if "Occupation" in filtered and metric in filtered:
            summary = filtered.groupby("Occupation")[metric].mean().sort_values(ascending=False).head(10).reset_index()
            st.plotly_chart(fig_clean(px.bar(
                summary, x=metric, y="Occupation", orientation="h",
                title=f"Top Occupations by Average {label}"
            )), use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_clean(px.histogram(
            filtered, x="Avg_Monthly_Spending", nbins=30,
            title="Monthly Spending Distribution"
        )), use_container_width=True)
    with c2:
        if all(c in filtered for c in ["Avg_Monthly_Transactions","Avg_Monthly_Spending"]):
            st.plotly_chart(fig_clean(px.scatter(
                filtered, x="Avg_Monthly_Transactions", y="Avg_Monthly_Spending",
                color="Credit_Utilization", size="Credit_Limit" if "Credit_Limit" in filtered else None,
                title="Transactions vs Monthly Spending"
            )), use_container_width=True)

# ========================= FRAUD & COMPLIANCE ==================
with tabs[5]:
    st.markdown('<div class="section">🛡️ Fraud & Compliance Monitoring</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    fraud_count = int((filtered["Fraud_Flag"].astype(str).str.lower().isin(["1","yes","true","fraud"])).sum()) if "Fraud_Flag" in filtered else 0
    c1.metric("Fraud-Flagged", f"{fraud_count:,}")
    c2.metric("KYC Complete", f"{(filtered['KYC_Status'].astype(str).str.lower().isin(['complete','completed','yes','verified'])).sum():,}" if "KYC_Status" in filtered else "N/A")
    c3.metric("PAN Verified", f"{(filtered['PAN_Verified'].astype(str).str.lower().isin(['yes','true','verified','1'])).sum():,}" if "PAN_Verified" in filtered else "N/A")
    c4.metric("Customers Reviewed", f"{len(filtered):,}")

    c1,c2 = st.columns(2)
    with c1:
        if "Fraud_Flag" in filtered:
            fr = filtered["Fraud_Flag"].astype(str).value_counts().reset_index()
            fr.columns = ["Fraud Flag","Customers"]
            st.plotly_chart(fig_clean(px.pie(fr, names="Fraud Flag", values="Customers", hole=.55, title="Fraud Flag Distribution")), use_container_width=True)
    with c2:
        if "KYC_Status" in filtered:
            ky = filtered["KYC_Status"].astype(str).value_counts().reset_index()
            ky.columns = ["KYC Status","Customers"]
            st.plotly_chart(fig_clean(px.bar(ky, x="KYC Status", y="Customers", color="KYC Status", title="KYC Status")), use_container_width=True)

    if "Fraud_Flag" in filtered:
        fraud_customers = filtered[filtered["Fraud_Flag"].astype(str).str.lower().isin(["1","yes","true","fraud"])]
        if len(fraud_customers):
            st.warning(f"⚠️ {len(fraud_customers):,} selected customers are flagged for fraud based on the dataset's Fraud_Flag field.")
            st.dataframe(fraud_customers.head(100), hide_index=True, use_container_width=True)

# ========================= DATA ===============================
with tabs[6]:
    st.markdown('<div class="section">📋 Customer Data Explorer</div>', unsafe_allow_html=True)
    search = st.text_input("🔎 Search Customer ID", "")
    view = filtered.copy()
    if search and "Customer_ID" in view:
        view = view[view["Customer_ID"].astype(str).str.contains(search, case=False, na=False)]

    st.caption(f"{len(view):,} customers displayed")
    st.dataframe(view, hide_index=True, use_container_width=True, height=520)
    st.download_button(
        "⬇️ Download Filtered Customer Data",
        view.to_csv(index=False).encode("utf-8"),
        "finelite_filtered_customers.csv",
        "text/csv"
    )

# ----------------------------- FOOTER -------------------------
st.markdown("---")
st.caption("FinElite | Unified Customer Credit, Financial Behaviour, Risk, Default, Fraud & Compliance Analytics")
