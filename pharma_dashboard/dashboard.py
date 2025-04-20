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
            'total_orders': 0,
            'top_product': 'N/A',
            'top_region': 'N/A',
            'sales_growth': 0,
            'avg_daily_sales': 0
        }
    
    total_sales = filtered_sales['sales_amount'].sum()
    total_units = filtered_sales['units_sold'].sum()
    total_orders = len(filtered_sales)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Calculate top product
    top_product = filtered_sales.groupby('product_name')['sales_amount'].sum().idxmax()
    
    # Calculate top region
    top_region = filtered_sales.groupby('region')['sales_amount'].sum().idxmax()
    
    # Calculate sales growth
    daily_sales = filtered_sales.groupby('date')['sales_amount'].sum()
    if len(daily_sales) > 1:
        sales_growth = ((daily_sales.iloc[-1] - daily_sales.iloc[0]) / daily_sales.iloc[0]) * 100
    else:
        sales_growth = 0
    
    # Calculate average daily sales
    avg_daily_sales = total_sales / len(daily_sales) if len(daily_sales) > 0 else 0
    
    return {
        'total_sales': total_sales,
        'total_units': total_units,
        'avg_order_value': avg_order_value,
        'total_orders': total_orders,
        'top_product': top_product,
        'top_region': top_region,
        'sales_growth': sales_growth,
        'avg_daily_sales': avg_daily_sales
    }

def create_sales_trend_chart(filtered_sales):
    """Create an enhanced sales trend chart with moving average"""
    daily_sales = filtered_sales.groupby('date')['sales_amount'].sum().reset_index()
    daily_sales['7_day_ma'] = daily_sales['sales_amount'].rolling(window=7).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_sales['date'],
        y=daily_sales['sales_amount'],
        name='Daily Sales',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=daily_sales['date'],
        y=daily_sales['7_day_ma'],
        name='7-Day Moving Average',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title="Daily Sales Trend with Moving Average",
        xaxis_title="Date",
        yaxis_title="Sales Amount",
        height=400,
        showlegend=True
    )
    return fig

def create_regional_analysis(filtered_sales):
    """Create comprehensive regional analysis"""
    # Regional sales pie chart
    regional_sales = filtered_sales.groupby('region')['sales_amount'].sum().reset_index()
    fig_pie = px.pie(
        regional_sales,
        values='sales_amount',
        names='region',
        title="Sales Distribution by Region",
        hole=0.3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    # Regional growth chart
    regional_growth = filtered_sales.groupby(['region', 'date'])['sales_amount'].sum().reset_index()
    fig_growth = px.line(
        regional_growth,
        x='date',
        y='sales_amount',
        color='region',
        title="Regional Sales Growth Over Time"
    )
    fig_growth.update_layout(height=400)
    
    return fig_pie, fig_growth

def create_product_analysis(filtered_sales):
    """Create comprehensive product analysis"""
    # Product performance
    product_sales = filtered_sales.groupby(['product_name', 'category'])['sales_amount'].sum().reset_index()
    product_sales = product_sales.sort_values('sales_amount', ascending=True)
    
    fig_products = px.bar(
        product_sales,
        x='sales_amount',
        y='product_name',
        color='category',
        orientation='h',
        title="Sales by Product and Category"
    )
    fig_products.update_layout(height=400)
    
    # Category performance with trend
    category_trend = filtered_sales.groupby(['category', 'date'])['sales_amount'].sum().reset_index()
    fig_category = px.line(
        category_trend,
        x='date',
        y='sales_amount',
        color='category',
        title="Category Performance Over Time"
    )
    fig_category.update_layout(height=400)
    
    return fig_products, fig_category

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
            default=regions
        )
        
        # Product category filter
        categories = sorted(sales_df['category'].unique())
        selected_categories = st.sidebar.multiselect(
            "Select Product Categories",
            categories,
            default=categories
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
        
        # Additional metrics
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Top Product", metrics['top_product'])
        with col6:
            st.metric("Top Region", metrics['top_region'])
        with col7:
            st.metric("Sales Growth", f"{metrics['sales_growth']:.1f}%")
        with col8:
            st.metric("Avg Daily Sales", f"${metrics['avg_daily_sales']:,.2f}")
        
        # Sales Trend Analysis
        st.subheader("Sales Trend Analysis")
        fig_trend = create_sales_trend_chart(filtered_sales)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Regional Analysis
        st.subheader("Regional Analysis")
        fig_pie, fig_growth = create_regional_analysis(filtered_sales)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.plotly_chart(fig_growth, use_container_width=True)
        
        # Product Analysis
        st.subheader("Product Analysis")
        fig_products, fig_category = create_product_analysis(filtered_sales)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_products, use_container_width=True)
        with col2:
            st.plotly_chart(fig_category, use_container_width=True)
        
        # Customer Analysis
        st.subheader("Customer Analysis")
        customer_metrics = filtered_sales.groupby('customer_id').agg({
            'sales_amount': ['sum', 'count'],
            'units_sold': 'sum'
        }).reset_index()
        customer_metrics.columns = ['customer_id', 'total_spent', 'order_count', 'total_units']
        customer_metrics['avg_order_value'] = customer_metrics['total_spent'] / customer_metrics['order_count']
        
        fig_customer = px.scatter(
            customer_metrics,
            x='total_spent',
            y='order_count',
            size='total_units',
            title="Customer Value Analysis",
            labels={
                'total_spent': 'Total Spent ($)',
                'order_count': 'Number of Orders',
                'total_units': 'Total Units Purchased'
            }
        )
        st.plotly_chart(fig_customer, use_container_width=True)
    
    except Exception as e:
        logger.error(f"Error in main dashboard: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 