import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#Page config
st.set_page_config(page_title="Car Insurance Analysis Dasboard", layout="wide")

#Title
st.title("Car Insurance Analysis Dasboard")

#Load data
df = pd.read_csv("carInsurance_data.csv")

def init_filter_state(df):
    if "marital" not in st.session_state:
        st.session_state["marital"] = sorted(df["Marital"].dropna().unique().tolist())

    if "education" not in st.session_state:
        st.session_state["education"] = df["Education"].unique().tolist()

    if "communication" not in st.session_state:
        st.session_state["communication"] = df["Communication"].unique().tolist()

    month_order = ["jan","feb","mar","apr","may","jun",
                   "jul","aug","sep","oct","nov","dec"]
    month_options = [m for m in month_order if m in df["LastContactMonth"].unique()]

    if "months" not in st.session_state:
        st.session_state["months"] = month_options

    if "age_range" not in st.session_state:
        st.session_state["age_range"] = (
            int(df["Age"].min()),
            int(df["Age"].max())
        )

init_filter_state(df)

def sidebar_filters(df):
    st.sidebar.header("🔎 Filter Data")

    def reset_filters():
        st.session_state.clear()
        st.rerun()

    def clear_all_filters():
        st.session_state["marital"] = []
        st.session_state["education"] = []
        st.session_state["communication"]  = []
        st.session_state["months"] = []
        st.rerun()
        
    # Reset button
    if st.sidebar.button("🔄 Reset", use_container_width=True):
        reset_filters()

    # Clear button
    if st.sidebar.button("❌ CLear All", use_container_width=True):
        clear_all_filters()

    # Age filter
    min_age, max_age = st.sidebar.slider(
        "Select Age Range",
        int(df["Age"].min()),
        int(df["Age"].max()),
        (
            st.session_state.get("min_age", int(df["Age"].min())),
            st.session_state.get("max_age", int(df["Age"].max()))
        ),
        key="age_slider"
    )

    # Marital Status
    marital_options = sorted(df["Marital"].dropna().unique().tolist())
    selected_marital = st.sidebar.multiselect(
        "Marital Status",
        marital_options,
        default=marital_options,
        key="marital"
    )

    # Education
    education_options = df["Education"].unique().tolist()
    selected_education = st.sidebar.multiselect(
        "Education Level",
        education_options,
        default=education_options,
        key="education"
    )

    # Communication
    communication_options = df["Communication"].unique().tolist()
    selected_communication = st.sidebar.multiselect(
        "Communication Type",
        communication_options,
        default=communication_options,
        key="communication"
    )

    # Month sorting
    month_order = ["jan","feb","mar","apr","may","jun",
                   "jul","aug","sep","oct","nov","dec"]

    month_options = [m for m in month_order if m in df["LastContactMonth"].unique()]
    selected_months = st.sidebar.multiselect(
        "Months",
        month_options,
        default=month_options,
        key="months"
    )

    return min_age, max_age, selected_marital, selected_education, selected_communication, selected_months

    
(
    min_age,
    max_age,
    selected_marital,
    selected_education,
    selected_communication,
    selected_months
) = sidebar_filters(df)

filtered_df = df[
    (df["Age"] >= min_age) &
    (df["Age"] <= max_age) &
    (df["Marital"].isin(selected_marital)) &
    (df["Education"].isin(selected_education)) &
    (df["Communication"].isin(selected_communication)) &
    (df["LastContactMonth"].isin(selected_months))
]

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

#KPI
left, right = st.columns([0.25, 2])

#Call Duration
filtered_df["CallStart"] = pd.to_datetime(df["CallStart"])
filtered_df["CallEnd"] = pd.to_datetime(df["CallEnd"])
filtered_df["CallDuration"] = (filtered_df["CallEnd"]-filtered_df["CallStart"]).dt.total_seconds()

total_customers = len(filtered_df)
total_conversions = filtered_df["CarInsurance"].sum()
conversion_rate = (total_conversions/total_customers)*100

repeat_customers = filtered_df[filtered_df["NoOfContacts"] > 1].shape[0]
total_customers = filtered_df.shape[0]
repeat_contact_rate = (repeat_customers / total_customers) * 100

avg_call_duration = filtered_df["CallDuration"].mean()
avg_contacts = filtered_df["NoOfContacts"].mean()
avg_age = filtered_df["Age"].mean()
Best_Channel = filtered_df["Communication"].mode()[0]

