import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="E-Commerce Intelligence Portal", layout="wide")

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

    /* Clean Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        padding: 10px 20px;
        color: #cbd5e1;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
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
    st.title("🚀 E-Commerce Operations & Intelligence Portal")

    # File Uploader
    uploaded_file = st.file_uploader("Upload Store Sales CSV", type=["csv"])
    
    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
        cols = list(raw_df.columns)

        # Smart Column Matcher in Sidebar
        st.sidebar.header("🔗 Match Your CSV Columns")
        st.sidebar.caption("Select which columns in your file match our dashboard fields:")

        date_col = st.sidebar.selectbox("Date Column", cols, index=0)
        cat_col = st.sidebar.selectbox("Category / Product Column", cols, index=min(1, len(cols)-1))
        sales_col = st.sidebar.selectbox("Sales / Revenue Column", cols, index=min(2, len(cols)-1))
        
        orders_options = ["(Auto-count rows)"] + cols
        orders_col = st.sidebar.selectbox("Orders Column (Optional)", orders_options, index=0)
        
        stock_options = ["(Not tracked)"] + cols
        stock_col = st.sidebar.selectbox("Stock Level Column (Optional)", stock_options, index=0)

        # Build standardized DataFrame safely
        df = pd.DataFrame()
        df["Date"] = pd.to_datetime(raw_df[date_col], errors="coerce")
        df["Category"] = raw_df[cat_col].astype(str)
        # Clean currency symbols/commas if present in Sales column
        df["Sales"] = pd.to_numeric(raw_df[sales_col].astype(str).str.replace(r'[$,]', '', regex=True), errors="coerce").fillna(0)
        
        if orders_col == "(Auto-count rows)":
            df["Orders"] = 1
        else:
            df["Orders"] = pd.to_numeric(raw_df[orders_col], errors="coerce").fillna(1)

        if stock_col == "(Not tracked)":
            df["Stock_Level"] = 10  # Default healthy stock if column not provided
            track_stock = False
        else:
            df["Stock_Level"] = pd.to_numeric(raw_df[stock_col], errors="coerce").fillna(10)
            track_stock = True

        df = df.dropna(subset=["Date"])
        df["Day_of_Week"] = df["Date"].dt.day_name()

    else:
        st.info("💡 Showing sample dataset. Upload any CSV above to map your own store columns.")
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
        track_stock = True

    # Sidebar Category Filter
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filter Data")
    selected_categories = st.sidebar.multiselect(
        "Filter by Category:",
        options=df["Category"].unique(),
        default=df["Category"].unique()
    )
    filtered_df = df[df["Category"].isin(selected_categories)]
    total_revenue = filtered_df["Sales"].sum()

    # Clickable Navigation Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview & Charts", "🧮 Profit Simulator", "📋 Data & Export"])

    # --- TAB 1: OVERVIEW & CHARTS ---
    with tab1:
        st.subheader("💡 Automated Executive Insights")
        monthly_target = 15000
        low_stock_items = filtered_df[filtered_df["Stock_Level"] < 5] if track_stock else pd.DataFrame()

        col_ins1, col_ins2, col_ins3 = st.columns(3)
        col_ins1.metric("Total Revenue", f"${total_revenue:,.2f}")
        col_ins2.metric("Total Orders", f"{int(filtered_df['Orders'].sum()):,}")
        
        if track_stock:
            col_ins3.metric("Inventory Alerts", f"{len(low_stock_items)} SKUs Low Stock", delta="-Action Required" if len(low_stock_items) > 0 else "Healthy", delta_color="inverse" if len(low_stock_items) > 0 else "normal")
            if len(low_stock_items) > 0:
                st.warning(f"⚠️ **Stock Alert:** {len(low_stock_items)} record(s) show inventory below 5 units.")
        else:
            avg_order = total_revenue / max(filtered_df["Orders"].sum(), 1)
            col_ins3.metric("Average Order Value", f"${avg_order:,.2f}")

        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_revenue,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Monthly Revenue Goal Target ($15,000)", 'font': {'color': '#f8fafc'}},
            delta={'reference': monthly_target},
            gauge={
                'axis': {'range': [None, max(20000, total_revenue * 1.2)], 'tickcolor': "#f8fafc"},
                'bar': {'color': "#3b82f6"},
                'bgcolor': "#0f172a",
                'borderwidth': 1,
                'bordercolor': "rgba(255,255,255,0.1)",
                'steps': [
                    {'range': [0, 7500], 'color': "#ef4444"},
                    {'range': [7500, 15000], 'color': "#f59e0b"}
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
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig_line = px.line(
                filtered_df, x="Date", y="Sales", color="Category",
                title="📈 Revenue Trend & Breakdown", markers=True,
                template="plotly_dark"
            )
            fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_line, use_container_width=True)

        with chart_col2:
            fig_heatmap = px.density_heatmap(
                filtered_df, x="Day_of_Week", y="Category", z="Sales",
                title="🔥 Sales Heatmap by Day & Category",
                color_continuous_scale="Viridis",
                template="plotly_dark"
            )
            fig_heatmap.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_heatmap, use_container_width=True)

    # --- TAB 2: PROFIT SIMULATOR ---
    with tab2:
        st.subheader("🧮 What-If Revenue & Profit Simulator")
        st.caption("Move the sliders below to see how pricing and order volume changes affect your bottom line.")

        sim_col1, sim_col2, sim_col3 = st.columns(3)
        with sim_col1:
            price_change = st.slider("Price Adjustment (%)", min_value=-20, max_value=50, value=10, step=5)
        with sim_col2:
            volume_change = st.slider("Order Growth (%)", min_value=-20, max_value=100, value=15, step=5)
        with sim_col3:
            current_margin = st.slider("Profit Margin (%)", min_value=5, max_value=60, value=25, step=5)

        projected_revenue = total_revenue * (1 + price_change / 100) * (1 + volume_change / 100)
        projected_profit = projected_revenue * (current_margin / 100)
        revenue_diff = projected_revenue - total_revenue

        st.markdown("---")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Projected Revenue", f"${projected_revenue:,.2f}", delta=f"${revenue_diff:,.2f}")
        m_col2.metric("Projected Profit", f"${projected_profit:,.2f}")
        m_col3.metric("Combined Growth Lift", f"{price_change + volume_change}%")

    # --- TAB 3: DATA & EXPORT ---
    with tab3:
        st.subheader("📋 Filtered Store Data & CSV Export")
        csv_export = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Clean Report (CSV)",
            data=csv_export,
            file_name="clean_ecommerce_report.csv",
            mime="text/csv"
        )
        st.dataframe(filtered_df, use_container_width=True)