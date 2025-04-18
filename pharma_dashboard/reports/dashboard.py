import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from pathlib import Path
from pharma_dashboard.data.processing import download_and_process_data
from ..data.sql_interface import PharmaDB
import numpy as np

# Initialize database connection
db = PharmaDB()

def validate_and_clean_data(df, table_name):
    """Validate and clean data before visualization"""
    if df is None or df.empty:
        return None
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values based on table type
    if table_name == 'sales':
        # For sales data, we'll drop rows with missing critical fields
        critical_fields = ['date', 'sales_amount', 'units_sold', 'region']
        df = df.dropna(subset=critical_fields)
        
        # Convert date to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
            
    elif table_name == 'products':
        # For products, we'll fill missing categories with 'Uncategorized'
        df['category'] = df['category'].fillna('Uncategorized')
        
    elif table_name == 'customers':
        # For customers, we'll fill missing regions with 'Unknown'
        df['region'] = df['region'].fillna('Unknown')
    
    return df

def load_data():
    """Load data from SQL database with validation"""
    try:
        # Load sales data
        sales_df = db.execute_query("SELECT * FROM sales")
        sales_df = validate_and_clean_data(sales_df, 'sales')
        
        # Load products data
        products_df = db.execute_query("SELECT * FROM products")
        products_df = validate_and_clean_data(products_df, 'products')
        
        # Load customers data
        customers_df = db.execute_query("SELECT * FROM customers")
        customers_df = validate_and_clean_data(customers_df, 'customers')
        
        return sales_df, products_df, customers_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def apply_filters(sales_df, products_df, start_date, end_date, selected_regions, selected_categories):
    """Apply all filters to the data"""
    if sales_df is None or products_df is None:
        return None, None
    
    # Date range filter
    filtered_sales = sales_df[
        (sales_df['date'].dt.date >= start_date) &
        (sales_df['date'].dt.date <= end_date)
    ]
    
    # Region filter
    if selected_regions:
        filtered_sales = filtered_sales[filtered_sales['region'].isin(selected_regions)]
    
    # Product category filter
    if selected_categories:
        filtered_products = products_df[products_df['category'].isin(selected_categories)]
        filtered_sales = filtered_sales[filtered_sales['product_name'].isin(filtered_products['product_name'])]
    else:
        filtered_products = products_df
    
    return filtered_sales, filtered_products

def calculate_metrics(filtered_sales):
    """Calculate key metrics from filtered data"""
    if filtered_sales is None or filtered_sales.empty:
        return {
            'total_sales': 0,
            'total_units': 0,
            'avg_order_value': 0,
            'total_orders': 0,
            'yoy_growth': 0
        }
    
    total_sales = filtered_sales['sales_amount'].sum()
    total_units = filtered_sales['units_sold'].sum()
    total_orders = len(filtered_sales)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Calculate YoY growth
    current_year = datetime.now().year
    current_year_sales = filtered_sales[filtered_sales['date'].dt.year == current_year]['sales_amount'].sum()
    prev_year_sales = filtered_sales[filtered_sales['date'].dt.year == current_year - 1]['sales_amount'].sum()
    yoy_growth = ((current_year_sales - prev_year_sales) / prev_year_sales * 100) if prev_year_sales > 0 else 0
    
    return {
        'total_sales': total_sales,
        'total_units': total_units,
        'avg_order_value': avg_order_value,
        'total_orders': total_orders,
        'yoy_growth': yoy_growth
    }

def create_sales_metrics(sales_df):
    """Create sales metrics visualization"""
    total_sales = sales_df['Total'].sum()
    avg_order_value = sales_df['Total'].mean()
    total_orders = len(sales_df)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Average Order Value", f"${avg_order_value:,.2f}")
    with col3:
        st.metric("Total Orders", f"{total_orders:,}")

def create_sales_trend(sales_df):
    """Create sales trend visualization"""
    monthly_sales = sales_df.groupby(sales_df['Date'].dt.to_period('M')).agg({
        'Total': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=monthly_sales['Date'], y=monthly_sales['Total'],
                  name="Sales Amount", line=dict(color='blue'))
    )
    fig.update_layout(
        title='Monthly Sales Trend',
        xaxis_title='Date',
        yaxis_title='Sales Amount ($)'
    )
    st.plotly_chart(fig, use_container_width=True)