with left:
    st.metric("Total Customers", total_customers)
    st.metric("Total Conversions", total_conversions)
    st.metric("Conversion Rate%", f"{conversion_rate:.2f}")
    st.metric("Avg Call Duaration(sec)", f"{avg_call_duration:.0f}")
    st.metric("Avg Age", f"{avg_age:.1f}")
    st.metric("Repeat Contact Rate (%)", f"{repeat_contact_rate:.2f}%")
    st.metric("Best Perforimg Channel", Best_Channel)

channel_kpi = (
    df.groupby("Communication")["CarInsurance"]
    .mean() * 100
)

prev_kpi = df.groupby("Outcome")["CarInsurance"].mean() * 100

filtered_df["Duration_Bucket"] = pd.cut(
    filtered_df["CallDuration"],
    bins=[0,60,180,300,600,2000],
    labels=["<1 min","1-3 min","3-5 min","5-10 min","10+ min"]
)

conv_duration = filtered_df.groupby("Duration_Bucket")["CarInsurance"].mean()*100

filtered_df["Age_Group"] = pd.cut(
    filtered_df["Age"],
    bins=[18,25,35,45,60,100],
    labels=["18-25","26-35","36-45","46-60","60+"]
)

conv_age = filtered_df.groupby("Age_Group")["CarInsurance"].mean()*100

conv_contacts = filtered_df.groupby("NoOfContacts")["CarInsurance"].mean()*100

job_kpi = (
    df.groupby("Job")["CarInsurance"]
    .mean() * 100
)

with right:
    col11, col12, col13, col14 = st.columns(4)
    with col11:
        st.subheader("📞 Conversion Rate by Call Duration")
        st.bar_chart(conv_duration)
    
    with col12:
        st.subheader("Conversion Rate by Age Group")
        st.bar_chart(conv_age)
    
    with col13:
        st.subheader(" Conversion Rate by Communication Channel")
        st.bar_chart(channel_kpi)
    
    with col14:
        st.subheader("🔁 Conversion Rate by Previous Outcome")
        st.bar_chart(prev_kpi)
    
    col21, col22, col23, col24 = st.columns(4)
    with col21:
        st.subheader("Conversion Rate by Number of Contacts")
        st.line_chart(conv_contacts)

    with col22:
        st.subheader(" Conversion Rate by Job Category")
        st.bar_chart(job_kpi)
    
    with col23:
        fig, ax = plt.subplots()
        sns.boxplot(
            x="CarInsurance",
            y="Balance",
            data=filtered_df,
            ax=ax)
        ax.set_xticklabels(["No","Yes"])
        ax.set_title("Balance Distribution by Purchase Outcome")
        st.pyplot(fig)
    
    with col24:
        fig, ax = plt.subplots()
        sns.scatterplot(
            x="Age",
            y="Balance",
            hue="CarInsurance",
            data=filtered_df,
            ax=ax
        )
        ax.legend(title="Converted", labels=["No","Yes"])
        ax.set_title("Age vs Balance (Buyers vs Non-Buyers)")
        st.pyplot(fig)



# month_order = ["jan","feb","mar","apr","may","jun",
#                "jul","aug","sep","oct","nov","dec"]

# df["LastContactMonth"] = pd.Categorical(
#     df["LastContactMonth"],
#     categories=month_order,
#     ordered=True
# )

# month_kpi = df.groupby("LastContactMonth")["CarInsurance"].mean() * 100

# st.subheader("📆 Conversion Rate by Contact Month")
# st.line_chart(month_kpi)

# success_calls = df[df["CarInsurance"] == 1]["CallDuration"].mean()
# failed_calls = df[df["CarInsurance"] == 0]["CallDuration"].mean()

# col1, col2 = st.columns(2)
# col1.metric("Avg Call Duration (Converted)", f"{success_calls:.0f} sec")
# col2.metric("Avg Call Duration (Not Converted)", f"{failed_calls:.0f} sec")

# loan_kpi = df.groupby("CarLoan")["CarInsurance"].mean() * 100
# insurance_kpi = df.groupby("HHInsurance")["CarInsurance"].mean() * 100

# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("🚗 Car Loan Impact")
#     st.bar_chart(loan_kpi)

# with col2:
#     st.subheader("🏠 Home Insurance Impact")
#     st.bar_chart(insurance_kpi)

# summary = pd.DataFrame({
#     "Metric": [
#         "Total Customers",
#         "Total Conversions",
#         "Conversion Rate (%)",
#         "Avg Call Duration (sec)",
#         "Avg Account Balance"
#     ],
#     "Value": [
#         total_customers,
#         total_conversions,
#         f"{conversion_rate:.2f}",
#         f"{avg_call_duration:.0f}",
#         f"{avg_balance:.2f}"
#     ]
# })

# st.subheader("📋 KPI Summary")
# st.table(summary)

