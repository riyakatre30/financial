import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Financial Performance Analysis",
    page_icon="💰",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("💰 Financial Performance Analysis")
st.write(
    "Interactive analysis of Income, Savings, Investments, EMI, "
    "Debt, Credit Utilization, Credit Limit and Loan Portfolio."
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_excel("Credir_Card_Bank.xlsx")

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

st.sidebar.header("🔎 Filters")

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
# KPI CARDS
# ==================================================

st.subheader("📌 Financial KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Customers",
    filtered_df["Customer_ID"].nunique()
)

col2.metric(
    "Avg Monthly Income",
    f"₹{filtered_df['Monthly_Income'].mean():,.0f}"
)

col3.metric(
    "Avg Savings",
    f"₹{filtered_df['Savings_Balance'].mean():,.0f}"
)

col4.metric(
    "Avg Investment",
    f"₹{filtered_df['Investment_Value'].mean():,.0f}"
)

col5.metric(
    "Avg EMI",
    f"₹{filtered_df['EMI_Per_Month'].mean():,.0f}"
)


col6, col7, col8, col9, col10 = st.columns(5)

col6.metric(
    "Avg DTI",
    f"{filtered_df['Debt_To_Income_Ratio'].mean():.2f}"
)

col7.metric(
    "Avg Credit Utilization",
    f"{filtered_df['Credit_Utilization'].mean():.2f}%"
)

col8.metric(
    "Avg Credit Score",
    f"{filtered_df['Credit_Score'].mean():.0f}"
)

col9.metric(
    "Avg Credit Limit",
    f"₹{filtered_df['Existing_Credit_Limit'].mean():,.0f}"
)

col10.metric(
    "Avg Loan Count",
    f"{filtered_df['Loan_Count'].mean():.2f}"
)


# ==================================================
# 1. INCOME VS SAVINGS
# ==================================================

st.header("1️⃣ Income vs Savings Analysis")

col1, col2 = st.columns(2)

with col1:

    fig, ax = plt.subplots(figsize=(8, 5))

    sb.scatterplot(
        x="Monthly_Income",
        y="Savings_Balance",
        data=filtered_df,
        color="pink",
        ax=ax
    )

    ax.set_title("Income vs Savings")
    ax.set_xlabel("Monthly Income")
    ax.set_ylabel("Savings Balance")

    st.pyplot(fig)


with col2:

    savings_emp = (
        filtered_df
        .groupby("Employment_Type")
        [["Annual_Income", "Savings_Balance"]]
        .mean()
        .round(2)
    )

    st.write("### Employment-wise Income & Savings")

    st.dataframe(
        savings_emp,
        use_container_width=True
    )


# ==================================================
# 2. INCOME VS INVESTMENTS
# ==================================================

st.header("2️⃣ Income vs Investments")

col1, col2 = st.columns(2)

with col1:

    fig, ax = plt.subplots(figsize=(8, 5))

    sb.scatterplot(
        x="Monthly_Income",
        y="Investment_Value",
        data=filtered_df,
        color="green",
        ax=ax
    )

    ax.set_title("Income vs Investments")
    ax.set_xlabel("Monthly Income")
    ax.set_ylabel("Investment Value")

    st.pyplot(fig)


with col2:

    occupation_investment = (
        filtered_df
        .groupby("Occupation")
        [["Annual_Income", "Investment_Value"]]
        .mean()
        .round(2)
        .sort_values(
            by="Annual_Income",
            ascending=False
        )
        .head(10)
    )

    st.write("### Top Occupations")

    st.dataframe(
        occupation_investment,
        use_container_width=True
    )


# ==================================================
# 3. EMI ANALYSIS
# ==================================================

st.header("3️⃣ EMI Analysis")

col1, col2 = st.columns(2)

with col1:

    fig, ax = plt.subplots(figsize=(8, 5))

    sb.histplot(
        filtered_df["EMI_Per_Month"],
        bins=30,
        kde=True,
        color="#4C72B0",
        ax=ax
    )

    ax.set_title("Monthly EMI Distribution")
    ax.set_xlabel("EMI Per Month")

    st.pyplot(fig)


with col2:

    emi_emp = (
        filtered_df
        .groupby("Employment_Type")["EMI_Per_Month"]
        .mean()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    emi_emp.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title("Average EMI by Employment Type")
    ax.set_xlabel("Employment Type")
    ax.set_ylabel("Average EMI")

    plt.xticks(rotation=45)

    st.pyplot(fig)


# ==================================================
# 4. DEBT TO INCOME ANALYSIS
# ==================================================

st.header("4️⃣ Debt-to-Income Analysis")

col1, col2 = st.columns(2)

with col1:

    fig, ax = plt.subplots(figsize=(8, 5))

    sb.boxplot(
        y=filtered_df["Debt_To_Income_Ratio"],
        color="orchid",
        ax=ax
    )

    ax.set_title("Debt to Income Ratio")

    st.pyplot(fig)


with col2:

    dti_emp = (
        filtered_df
        .groupby("Employment_Type")
        ["Debt_To_Income_Ratio"]
        .mean()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    dti_emp.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title("Average DTI by Employment Type")
    ax.set_xlabel("Employment Type")
    ax.set_ylabel("Debt to Income Ratio")

    plt.xticks(rotation=45)

    st.pyplot(fig)


# ==================================================
# 5. CREDIT UTILIZATION
# ==================================================

st.header("5️⃣ Credit Utilization Analysis")

col1, col2 = st.columns(2)

with col1:

    fig, ax = plt.subplots(figsize=(8, 5))

    sb.histplot(
        filtered_df["Credit_Utilization"],
        bins=20,
        kde=True,
        color="#F28E2B",
        ax=ax
    )

    ax.set_title("Credit Utilization")
    ax.set_xlabel("Credit Utilization (%)")

    st.pyplot(fig)


with col2:

    occupation_credit = (
        filtered_df
        .groupby("Occupation")
        ["Credit_Utilization"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    occupation_credit.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title("Credit Utilization by Occupation")
    ax.set_xlabel("Occupation")
    ax.set_ylabel("Average Credit Utilization")

    plt.xticks(rotation=45)

    st.pyplot(fig)


# ==================================================
# 6. EXISTING CREDIT LIMIT
# ==================================================

st.header("6️⃣ Existing Credit Limit Analysis")

col1, col2 = st.columns(2)

with col1:

    fig, ax = plt.subplots(figsize=(8, 5))

    sb.histplot(
        filtered_df["Existing_Credit_Limit"],
        bins=30,
        color="plum",
        ax=ax
    )

    ax.set_title("Existing Credit Limit")
    ax.set_xlabel("Existing Credit Limit")

    st.pyplot(fig)


with col2:

    credit_emp = (
        filtered_df
        .groupby("Employment_Type")
        ["Existing_Credit_Limit"]
        .mean()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    credit_emp.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title("Average Credit Limit by Employment Type")
    ax.set_xlabel("Employment Type")
    ax.set_ylabel("Average Credit Limit")

    plt.xticks(rotation=45)

    st.pyplot(fig)


# ==================================================
# 7. LOAN PORTFOLIO
# ==================================================

st.header("7️⃣ Loan Portfolio Analysis")

col1, col2 = st.columns(2)

with col1:

    fig, ax = plt.subplots(figsize=(8, 5))

    sb.countplot(
        data=filtered_df,
        x="Loan_Count",
        ax=ax
    )

    ax.set_title("Loan Portfolio")
    ax.set_xlabel("Number of Loans")
    ax.set_ylabel("Number of Customers")

    st.pyplot(fig)


with col2:

    loan_analysis = (
        filtered_df
        .groupby("Loan_Count")
        [["Annual_Income", "Credit_Score"]]
        .mean()
        .round(2)
    )

    st.write("### Loan Count vs Financial Profile")

    st.dataframe(
        loan_analysis,
        use_container_width=True
    )


# ==================================================
# CORRELATION ANALYSIS
# ==================================================

st.header("📊 Financial Correlation Analysis")

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

fig, ax = plt.subplots(figsize=(14, 8))

sb.heatmap(
    filtered_df[corr_columns].corr(),
    annot=True,
    cmap="viridis",
    fmt=".2f",
    ax=ax
)

ax.set_title("Financial Correlation Matrix")

st.pyplot(fig)


# ==================================================
# KPI REPORT
# ==================================================

st.header("📋 Financial Performance Report")

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

st.header("⬇️ Download Analysis Data")

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="financial_analysis.csv",
    mime="text/csv"
)
