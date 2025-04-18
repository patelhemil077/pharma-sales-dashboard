import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from pathlib import Path
from pharma_dashboard.data_processor import load_and_preprocess_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Pharmaceutical Sales Dashboard",
    page_icon="💊",
    layout="wide"
)

@st.cache_data
def load_data():
    """Load and preprocess data using the data processor"""
    try:
        return load_and_preprocess_data()
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def apply_filters(sales_df, products_df, start_date, end_date, selected_regions, selected_categories, min_amount=None, max_amount=None):
    """Apply all filters to the data"""
    if sales_df is None or products_df is None:
        return None, None
    
    filtered_sales = sales_df.copy()
    
    # Date range filter
    filtered_sales = filtered_sales[
        (filtered_sales['date'].dt.date >= start_date) &
        (filtered_sales['date'].dt.date <= end_date)
    ]
    
    # Region filter
    if selected_regions:
        filtered_sales = filtered_sales[filtered_sales['region'].isin(selected_regions)]
    
    # Product category filter
    if selected_categories:
        filtered_sales = filtered_sales[filtered_sales['category'].isin(selected_categories)]
    
    # Amount range filter
    if min_amount is not None:
        filtered_sales = filtered_sales[filtered_sales['sales_amount'] >= min_amount]
    if max_amount is not None:
        filtered_sales = filtered_sales[filtered_sales['sales_amount'] <= max_amount]
    
    return filtered_sales, products_df

def calculate_metrics(filtered_sales):
    """Calculate key metrics from filtered data"""
    if filtered_sales is None or filtered_sales.empty:
        return {
            'total_sales': 0,
            'total_units': 0,
            'avg_order_value': 0,
            'total_orders': 0
        }
    
    total_sales = filtered_sales['sales_amount'].sum()
    total_units = filtered_sales['units_sold'].sum()
    total_orders = len(filtered_sales)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    return {
        'total_sales': total_sales,
        'total_units': total_units,
        'avg_order_value': avg_order_value,
        'total_orders': total_orders
    }

def main():
    st.title("Pharmaceutical Sales Dashboard")
    
    try:
        # Load data
        sales_df, products_df, customers_df = load_data()
        if sales_df is None or products_df is None or customers_df is None:
            st.error("Failed to load data. Please check the data files and their format.")
            return
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Date range filter
        min_date = sales_df['date'].min().date()
        max_date = sales_df['date'].max().date()
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_date)
        with col2:
            end_date = st.date_input("End Date", max_date)
        
        # Region filter
        regions = sorted(sales_df['region'].unique())
        selected_regions = st.sidebar.multiselect(
            "Select Regions",
            regions,
            default=regions[:2] if len(regions) > 1 else regions
        )
        
        # Product category filter
        categories = sorted(sales_df['category'].unique())
        selected_categories = st.sidebar.multiselect(
            "Select Product Categories",
            categories,
            default=categories[:2] if len(categories) > 1 else categories
        )
        
        # Sales amount range filter
        st.sidebar.subheader("Sales Amount Range")
        min_sales = float(sales_df['sales_amount'].min())
        max_sales = float(sales_df['sales_amount'].max())
        sales_range = st.sidebar.slider(
            "Select Range",
            min_value=min_sales,
            max_value=max_sales,
            value=(min_sales, max_sales)
        )
        
        # Apply filters
        filtered_sales, filtered_products = apply_filters(
            sales_df, products_df, start_date, end_date,
            selected_regions, selected_categories,
            sales_range[0], sales_range[1]
        )
        
        if filtered_sales is None or filtered_sales.empty:
            st.warning("No data available for the selected filters")
            return
        
        # Calculate metrics
        metrics = calculate_metrics(filtered_sales)
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sales", f"${metrics['total_sales']:,.2f}")
        with col2:
            st.metric("Total Units Sold", f"{metrics['total_units']:,}")
        with col3:
            st.metric("Average Order Value", f"${metrics['avg_order_value']:,.2f}")
        with col4:
            st.metric("Total Orders", f"{metrics['total_orders']:,}")
        
        # Create two columns for charts
        left_column, right_column = st.columns(2)
        
        with left_column:
            # Sales trend chart
            st.subheader("Sales Trend")
            daily_sales = filtered_sales.groupby('date')['sales_amount'].sum().reset_index()
            fig = px.line(
                daily_sales,
                x='date',
                y='sales_amount',
                title="Daily Sales Trend"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Product performance
            st.subheader("Product Performance")
            product_sales = filtered_sales.groupby('product_name')['sales_amount'].sum().reset_index()
            product_sales = product_sales.sort_values('sales_amount', ascending=True)
            fig = px.bar(
                product_sales,
                x='sales_amount',
                y='product_name',
                orientation='h',
                title="Sales by Product"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with right_column:
            # Regional performance
            st.subheader("Regional Performance")
            regional_sales = filtered_sales.groupby('region')['sales_amount'].sum().reset_index()
            fig = px.pie(
                regional_sales,
                values='sales_amount',
                names='region',
                title="Sales by Region"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Category performance
            st.subheader("Category Performance")
            category_sales = filtered_sales.groupby('category')['sales_amount'].sum().reset_index()
            category_sales = category_sales.sort_values('sales_amount', ascending=True)
            fig = px.bar(
                category_sales,
                x='sales_amount',
                y='category',
                orientation='h',
                title="Sales by Category"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        logger.error(f"Error in main dashboard: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 