import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Fitness Club Intelligence Portal", layout="wide")

# Custom CSS for Sleek Visual Styling & UI Enhancements
st.markdown("""
    <style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Fix Top Title Clipping */
    .block-container {
        padding-top: 3.5rem !important;
    }
    
    /* Styled Metric Container Cards */
    div[data-testid="stMetric"] {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }

    /* Custom Header Styling */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #f1f5f9 !important;
        font-weight: 700;
    }

    /* Primary Accent Buttons */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# Password Authentication Gate
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
    st.title("🏋️ Fitness Club Operations & MRR Intelligence Portal")

    # File Uploader with Sample Fallback
    uploaded_file = st.file_uploader("Upload Member Roster CSV", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.info("💡 Showing sample club dataset. Upload a CSV to view your own facility metrics.")
        df = pd.DataFrame({
            "Member_ID": [f"M-{100+i}" for i in range(15)],
            "Plan": ["Monthly", "Annual", "Monthly", "VIP", "Monthly", "Annual", "VIP", "Monthly", "Annual", "Monthly", "VIP", "Monthly", "Annual", "VIP", "Monthly"],
            "Monthly_Fee": [50, 40, 50, 100, 50, 40, 100, 50, 40, 50, 100, 50, 40, 100, 50],
            "Day_Visited": ["Monday", "Monday", "Tuesday", "Wednesday", "Monday", "Thursday", "Friday", "Saturday", "Sunday", "Monday", "Wednesday", "Tuesday", "Friday", "Monday", "Thursday"],
            "Visits_This_Month": [12, 16, 8, 14, 1, 11, 18, 9, 2, 15, 20, 7, 13, 19, 1],
            "Status": ["Active", "Active", "Active", "Active", "Churned", "Active", "Active", "Active", "Churned", "Active", "Active", "Active", "Active", "Active", "Active"]
        })

    # Sidebar Interactive Controls
    st.sidebar.header("🔍 Interactive Controls")
    selected_plans = st.sidebar.multiselect(
        "Filter by Membership Tier:",
        options=df["Plan"].unique(),
        default=df["Plan"].unique()
    )
    selected_status = st.sidebar.multiselect(
        "Filter by Member Status:",
        options=df["Status"].unique(),
        default=df["Status"].unique()
    )

    filtered_df = df[(df["Plan"].isin(selected_plans)) & (df["Status"].isin(selected_status))]

    # 1. Automated Executive Insights
    st.subheader("💡 Automated Retention & Revenue Insights")
    active_df = filtered_df[filtered_df["Status"] == "Active"]
    active_members = len(active_df)
    mrr = active_df["Monthly_Fee"].sum()
    at_risk_members = active_df[active_df["Visits_This_Month"] <= 2]

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Members", active_members)
    col2.metric("Monthly Recurring Revenue (MRR)", f"${mrr:,}")
    col3.metric("At-Risk Members (≤2 Visits)", f"{len(at_risk_members)} Members", delta="-Retention Alert", delta_color="inverse")

    if len(at_risk_members) > 0:
        st.warning(f"⚠️ **Churn Risk Alert:** {len(at_risk_members)} active member(s) visited 2 times or less this month. Trigger automated check-in SMS.")

    # MRR Target Gauge
    mrr_target = 1000
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=mrr,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Monthly Recurring Revenue Target ($1,000)", 'font': {'color': '#f8fafc'}},
        delta={'reference': mrr_target},
        gauge={
            'axis': {'range': [None, 1500], 'tickcolor': "#f8fafc"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "#0f172a",
            'borderwidth': 1,
            'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, 500], 'color': "#ef4444"},
                {'range': [500, 1000], 'color': "#f59e0b"}
            ]
        }
    ))
    fig_gauge.update_layout(
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f8fafc"},
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # 2. Interactive Visualizations
    st.subheader("📊 Facility Attendance & Tier Breakdown")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        visit_counts = filtered_df["Day_Visited"].value_counts().reindex(day_order, fill_value=0).reset_index()
        visit_counts.columns = ["Day", "Visits"]
        fig_visits = px.bar(
            visit_counts, x="Day", y="Visits", 
            title="📅 Peak Club Attendance by Day", 
            color="Visits", color_continuous_scale="Blues",
            template="plotly_dark"
        )
        fig_visits.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_visits, use_container_width=True)

    with chart_col2:
        plan_rev = active_df.groupby("Plan")["Monthly_Fee"].sum().reset_index()
        fig_plans = px.pie(
            plan_rev, names="Plan", values="Monthly_Fee", 
            title="💰 MRR Contribution by Tier", hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b"]
        )
        fig_plans.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_plans, use_container_width=True)

    st.markdown("---")

    # 3. Interactive Retention & MRR Simulator
    st.subheader("🧮 What-If Retention & Pricing Simulator")
    st.caption("Simulate how reducing churn or adding new members impacts annual recurring revenue.")

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        new_members = st.slider("New Monthly Signups", min_value=0, max_value=50, value=10, step=2)
    with sim_col2:
        avg_new_fee = st.slider("Avg New Member Fee ($)", min_value=30, max_value=150, value=60, step=10)
    with sim_col3:
        retention_boost = st.slider("Saved At-Risk Members", min_value=0, max_value=10, value=2, step=1)

    projected_mrr = mrr + (new_members * avg_new_fee) + (retention_boost * 50)
    projected_arr = projected_mrr * 12
    mrr_gain = projected_mrr - mrr

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Projected Monthly Revenue", f"${projected_mrr:,.2f}", delta=f"+${mrr_gain:,.2f}/mo")
    m_col2.metric("Projected Annual Run-Rate (ARR)", f"${projected_arr:,.2f}")
    m_col3.metric("MRR Growth Rate", f"+{(mrr_gain / max(mrr, 1)) * 100:.1f}%")

    st.markdown("---")

    # 4. Data Explorer & Export
    st.subheader("📋 Member Roster Explorer & Export")
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Roster (CSV)",
        data=csv_data,
        file_name="gym_member_report.csv",
        mime="text/csv"
    )

    st.dataframe(filtered_df, use_container_width=True)