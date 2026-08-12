import io
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# FINELITE | CREDIT RISK & LIMIT DECISIONING
# Unified product built from the project's three dashboards:
# - Risk Analytics & Decision Intelligence
# - Financial Performance Analysis
# - Customer financial / credit analysis
# ============================================================

st.set_page_config(
    page_title="FinElite | Credit Decisioning",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- THEME --------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: #090d14;
    color: #e8edf5;
}
.block-container {
    max-width: 1500px;
    padding: 1.2rem 2rem 2.5rem 2rem;
}
[data-testid="stSidebar"] {
    background: #0d121b;
    border-right: 1px solid #202938;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

.brand {
    padding: 8px 4px 18px 4px;
    border-bottom: 1px solid #202938;
    margin-bottom: 18px;
}
.brand-title {
    font-size: 25px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.7px;
}
.brand-title span { color: #38d9b2; }
.brand-sub { color:#8190a6; font-size:12px; margin-top:3px; }

.page-head {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding: 18px 22px;
    border:1px solid #202938;
    border-radius:16px;
    background: linear-gradient(135deg,#111927,#0d131e);
    margin-bottom:18px;
}
.page-title { font-size:28px; font-weight:800; color:#fff; margin:0; }
.page-sub { color:#8e9caf; margin-top:5px; font-size:13px; }
.status-pill {
    padding:7px 12px; border-radius:999px;
    background:#0e2d29; color:#45e0bb;
    border:1px solid #1c5b50; font-size:12px; font-weight:700;
}

.section-title {
    font-size:17px; font-weight:750; color:#fff;
    margin:20px 0 10px 0;
}
.section-note { color:#7f8da2; font-size:12px; margin-bottom:12px; }

.kpi {
    background:#111823;
    border:1px solid #202b3a;
    border-radius:14px;
    padding:15px 17px;
    min-height:105px;
    box-shadow:0 8px 22px rgba(0,0,0,.16);
}
.kpi-label { color:#8795a9; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.5px; }
.kpi-value { color:#f5f8fc; font-size:25px; font-weight:800; margin-top:8px; }
.kpi-help { color:#647286; font-size:10px; margin-top:5px; }

.panel {
    background:#111823;
    border:1px solid #202b3a;
    border-radius:15px;
    padding:16px;
    margin-bottom:14px;
}
.decision {
    border-radius:15px;
    padding:19px 21px;
    margin:8px 0 15px 0;
}
.approve { background:#0c2924; border:1px solid #1c6758; }
.review { background:#2a2110; border:1px solid #765a20; }
.reject { background:#2c1518; border:1px solid #71313a; }
.decision-title { font-size:23px; font-weight:800; color:#fff; }
.decision-sub { color:#a8b4c5; font-size:12px; margin-top:4px; }

.factor {
    padding:11px 13px;
    border-radius:10px;
    background:#0d141f;
    border:1px solid #202b3a;
    margin-bottom:8px;
    color:#c8d2df;
    font-size:12px;
}
.factor.good { border-left:4px solid #35d0ad; }
.factor.warn { border-left:4px solid #f0b84b; }
.factor.bad { border-left:4px solid #ef6674; }

.score-ring {
    text-align:center;
    padding:14px;
}
.score-number { font-size:42px; font-weight:850; color:#fff; line-height:1; }
.score-caption { color:#8795a9; font-size:11px; margin-top:5px; }

.tag {
    display:inline-block;
    padding:5px 9px;
    border-radius:999px;
    font-size:10px;
    font-weight:700;
    margin:2px;
}
.tag-green { background:#0d3029; color:#55e2c0; }
.tag-yellow { background:#33280f; color:#f3c85d; }
.tag-red { background:#36171c; color:#f37a86; }
.tag-blue { background:#13273c; color:#6eb8ff; }

[data-testid="stMetric"] {
    background:#111823;
    border:1px solid #202b3a;
    border-radius:13px;
    padding:12px;
}
[data-testid="stMetricLabel"] { color:#8491a4; }
[data-testid="stMetricValue"] { color:#f5f8fc; }

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background:#111823 !important;
    border-color:#2a3545 !important;
}
.stTextInput input, .stNumberInput input {
    background:#111823 !important;
    color:#f5f8fc !important;
}
.stButton > button {
    background:#173a35;
    border:1px solid #2d806f;
    color:#dffbf4;
    border-radius:9px;
    font-weight:700;
}
.stButton > button:hover { border-color:#49dfbe; color:#fff; }
div[role="radiogroup"] label { color:#b8c3d1 !important; }
.stDownloadButton > button {
    background:#172231; border:1px solid #304055; color:#dce5ef;
}
[data-testid="stDataFrame"] {
    border:1px solid #202b3a;
}
.small { color:#6f7d91; font-size:11px; }
.warning-box {
    background:#261f0e; border:1px solid #66521d;
    color:#ddca8b; padding:12px 14px; border-radius:10px;
}
.info-box {
    background:#101f2f; border:1px solid #254563;
    color:#a8c9e8; padding:12px 14px; border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------- DATA ---------------------------
NUMERIC = [
    "Age","Monthly_Income","Annual_Income","Credit_Score","Years_With_Bank",
    "Existing_Credit_Cards","Existing_Credit_Limit","Loan_Count","EMI_Per_Month",
    "Debt_To_Income_Ratio","Savings_Balance","Investment_Value",
    "Avg_Monthly_Transactions","Avg_Monthly_Spending","Credit_Utilization",
    "Credit_History_Years","Missed_Payments","Late_Payment_Count",
    "Number_of_Defaults","Credit_Limit","default_payment_next_month"
]

@st.cache_data
def load_data(file_bytes=None):
    if file_bytes:
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        candidates = [
            "Credir_Card_Bank.xlsx",
            "Credir_Card_Bank(4).xlsx",
            "Credit_Card_Bank.xlsx",
            "customer_data.xlsx",
            "../DataSets/Credir_Card_Bank.xlsx",
        ]
        path = next((x for x in candidates if os.path.exists(x)), None)
        if not path:
            raise FileNotFoundError("Upload the customer Excel dataset using the sidebar.")
        df = pd.read_excel(path)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_", regex=False)
    )

    for c in NUMERIC:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "Annual_Income" not in df.columns and "Monthly_Income" in df.columns:
        df["Annual_Income"] = df["Monthly_Income"] * 12

    # Credit category used in the original financial dashboard.
    if "Credit_Score" in df.columns:
        def credit_category(x):
            if pd.isna(x): return "Unknown"
            if x < 580: return "Poor"
            if x < 670: return "Fair"
            if x < 740: return "Good"
            if x < 800: return "Very Good"
            return "Excellent"
        df["Credit_Band"] = df["Credit_Score"].apply(credit_category)

    # Unified default target: support either project's naming convention.
    if "default_payment_next_month" in df.columns:
        df["Default_Flag"] = df["default_payment_next_month"].fillna(0).astype(int)
    elif "Number_of_Defaults" in df.columns:
        df["Default_Flag"] = (df["Number_of_Defaults"].fillna(0) > 0).astype(int)
    else:
        df["Default_Flag"] = 0

    # Original custom risk indicator from the financial dashboard.
    required = [
        "Debt_To_Income_Ratio","Credit_Utilization",
        "Missed_Payments","Late_Payment_Count","Number_of_Defaults"
    ]
    if all(c in df.columns for c in required):
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

    # Original high-risk rule from the risk dashboard.
    if all(c in df.columns for c in ["Credit_Score","Credit_Utilization","Missed_Payments"]):
        df["High_Risk_Flag"] = np.where(
            (df["Credit_Score"] < 600)
            | (df["Credit_Utilization"] > 75)
            | (df["Missed_Payments"] >= 3),
            "High Risk","Standard"
        )
    else:
        df["High_Risk_Flag"] = "Standard"

    if "Age" in df.columns:
        df["Age_Group"] = pd.cut(
            df["Age"], [18,25,35,50,65,100],
            labels=["18-25","26-35","36-50","51-65","65+"],
            include_lowest=True
        )

    return df

def money(v):
    if pd.isna(v): return "₹0"
    v = float(v)
    if abs(v) >= 1e7: return f"₹{v/1e7:.2f} Cr"
    if abs(v) >= 1e5: return f"₹{v/1e5:.2f} L"
    return f"₹{v:,.0f}"

def mean(df, col):
    return float(df[col].mean()) if col in df.columns and len(df) else 0.0

def chart(fig, height=340):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111823",
        plot_bgcolor="#111823",
        font=dict(color="#c6d0dd"),
        height=height,
        margin=dict(l=10,r=10,t=45,b=10),
        legend_title_text="",
    )
    return fig

# ------------------------- DECISION ENGINE --------------------
def credit_decision(row):
    """
    Explainable project-level decision engine.
    It uses the same risk variables present in the supplied dashboards.
    It is not a regulated credit score.
    """
    credit = float(row.get("Credit_Score", 0) or 0)
    util = float(row.get("Credit_Utilization", 0) or 0)
    dti = float(row.get("Debt_To_Income_Ratio", 0) or 0)
    missed = float(row.get("Missed_Payments", 0) or 0)
    late = float(row.get("Late_Payment_Count", 0) or 0)
    defaults = float(row.get("Number_of_Defaults", 0) or 0)
    income = float(row.get("Annual_Income", 0) or 0)
    existing = float(row.get("Existing_Credit_Limit", row.get("Credit_Limit", 0)) or 0)

    fraud = str(row.get("Fraud_Flag","")).lower()
    kyc = str(row.get("KYC_Status","")).lower()
    pan = str(row.get("PAN_Verified","")).lower()

    score = 0
    good, risks = [], []

    if credit >= 750:
        score += 25; good.append("Very strong credit score")
    elif credit >= 700:
        score += 20; good.append("Good credit score")
    elif credit >= 650:
        score += 12
    else:
        score += 3; risks.append("Credit score is below the preferred range")

    if util <= 30:
        score += 20; good.append("Low credit utilization")
    elif util <= 50:
        score += 14
    elif util <= 75:
        score += 7
    else:
        risks.append("Credit utilization is above 75%")

    if dti <= 25:
        score += 20; good.append("Healthy debt-to-income ratio")
    elif dti <= 35:
        score += 14
    elif dti <= 45:
        score += 7
    else:
        risks.append("High debt-to-income ratio")

    if missed == 0:
        score += 15; good.append("No missed payments")
    elif missed <= 2:
        score += 7
    else:
        risks.append("Frequent missed payments")

    if defaults == 0:
        score += 10; good.append("No recorded defaults")
    elif defaults == 1:
        score += 2
    else:
        risks.append("Multiple defaults")

    if late >= 4:
        risks.append("High late-payment count")

    compliance = (
        fraud in {"1","yes","true","fraud","flagged"}
        or kyc in {"failed","incomplete","pending","no"}
        or pan in {"no","false","0","unverified"}
    )
    if compliance:
        risks.append("Fraud/KYC/PAN verification needs review")

    if compliance or defaults >= 2 or (credit < 580 and util > 75):
        decision = "REJECT / ESCALATE"
        css = "reject"
    elif score >= 75 and defaults == 0 and util <= 75 and dti <= 45:
        decision = "APPROVE"
        css = "approve"
    else:
        decision = "MANUAL REVIEW"
        css = "review"

    # Income-based analytical exposure recommendation.
    monthly_income = income / 12 if income > 0 else 0
    base = monthly_income * 2.0
    multiplier = 1.20 if credit >= 750 else 1.00 if credit >= 700 else 0.75 if credit >= 650 else 0.50

    if dti > 45: multiplier *= .50
    elif dti > 35: multiplier *= .75

    if util > 75: multiplier *= .65
    elif util > 50: multiplier *= .85

    if defaults >= 2: multiplier *= .35
    elif defaults == 1: multiplier *= .70

    recommended = max(existing, base * multiplier)
    if income > 0:
        recommended = min(recommended, income * .50)
    recommended = max(existing, round(recommended / 5000) * 5000)

    if decision == "REJECT / ESCALATE":
        recommended = existing

    additional = max(0, recommended - existing)

    return {
        "score": min(100, round(score,1)),
        "decision": decision,
        "css": css,
        "recommended": recommended,
        "additional": additional,
        "good": good,
        "risks": risks,
    }

# ----------------------------- SIDEBAR ------------------------
uploaded = st.sidebar.file_uploader("Upload customer dataset", type=["xlsx","xls"])

try:
    df = load_data(uploaded.getvalue() if uploaded else None)
except Exception as e:
    st.markdown("""
    <div class="page-head">
        <div>
            <div class="page-title">💳 Fin<span>Elite</span></div>
            <div class="page-sub">Credit Risk & Limit Decisioning Platform</div>
        </div>
        <div class="status-pill">DATA REQUIRED</div>
    </div>
    """, unsafe_allow_html=True)
    st.error(str(e))
    st.info("Upload your customer Excel file from the left sidebar to start the application.")
    st.stop()

st.sidebar.markdown("""
<div class="brand">
<div class="brand-title">💳 Fin<span>Elite</span></div>
<div class="brand-sub">Credit Risk & Decision Intelligence</div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "WORKSPACE",
    [
        "Command Center",
        "Credit Application",
        "Limit Decisioning",
        "Customer 360",
        "Risk Monitoring",
        "Financial Behaviour",
        "Fraud & Compliance",
        "Customer Explorer",
    ],
    label_visibility="visible",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Portfolio Controls")

# Filters retained from the original risk dashboard.
risk_filter = st.sidebar.selectbox(
    "Risk Segment",
    ["All Customers","High Risk Only","Standard Risk Only"]
)

age_range = st.sidebar.slider(
    "Age Range",
    int(df["Age"].min()) if "Age" in df else 18,
    int(df["Age"].max()) if "Age" in df else 100,
    (
        int(df["Age"].min()) if "Age" in df else 18,
        int(df["Age"].max()) if "Age" in df else 100
    )
)

gender = "All Genders"
if "Gender" in df:
    gender = st.sidebar.selectbox("Gender", ["All Genders"] + sorted(df["Gender"].dropna().astype(str).unique().tolist()))

min_score = int(df["Credit_Score"].min()) if "Credit_Score" in df else 300
max_score = int(df["Credit_Score"].max()) if "Credit_Score" in df else 850
score_cutoff = st.sidebar.slider("Minimum Credit Score", min_score, max_score, min_score)

util_max = st.sidebar.slider("Maximum Credit Utilization", 0, 100, 100)

st.sidebar.markdown("### Compliance")
require_kyc = st.sidebar.checkbox("KYC Complete Only")
require_pan = st.sidebar.checkbox("PAN Verified Only")

filtered = df.copy()

if risk_filter == "High Risk Only":
    filtered = filtered[filtered["High_Risk_Flag"] == "High Risk"]
elif risk_filter == "Standard Risk Only":
    filtered = filtered[filtered["High_Risk_Flag"] == "Standard"]

if "Age" in filtered:
    filtered = filtered[filtered["Age"].between(age_range[0], age_range[1])]

if gender != "All Genders" and "Gender" in filtered:
    filtered = filtered[filtered["Gender"].astype(str) == gender]

if "Credit_Score" in filtered:
    filtered = filtered[filtered["Credit_Score"] >= score_cutoff]

if "Credit_Utilization" in filtered:
    filtered = filtered[filtered["Credit_Utilization"] <= util_max]

if require_kyc and "KYC_Status" in filtered:
    filtered = filtered[filtered["KYC_Status"].astype(str).str.lower() == "complete"]

if require_pan and "PAN_Verified" in filtered:
    filtered = filtered[filtered["PAN_Verified"].astype(str).str.lower().isin(["yes","true","1","verified"])]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** customers")

# --------------------- UNDERWRITER SIMULATOR ------------------
st.sidebar.markdown("### Underwriter Simulator")
sim_score = st.sidebar.slider("Applicant Credit Score", 300, 850, 700)
sim_util = st.sidebar.slider("Applicant Utilization", 0, 100, 40)
sim_missed = st.sidebar.slider("Applicant Missed Payments", 0, 10, 0)

sim_high = (sim_score < 600) or (sim_util > 75) or (sim_missed >= 3)
sim_risk_score = min(
    100,
    max(0, (850 - sim_score) * 0.4 + sim_util * 0.4 + sim_missed * 10)
)

if sim_high:
    st.sidebar.error(f"HIGH RISK\nScore: {sim_risk_score:.1f}/100")
else:
    st.sidebar.success(f"STANDARD RISK\nScore: {sim_risk_score:.1f}/100")

if filtered.empty:
    st.warning("No customers match the current filters. Adjust the controls in the sidebar.")
    st.stop()

# ---------------------------- HEADER --------------------------
st.markdown(f"""
<div class="page-head">
  <div>
    <div class="page-title">FinElite</div>
    <div class="page-sub">Credit Risk, Customer Intelligence & Limit Decisioning</div>
  </div>
  <div class="status-pill">● LIVE PORTFOLIO</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# COMMAND CENTER
# ============================================================
if page == "Command Center":
    st.markdown('<div class="section-title">Credit Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">A single view for portfolio health, credit exposure and immediate analyst actions.</div>', unsafe_allow_html=True)

    total = len(filtered)
    defaults = int(filtered["Default_Flag"].sum())
    default_rate = defaults / total * 100
    high = int((filtered["High_Risk_Flag"] == "High Risk").sum())
    higher = int((filtered["Risk_Level"].astype(str) == "Higher").sum())
    avg_score = mean(filtered,"Credit_Score")
    avg_util = mean(filtered,"Credit_Utilization")
    exposure = filtered["Credit_Limit"].sum() if "Credit_Limit" in filtered else 0

    cols = st.columns(6)
    metrics = [
        ("CUSTOMERS", f"{total:,}", "Filtered portfolio"),
        ("AVG CREDIT SCORE", f"{avg_score:,.0f}", "Portfolio average"),
        ("DEFAULT RATE", f"{default_rate:.2f}%", f"{defaults:,} defaulters"),
        ("HIGH RISK", f"{high:,}", "Early-warning rule"),
        ("HIGHER RISK", f"{higher:,}", "Custom risk indicator"),
        ("CREDIT EXPOSURE", money(exposure), "Current portfolio"),
    ]
    for col,(lab,val,help_) in zip(cols,metrics):
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{lab}</div><div class="kpi-value">{val}</div><div class="kpi-help">{help_}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Today\'s Credit Action Queue</div>', unsafe_allow_html=True)
    queue = []
    id_col = "Customer_ID" if "Customer_ID" in filtered else filtered.columns[0]
    for _, row in filtered.iterrows():
        r = credit_decision(row)
        queue.append({
            "Customer": str(row[id_col]),
            "Decision": r["decision"],
            "Risk Score": r["score"],
            "Credit Score": row.get("Credit_Score",np.nan),
            "Utilization": row.get("Credit_Utilization",np.nan),
            "DTI": row.get("Debt_To_Income_Ratio",np.nan),
            "Recommended Limit": r["recommended"],
        })
    queue_df = pd.DataFrame(queue)
    priority = queue_df[queue_df["Decision"] != "REJECT / ESCALATE"].sort_values("Risk Score", ascending=False).head(12)

    st.dataframe(priority, hide_index=True, use_container_width=True)

    c1,c2,c3 = st.columns(3)
    with c1:
        risk = filtered["Risk_Level"].astype(str).value_counts().reset_index()
        risk.columns = ["Risk","Customers"]
        st.plotly_chart(chart(px.pie(risk,names="Risk",values="Customers",hole=.58,title="Portfolio Risk Mix"),300),use_container_width=True)
    with c2:
        if "Credit_Score" in filtered:
            st.plotly_chart(chart(px.histogram(filtered,x="Credit_Score",color="Risk_Level",nbins=28,title="Credit Score Distribution"),300),use_container_width=True)
    with c3:
        d = filtered["Default_Flag"].map({0:"Non-Defaulter",1:"Defaulter"}).value_counts().reset_index()
        d.columns = ["Status","Customers"]
        st.plotly_chart(chart(px.bar(d,x="Status",y="Customers",title="Default Portfolio"),300),use_container_width=True)

    st.markdown('<div class="section-title">Portfolio Signals</div>', unsafe_allow_html=True)
    s1,s2,s3 = st.columns(3)
    with s1:
        st.markdown(f'<div class="factor good">Average credit score: <b>{avg_score:,.0f}</b></div>',unsafe_allow_html=True)
    with s2:
        cls = "bad" if avg_util > 50 else "warn" if avg_util > 30 else "good"
        st.markdown(f'<div class="factor {cls}">Average utilization: <b>{avg_util:.1f}%</b></div>',unsafe_allow_html=True)
    with s3:
        dti = mean(filtered,"Debt_To_Income_Ratio")
        cls = "bad" if dti > 45 else "warn" if dti > 35 else "good"
        st.markdown(f'<div class="factor {cls}">Average DTI: <b>{dti:.2f}</b></div>',unsafe_allow_html=True)

# ============================================================
# CREDIT APPLICATION
# ============================================================
elif page == "Credit Application":
    st.markdown('<div class="section-title">Credit Application</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Select an existing customer and assess eligibility, risk and suggested exposure.</div>', unsafe_allow_html=True)

    id_col = "Customer_ID" if "Customer_ID" in filtered else filtered.columns[0]
    ids = filtered[id_col].astype(str).tolist()
    selected = st.selectbox("Applicant / Customer ID", ids)
    row = filtered[filtered[id_col].astype(str) == selected].iloc[0]
    result = credit_decision(row)

    css = result["css"]
    icon = "✓" if css == "approve" else "!" if css == "review" else "×"
    st.markdown(f"""
    <div class="decision {css}">
      <div class="decision-title">{icon} {result["decision"]}</div>
      <div class="decision-sub">Explainable analytical risk score: <b>{result["score"]}/100</b></div>
    </div>
    """,unsafe_allow_html=True)

    a,b,c,d = st.columns(4)
    a.metric("Credit Score", f'{row.get("Credit_Score",0):,.0f}')
    b.metric("Annual Income", money(row.get("Annual_Income",0)))
    c.metric("Current Limit", money(row.get("Existing_Credit_Limit",row.get("Credit_Limit",0))))
    d.metric("Recommended Limit", money(result["recommended"]))

    st.markdown('<div class="section-title">Why this decision?</div>',unsafe_allow_html=True)
    left,right = st.columns(2)
    with left:
        st.markdown("#### Positive signals")
        for x in result["good"] or ["No strong positive signal identified."]:
            st.markdown(f'<div class="factor good">✓ {x}</div>',unsafe_allow_html=True)
    with right:
        st.markdown("#### Risk signals")
        for x in result["risks"] or ["No major risk signal identified."]:
            st.markdown(f'<div class="factor warn">! {x}</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-title">Applicant Snapshot</div>',unsafe_allow_html=True)
    snap = {}
    for label,col in [
        ("Age","Age"),("Employment","Employment_Type"),("Occupation","Occupation"),
        ("Credit Band","Credit_Band"),("Utilization","Credit_Utilization"),
        ("DTI","Debt_To_Income_Ratio"),("Loans","Loan_Count"),
        ("EMI","EMI_Per_Month"),("Missed Payments","Missed_Payments"),
        ("Defaults","Number_of_Defaults"),("KYC","KYC_Status"),
        ("PAN","PAN_Verified"),("Fraud Flag","Fraud_Flag")
    ]:
        if col in row.index:
            snap[label] = row[col]
    st.dataframe(pd.DataFrame(list(snap.items()),columns=["Factor","Value"]),hide_index=True,use_container_width=True)

    st.markdown('<div class="warning-box">This recommendation is for your project\'s analytical demonstration. A real credit decision requires validated underwriting policy, regulatory checks and human oversight.</div>',unsafe_allow_html=True)

# ============================================================
# LIMIT DECISIONING
# ============================================================
elif page == "Limit Decisioning":
    st.markdown('<div class="section-title">Limit Decisioning Workbench</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Identify customers who appear suitable for additional exposure under the project rules.</div>', unsafe_allow_html=True)

    id_col = "Customer_ID" if "Customer_ID" in filtered else filtered.columns[0]
    records = []
    for _, row in filtered.iterrows():
        r = credit_decision(row)
        records.append({
            "Customer": str(row[id_col]),
            "Decision": r["decision"],
            "Risk Score": r["score"],
            "Credit Score": row.get("Credit_Score",np.nan),
            "DTI": row.get("Debt_To_Income_Ratio",np.nan),
            "Utilization": row.get("Credit_Utilization",np.nan),
            "Defaults": row.get("Number_of_Defaults",np.nan),
            "Current Limit": row.get("Existing_Credit_Limit",row.get("Credit_Limit",np.nan)),
            "Recommended Limit": r["recommended"],
            "Additional Headroom": r["additional"],
        })
    rec = pd.DataFrame(records)

    a,b,c,d = st.columns(4)
    a.metric("Approve", int((rec["Decision"]=="APPROVE").sum()))
    b.metric("Manual Review", int((rec["Decision"]=="MANUAL REVIEW").sum()))
    c.metric("Reject / Escalate", int((rec["Decision"]=="REJECT / ESCALATE").sum()))
    d.metric("Potential New Exposure", money(rec["Additional Headroom"].sum()))

    view = st.selectbox("Decision queue",["Approved for additional limit","Manual review","All customers"])
    if view == "Approved for additional limit":
        table = rec[rec["Decision"]=="APPROVE"]
    elif view == "Manual review":
        table = rec[rec["Decision"]=="MANUAL REVIEW"]
    else:
        table = rec
    table = table.sort_values(["Risk Score","Credit Score"],ascending=False)

    st.dataframe(table.head(150),hide_index=True,use_container_width=True)
    st.download_button(
        "Download decision report",
        rec.to_csv(index=False).encode(),
        "FinElite_Credit_Decision_Report.csv",
        "text/csv"
    )

    st.markdown('<div class="info-box"><b>Limit logic:</b> income capacity is used as a base; credit score, DTI, utilization and repayment history adjust the recommended exposure. Existing exposure is respected.</div>',unsafe_allow_html=True)

# ============================================================
# CUSTOMER 360
# ============================================================
elif page == "Customer 360":
    st.markdown('<div class="section-title">Customer 360</div>', unsafe_allow_html=True)
    id_col = "Customer_ID" if "Customer_ID" in filtered else filtered.columns[0]
    selected = st.selectbox("Search customer", filtered[id_col].astype(str).tolist(), key="c360")
    row = filtered[filtered[id_col].astype(str)==selected].iloc[0]
    r = credit_decision(row)

    st.markdown(f'<div class="panel"><span class="tag tag-blue">CUSTOMER</span><b>{selected}</b> &nbsp; <span class="tag {"tag-green" if r["decision"]=="APPROVE" else "tag-yellow" if r["decision"]=="MANUAL REVIEW" else "tag-red"}">{r["decision"]}</span></div>',unsafe_allow_html=True)

    a,b,c,d,e = st.columns(5)
    a.metric("Credit Score",f'{row.get("Credit_Score",0):,.0f}')
    b.metric("Risk Score",f'{r["score"]}/100')
    c.metric("Utilization",f'{row.get("Credit_Utilization",0):.1f}%')
    d.metric("DTI",f'{row.get("Debt_To_Income_Ratio",0):.2f}')
    e.metric("Recommended Limit",money(r["recommended"]))

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="panel"><b>Personal Profile</b>',unsafe_allow_html=True)
        fields=["Age","Gender","Employment_Type","Occupation","Residential_Status","Years_With_Bank"]
        st.dataframe(pd.DataFrame({"Metric":[x.replace("_"," ") for x in fields if x in row.index],"Value":[row[x] for x in fields if x in row.index]}),hide_index=True,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><b>Credit & Loans</b>',unsafe_allow_html=True)
        fields=["Credit_Score","Credit_Band","Credit_Limit","Existing_Credit_Limit","Existing_Credit_Cards","Loan_Count","EMI_Per_Month"]
        st.dataframe(pd.DataFrame({"Metric":[x.replace("_"," ") for x in fields if x in row.index],"Value":[row[x] for x in fields if x in row.index]}),hide_index=True,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="panel"><b>Repayment & Compliance</b>',unsafe_allow_html=True)
        fields=["Missed_Payments","Late_Payment_Count","Number_of_Defaults","KYC_Status","PAN_Verified","Fraud_Flag"]
        st.dataframe(pd.DataFrame({"Metric":[x.replace("_"," ") for x in fields if x in row.index],"Value":[row[x] for x in fields if x in row.index]}),hide_index=True,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-title">Financial Position</div>',unsafe_allow_html=True)
    metrics=[x for x in ["Savings_Balance","Investment_Value","Avg_Monthly_Spending","EMI_Per_Month"] if x in row.index]
    if metrics:
        p=pd.DataFrame({"Metric":[x.replace("_"," ") for x in metrics],"Value":[float(row[x]) for x in metrics]})
        st.plotly_chart(chart(px.bar(p,x="Metric",y="Value",title="Customer Financial Indicators"),320),use_container_width=True)

# ============================================================
# RISK MONITORING
# ============================================================
elif page == "Risk Monitoring":
    st.markdown('<div class="section-title">Risk Monitoring & Early Warning</div>',unsafe_allow_html=True)

    high = int((filtered["High_Risk_Flag"]=="High Risk").sum())
    moderate = int((filtered["Risk_Level"].astype(str)=="Moderate").sum())
    defaults = int(filtered["Default_Flag"].sum())
    missed = int(filtered["Missed_Payments"].sum()) if "Missed_Payments" in filtered else 0

    a,b,c,d = st.columns(4)
    a.metric("High Risk",f"{high:,}")
    b.metric("Moderate Risk",f"{moderate:,}")
    c.metric("Defaulters",f"{defaults:,}")
    d.metric("Missed Payments",f"{missed:,}")

    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart(px.histogram(filtered,x="Credit_Utilization",color="Risk_Level",nbins=30,title="Credit Utilization Distribution"),340),use_container_width=True)
    with c2:
        st.plotly_chart(chart(px.scatter(filtered,x="Debt_To_Income_Ratio",y="Credit_Score",color="Risk_Level",size="Credit_Limit" if "Credit_Limit" in filtered else None,hover_data=["Customer_ID"] if "Customer_ID" in filtered else None,title="DTI vs Credit Score"),340),use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        if "Age_Group" in filtered:
            age_risk=filtered.groupby("Age_Group",observed=False)["Default_Flag"].mean().mul(100).reset_index(name="Default Rate")
            st.plotly_chart(chart(px.bar(age_risk,x="Age_Group",y="Default Rate",title="Default Rate by Age Group"),320),use_container_width=True)
    with c2:
        if "Occupation" in filtered:
            occ=filtered.groupby("Occupation")["Default_Flag"].mean().mul(100).sort_values(ascending=False).reset_index(name="Default Rate")
            st.plotly_chart(chart(px.bar(occ,y="Occupation",x="Default Rate",orientation="h",title="Default Rate by Occupation"),320),use_container_width=True)

    st.markdown('<div class="section-title">Highest Priority Customers</div>',unsafe_allow_html=True)
    cols=[c for c in ["Customer_ID","Credit_Score","Credit_Utilization","Debt_To_Income_Ratio","Missed_Payments","Late_Payment_Count","Number_of_Defaults","Risk_Indicator","Risk_Level","High_Risk_Flag"] if c in filtered]
    st.dataframe(filtered.sort_values("Risk_Indicator",ascending=False)[cols].head(50),hide_index=True,use_container_width=True)

# ============================================================
# FINANCIAL BEHAVIOUR
# ============================================================
elif page == "Financial Behaviour":
    st.markdown('<div class="section-title">Financial Behaviour</div>',unsafe_allow_html=True)
    metric_map={
        "Savings Balance":"Savings_Balance",
        "Investment Value":"Investment_Value",
        "Monthly Spending":"Avg_Monthly_Spending",
        "Monthly EMI":"EMI_Per_Month",
    }
    selected_metric=st.selectbox("Financial metric",list(metric_map))
    metric=metric_map[selected_metric]

    c1,c2=st.columns(2)
    with c1:
        if metric in filtered and "Annual_Income" in filtered:
            st.plotly_chart(chart(px.scatter(filtered,x="Annual_Income",y=metric,color="Employment_Type" if "Employment_Type" in filtered else None,hover_data=["Customer_ID"] if "Customer_ID" in filtered else None,title=f"Income vs {selected_metric}"),340),use_container_width=True)
    with c2:
        if metric in filtered and "Occupation" in filtered:
            x=filtered.groupby("Occupation")[metric].mean().sort_values(ascending=False).head(10).reset_index()
            st.plotly_chart(chart(px.bar(x,x=metric,y="Occupation",orientation="h",title=f"Top Occupations by {selected_metric}"),340),use_container_width=True)

    c1,c2=st.columns(2)
    with c1:
        if "Avg_Monthly_Transactions" in filtered and "Avg_Monthly_Spending" in filtered:
            st.plotly_chart(chart(px.scatter(filtered,x="Avg_Monthly_Transactions",y="Avg_Monthly_Spending",color="Credit_Utilization",size="Credit_Limit" if "Credit_Limit" in filtered else None,title="Transactions vs Spending"),340),use_container_width=True)
    with c2:
        if "EMI_Per_Month" in filtered:
            st.plotly_chart(chart(px.histogram(filtered,x="EMI_Per_Month",nbins=30,title="Monthly EMI Distribution"),340),use_container_width=True)

# ============================================================
# FRAUD & COMPLIANCE
# ============================================================
elif page == "Fraud & Compliance":
    st.markdown('<div class="section-title">Fraud & Compliance</div>',unsafe_allow_html=True)

    fraud_mask = filtered["Fraud_Flag"].astype(str).str.lower().isin(["1","yes","true","fraud","flagged"]) if "Fraud_Flag" in filtered else pd.Series(False,index=filtered.index)
    kyc_mask = filtered["KYC_Status"].astype(str).str.lower().isin(["complete","completed","verified","yes"]) if "KYC_Status" in filtered else pd.Series(False,index=filtered.index)
    pan_mask = filtered["PAN_Verified"].astype(str).str.lower().isin(["yes","true","verified","1"]) if "PAN_Verified" in filtered else pd.Series(False,index=filtered.index)

    a,b,c,d=st.columns(4)
    a.metric("Fraud Flagged",int(fraud_mask.sum()))
    b.metric("KYC Complete",int(kyc_mask.sum()))
    c.metric("PAN Verified",int(pan_mask.sum()))
    d.metric("Customers Reviewed",len(filtered))

    c1,c2=st.columns(2)
    with c1:
        if "Fraud_Flag" in filtered:
            x=filtered["Fraud_Flag"].astype(str).value_counts().reset_index()
            x.columns=["Fraud Flag","Customers"]
            st.plotly_chart(chart(px.pie(x,names="Fraud Flag",values="Customers",hole=.55,title="Fraud Flag Distribution"),320),use_container_width=True)
    with c2:
        if "KYC_Status" in filtered:
            x=filtered["KYC_Status"].astype(str).value_counts().reset_index()
            x.columns=["KYC Status","Customers"]
            st.plotly_chart(chart(px.bar(x,x="KYC Status",y="Customers",title="KYC Status"),320),use_container_width=True)

    if fraud_mask.any():
        st.markdown('<div class="warning-box">Fraud-flagged customers are separated for review. Do not automatically approve additional exposure for these records.</div>',unsafe_allow_html=True)
        st.dataframe(filtered[fraud_mask].head(100),hide_index=True,use_container_width=True)

# ============================================================
# CUSTOMER EXPLORER
# ============================================================
elif page == "Customer Explorer":
    st.markdown('<div class="section-title">Customer Explorer</div>',unsafe_allow_html=True)
    search=st.text_input("Search Customer ID")
    view=filtered.copy()
    if search and "Customer_ID" in view:
        view=view[view["Customer_ID"].astype(str).str.contains(search,case=False,na=False)]

    st.caption(f"{len(view):,} customers")
    st.dataframe(view,hide_index=True,use_container_width=True,height=560)
    st.download_button(
        "Download filtered customer data",
        view.to_csv(index=False).encode(),
        "FinElite_Filtered_Customers.csv",
        "text/csv"
    )

# ----------------------------- FOOTER -------------------------
st.markdown("---")
st.markdown(
    '<div class="small">FinElite • Credit Risk & Decision Intelligence • Built with Streamlit, Pandas, NumPy & Plotly</div>',
    unsafe_allow_html=True
)