def create_product_analysis(sales_df, products_df):
    """Create product analysis visualization"""
    product_sales = pd.merge(sales_df, products_df, on='Product')
    sales_by_category = product_sales.groupby('Category')['Total'].sum().sort_values(ascending=True)
    
    fig = px.bar(
        x=sales_by_category.values,
        y=sales_by_category.index,
        orientation='h',
        title='Sales by Product Category'
    )
    fig.update_layout(
        xaxis_title='Total Sales ($)',
        yaxis_title='Category'
    )
    st.plotly_chart(fig, use_container_width=True)

def create_customer_analysis(sales_df, customers_df):
    """Create customer analysis visualization"""
    customer_sales = pd.merge(sales_df, customers_df, on='Customer')
    sales_by_type = customer_sales.groupby('Customer Type')['Total'].sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=sales_by_type.index,
        values=sales_by_type.values,
        hole=.3
    )])
    fig.update_layout(title='Sales Distribution by Customer Type')
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(page_title="Pharma Sales Dashboard", layout="wide")
    
    st.title("Pharmaceutical Sales Dashboard")
    
    try:
        # Load data
        sales_df, products_df, customers_df = load_data()
        
        if sales_df is None or products_df is None or customers_df is None:
            st.error("Failed to load data. Please check the database connection.")
            return
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Date range filter
        min_date = sales_df['date'].min().date()
        max_date = sales_df['date'].max().date()
        start_date = st.sidebar.date_input("Start Date", min_date)
        end_date = st.sidebar.date_input("End Date", max_date)
        
        # Region filter
        regions = sorted(sales_df['region'].unique())
        selected_regions = st.sidebar.multiselect("Select Regions", regions, default=regions)
        
        # Product category filter
        categories = sorted(products_df['category'].unique())
        selected_categories = st.sidebar.multiselect("Select Categories", categories, default=categories)
        
        # Apply filters
        filtered_sales, filtered_products = apply_filters(
            sales_df, products_df, start_date, end_date, 
            selected_regions, selected_categories
        )
        
        # Calculate metrics
        metrics = calculate_metrics(filtered_sales)
        
        # Main dashboard layout
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sales", f"${metrics['total_sales']:,.2f}")
        with col2:
            st.metric("Total Units Sold", f"{metrics['total_units']:,}")
        with col3:
            st.metric("Average Order Value", f"${metrics['avg_order_value']:,.2f}")
        with col4:
            st.metric("YoY Growth", f"{metrics['yoy_growth']:.1f}%")
        
        # Sales trend chart
        st.subheader("Sales Trend")
        daily_sales = filtered_sales.groupby('date')['sales_amount'].sum().reset_index()
        fig = px.line(daily_sales, x='date', y='sales_amount', title="Daily Sales Trend")
        st.plotly_chart(fig)
        
        # Product performance
        st.subheader("Product Performance")
        product_sales = filtered_sales.groupby('product_name')['sales_amount'].sum().reset_index()
        product_sales = product_sales.sort_values('sales_amount', ascending=False)
        fig = px.bar(product_sales, x='product_name', y='sales_amount', title="Sales by Product")
        st.plotly_chart(fig)
        
        # Regional performance
        st.subheader("Regional Performance")
        regional_sales = filtered_sales.groupby('region')['sales_amount'].sum().reset_index()
        regional_sales = regional_sales.sort_values('sales_amount', ascending=False)
        fig = px.bar(regional_sales, x='region', y='sales_amount', title="Sales by Region")
        st.plotly_chart(fig)
        
        # SQL Query Interface
        st.subheader("SQL Query Interface")
        query = st.text_area("Enter your SQL query:", height=100)
        if st.button("Execute Query"):
            try:
                result = db.execute_query(query)
                st.dataframe(result)
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        print(f"Detailed error: {str(e)}")  # Add detailed error logging

if __name__ == "__main__":
    main() 