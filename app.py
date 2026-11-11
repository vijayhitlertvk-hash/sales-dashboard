import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="Operations Dashboard", layout="wide")
st.title("📊 E-Commerce Sales & Inventory Portal")

# File Uploader
uploaded_file = st.file_uploader("Upload Daily Sales CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${df['Sales'].sum():,.2f}")
    col2.metric("Total Orders", f"{len(df):,}")
    col3.metric("Avg Order Value", f"${df['Sales'].mean():,.2f}")
    
    # Interactive Revenue Chart
    fig = px.line(df, x="Date", y="Sales", title="Daily Revenue Trend")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please upload a CSV file to render the metrics.")