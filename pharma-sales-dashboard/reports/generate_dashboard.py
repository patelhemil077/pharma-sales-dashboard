import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore
from plotly.subplots import make_subplots # type: ignore
from datetime import datetime
import os

def load_data():
    """Load the CSV files"""
    sales_df = pd.read_csv('../data/sales.csv')
    customers_df = pd.read_csv('../data/customers.csv')
    products_df = pd.read_csv('../data/products.csv')
    
    # Convert date column
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    return sales_df, customers_df, products_df

def create_ytd_metrics(sales_df):
    """Create YTD metrics visualization"""
    current_year = datetime.now().year
    ytd_sales = sales_df[sales_df['date'].dt.year == current_year]['sales_amount'].sum()
    prev_ytd_sales = sales_df[sales_df['date'].dt.year == current_year - 1]['sales_amount'].sum()
    yoy_growth = ((ytd_sales - prev_ytd_sales) / prev_ytd_sales) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = ytd_sales,
        number = {'prefix': "$", "valueformat": ",.0f"},
        delta = {'position': "top", 'reference': prev_ytd_sales},
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Year-to-Date Sales"}
    ))
    return fig

def create_monthly_trend(sales_df):
    """Create monthly sales trend visualization"""
    monthly_sales = sales_df.groupby(sales_df['date'].dt.to_period('M')).agg({
        'sales_amount': 'sum',
        'units_sold': 'sum'
    }).reset_index()
    monthly_sales['date'] = monthly_sales['date'].dt.to_timestamp()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=monthly_sales['date'], y=monthly_sales['sales_amount'],
                  name="Sales Amount", line=dict(color='blue')),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_sales['date'], y=monthly_sales['units_sold'],
                  name="Units Sold", line=dict(color='red')),
        secondary_y=True,
    )
    
    fig.update_layout(
        title='Monthly Sales Trend',
        xaxis_title='Date',
        yaxis_title='Sales Amount ($)',
        yaxis2_title='Units Sold'
    )
    return fig

def create_customer_distribution(sales_df, customers_df):
    """Create customer distribution pie chart"""
    customer_sales = pd.merge(sales_df, customers_df, on='customer_id')
    sales_by_type = customer_sales.groupby('customer_type')['sales_amount'].sum()
    
    fig = go.Figure(data=[go.Pie(labels=sales_by_type.index, 
                                values=sales_by_type.values,
                                hole=.3)])
    fig.update_layout(title='Sales Distribution by Customer Type')
    return fig

def create_regional_performance(sales_df):
    """Create regional performance heatmap"""
    regional_monthly = sales_df.pivot_table(
        index=sales_df['date'].dt.strftime('%Y-%m'),
        columns='region',
        values='sales_amount',
        aggfunc='sum'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=regional_monthly.values,
        x=regional_monthly.columns,
        y=regional_monthly.index,
        colorscale='RdYlBu_r'
    ))
    
    fig.update_layout(
        title='Regional Performance Heatmap',
        xaxis_title='Region',
        yaxis_title='Month'
    )
    return fig

def main():
    # Create reports directory if it doesn't exist
    if not os.path.exists('html_reports'):
        os.makedirs('html_reports')
    
    # Load data
    sales_df, customers_df, products_df = load_data()
    
    # Generate visualizations
    ytd_fig = create_ytd_metrics(sales_df)
    trend_fig = create_monthly_trend(sales_df)
    customer_fig = create_customer_distribution(sales_df, customers_df)
    regional_fig = create_regional_performance(sales_df)
    
    # Save individual plots
    ytd_fig.write_html("html_reports/ytd_metrics.html")
    trend_fig.write_html("html_reports/monthly_trend.html")
    customer_fig.write_html("html_reports/customer_distribution.html")
    regional_fig.write_html("html_reports/regional_performance.html")
    
    # Create a combined dashboard
    dashboard = make_subplots(
        rows=2, cols=2,
        subplot_titles=("YTD Metrics", "Monthly Trend", 
                       "Customer Distribution", "Regional Performance")
    )
    
    # Add all plots to the dashboard
    dashboard.add_trace(ytd_fig.data[0], row=1, col=1)
    dashboard.add_trace(trend_fig.data[0], row=1, col=2)
    dashboard.add_trace(customer_fig.data[0], row=2, col=1)
    dashboard.add_trace(regional_fig.data[0], row=2, col=2)
    
    # Update layout
    dashboard.update_layout(height=1000, width=1200, title_text="Pharma Sales Dashboard")
    dashboard.write_html("html_reports/dashboard.html")
    
    print("Dashboard generated successfully!")

if __name__ == "__main__":
    main() 