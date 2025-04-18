import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processor import load_and_process_data

# Page config
st.set_page_config(
    page_title="Pharmaceutical Sales Dashboard",
    page_icon="💊",
    layout="wide"
)

# Load data
sales_df, products_df, customers_df = load_and_process_data()

# Sidebar filters
st.sidebar.title("Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(sales_df['Date'].min(), sales_df['Date'].max())
)

# Region filter
regions = customers_df['Region'].unique()
selected_region = st.sidebar.multiselect(
    "Select Region",
    regions,
    default=regions[0]
)

# Product category filter
categories = products_df['Category'].unique()
selected_category = st.sidebar.multiselect(
    "Select Product Category",
    categories,
    default=categories[0]
)

# Main dashboard
st.title("Pharmaceutical Sales Dashboard")

# KPI metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sales", f"${sales_df['Total'].sum():,.2f}")
with col2:
    st.metric("Total Units", f"{sales_df['Quantity'].sum():,}")
with col3:
    st.metric("Average Order Value", f"${sales_df['Total'].mean():,.2f}")
with col4:
    st.metric("Total Orders", f"{len(sales_df):,}")

# Charts
st.subheader("Sales Trends")
# Add your visualization code here

st.subheader("Product Performance")
# Add your visualization code here

st.subheader("Regional Distribution")
# Add your visualization code here

st.subheader("Customer Segments")
# Add your visualization code here 