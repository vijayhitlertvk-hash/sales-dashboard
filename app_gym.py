import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gym Operations Dashboard", layout="wide")

# Password Gate
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔒 Client Portal Access")
        password = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            if password == "demo123":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect Password")
        return False
    return True

if check_password():
    st.title("🏋️ Fitness Club Operations & MRR Portal")

    # Sample Data Generator for Practice
    data = {
        "Member_ID": [f"M-{100+i}" for i in range(10)],
        "Plan": ["Monthly", "Annual", "Monthly", "VIP", "Monthly", "Annual", "VIP", "Monthly", "Annual", "Monthly"],
        "Monthly_Fee": [50, 40, 50, 100, 50, 40, 100, 50, 40, 50],
        "Day_Visited": ["Monday", "Monday", "Tuesday", "Wednesday", "Monday", "Thursday", "Friday", "Saturday", "Sunday", "Monday"],
        "Status": ["Active", "Active", "Active", "Active", "Churned", "Active", "Active", "Active", "Churned", "Active"]
    }
    df = pd.DataFrame(data)

    # Key Performance Metrics
    col1, col2, col3 = st.columns(3)
    active_members = len(df[df["Status"] == "Active"])
    mrr = df[df["Status"] == "Active"]["Monthly_Fee"].sum()
    churn_count = len(df[df["Status"] == "Churned"])

    col1.metric("Active Members", active_members)
    col2.metric("Monthly Recurring Revenue (MRR)", f"${mrr:,}")
    col3.metric("Churned Members", churn_count, delta_color="inverse")

    st.markdown("---")

    # Visualizations
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        visit_counts = df["Day_Visited"].value_counts().reset_index()
        visit_counts.columns = ["Day", "Visits"]
        fig_visits = px.bar(visit_counts, x="Day", y="Visits", title="📊 Peak Attendance by Day", color="Visits")
        st.plotly_chart(fig_visits, use_container_width=True)

    with chart_col2:
        plan_dist = df[df["Status"] == "Active"]["Plan"].value_counts().reset_index()
        plan_dist.columns = ["Plan", "Count"]
        fig_plans = px.pie(plan_dist, names="Plan", values="Count", title="🍰 Active Membership Tier Distribution", hole=0.4)
        st.plotly_chart(fig_plans, use_container_width=True)

    st.markdown("---")

    # CSV Download Feature
    st.subheader("📥 Export Filtered Member Data")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Member Report CSV",
        data=csv_data,
        file_name="gym_member_report.csv",
        mime="text/csv"
    )

    st.dataframe(df, use_container_width=True)