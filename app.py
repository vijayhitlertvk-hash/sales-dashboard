import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Operations Dashboard", layout="wide")

# Password Gate Function
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

# Render Dashboard if Authenticated
if check_password():
    st.title("📊 E-Commerce Sales & Inventory Portal")

    uploaded_file = st.file_uploader("Upload Daily Sales CSV", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Metric Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sales", f"${df['Sales'].sum():,.2f}")
        col2.metric("Total Orders", f"{len(df):,}")
        col3.metric("Avg Order Value", f"${df['Sales'].mean():,.2f}")
        
        st.markdown("---")
        
        # Side-by-Side Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            fig_line = px.line(df, x="Date", y="Sales", title="📈 Daily Revenue Trend")
            st.plotly_chart(fig_line, use_container_width=True)
            
        with chart_col2:
            fig_bar = px.bar(df, x="Category", y="Sales", color="Category", title="🏷️ Revenue by Category", barmode="group")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("---")
        
        # Data Table Explorer
        st.subheader("📋 Raw Data Explorer")
        selected_category = st.multiselect("Filter by Category", options=df["Category"].unique(), default=df["Category"].unique())
        filtered_df = df[df["Category"].isin(selected_category)]
        st.dataframe(filtered_df, use_container_width=True)

    else:
        st.info("Please upload a CSV file to render the metrics.")