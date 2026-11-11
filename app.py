import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="E-Commerce Intelligence Portal", layout="wide")

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
    st.title("🚀 E-Commerce Operations & Interactive Intelligence Portal")

    # File Uploader with Interactive Fallback
    uploaded_file = st.file_uploader("Upload Sales CSV", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        st.info("💡 Showing sample dataset. Upload a CSV to view your own store metrics.")
        # Generate rich interactive dataset
        dates = pd.date_range(start="2026-01-01", periods=14, freq="D")
        df = pd.DataFrame({
            "Date": dates,
            "Day_of_Week": dates.day_name(),
            "Category": ["Electronics", "Clothing", "Electronics", "Home", "Clothing", "Home", "Electronics", 
                         "Clothing", "Home", "Electronics", "Clothing", "Home", "Electronics", "Clothing"],
            "Sales": [1200, 450, 950, 300, 600, 400, 1500, 500, 350, 1100, 750, 620, 1800, 890],
            "Orders": [12, 15, 8, 5, 20, 6, 11, 14, 4, 9, 18, 7, 13, 16],
            "Stock_Level": [4, 45, 12, 2, 30, 18, 5, 22, 1, 15, 28, 9, 3, 31]
        })

    # Sidebar Interactive Filters
    st.sidebar.header("🔍 Interactive Controls")
    selected_categories = st.sidebar.multiselect(
        "Filter by Category:",
        options=df["Category"].unique(),
        default=df["Category"].unique()
    )
    
    # Filter DataFrame based on selection
    filtered_df = df[df["Category"].isin(selected_categories)]

    # 1. Executive Summary & Dynamic Insights Header
    st.subheader("💡 Automated Executive Insights")
    total_revenue = filtered_df["Sales"].sum()
    monthly_target = 15000
    progress_pct = min(total_revenue / monthly_target * 100, 100)
    low_stock_items = filtered_df[filtered_df["Stock_Level"] < 5]

    col_ins1, col_ins2, col_ins3 = st.columns(3)
    col_ins1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col_ins2.metric("Filtered Orders", f"{filtered_df['Orders'].sum():,}")
    col_ins3.metric("Inventory Alerts", f"{len(low_stock_items)} SKUs Low Stock", delta="-Action Required", delta_color="inverse")

    # Gauge Chart for Target Tracking
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = total_revenue,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Monthly Revenue Goal Target ($15,000)"},
        delta = {'reference': monthly_target},
        gauge = {
            'axis': {'range': [None, 20000]},
            'bar': {'color': "#00CC96"},
            'steps': [
                {'range': [0, 7500], 'color': "#FF6B6B"},
                {'range': [7500, 15000], 'color': "#FFE66D"}
            ]
        }
    ))
    fig_gauge.update_layout(height=220, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # 2. Advanced Interactive Visualizations
    st.subheader("📊 Interactive Performance Visualizations")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_line = px.line(
            filtered_df, x="Date", y="Sales", color="Category",
            title="📈 Revenue Trend & Breakdown", markers=True,
            hover_data=["Orders", "Stock_Level"]
        )
        fig_line.update_traces(hovertemplate="<b>Date:</b> %{x}<br><b>Sales:</b> $%{y:,.2f}")
        st.plotly_chart(fig_line, use_container_width=True)

    with chart_col2:
        fig_heatmap = px.density_heatmap(
            filtered_df, x="Day_of_Week", y="Category", z="Sales",
            title="🔥 Sales Heatmap by Day & Category",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("---")

    # 3. Interactive Financial & ROI Simulator
    st.subheader("🧮 What-If Revenue & Profit Simulator")
    st.caption("Adjust controls below to simulate potential growth scenarios.")

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        price_change = st.slider("Price Adjustment (%)", min_value=-20, max_value=50, value=10, step=5)
    with sim_col2:
        volume_change = st.slider("Order Growth (%)", min_value=-20, max_value=100, value=15, step=5)
    with sim_col3:
        current_margin = st.slider("Profit Margin (%)", min_value=5, max_value=60, value=25, step=5)

    # Calculations
    projected_revenue = total_revenue * (1 + price_change / 100) * (1 + volume_change / 100)
    projected_profit = projected_revenue * (current_margin / 100)
    revenue_diff = projected_revenue - total_revenue

    st.markdown("#### **Simulation Results:**")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Projected Revenue", f"${projected_revenue:,.2f}", delta=f"${revenue_diff:,.2f}")
    m_col2.metric("Projected Profit", f"${projected_profit:,.2f}")
    m_col3.metric("Margin Multiplier Growth", f"{price_change + volume_change}%")

    st.markdown("---")

    # 4. Interactive Data Explorer with Download Button
    st.subheader("📋 Raw Data Explorer & Export")
    
    csv_export = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=csv_export,
        file_name="filtered_ecommerce_data.csv",
        mime="text/csv"
    )

    st.dataframe(filtered_df, use_container_width=True)