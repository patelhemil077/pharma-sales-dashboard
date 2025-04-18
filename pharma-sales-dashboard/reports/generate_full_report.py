import pandas as pd # type: ignore
import numpy as np # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore
from plotly.subplots import make_subplots # type: ignore
from datetime import datetime, timedelta
import os

def load_data():
    """Load and preprocess the data"""
    sales_df = pd.read_csv('data/sales.csv')
    customers_df = pd.read_csv('data/customers.csv')
    products_df = pd.read_csv('data/products.csv')
    
    # Convert date column
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    return sales_df, customers_df, products_df

def create_sales_summary(sales_df):
    """Create sales summary metrics"""
    current_year = datetime.now().year
    ytd_sales = sales_df[sales_df['date'].dt.year == current_year]['sales_amount'].sum()
    prev_ytd_sales = sales_df[sales_df['date'].dt.year == current_year - 1]['sales_amount'].sum()
    yoy_growth = ((ytd_sales - prev_ytd_sales) / prev_ytd_sales) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=ytd_sales,
        number={'prefix': "$", "valueformat": ",.0f"},
        delta={'position': "top", 'reference': prev_ytd_sales,
               'relative': True, 'valueformat': ".1%"},
        title={'text': "Year-to-Date Sales<br><span style='font-size:0.8em;color:gray'>with YoY Growth</span>"}
    ))
    return fig

def create_monthly_trend(sales_df):
    """Create monthly sales trend with target"""
    monthly_sales = sales_df.groupby(pd.Grouper(key='date', freq='M')).agg({
        'sales_amount': 'sum',
        'units_sold': 'sum'
    }).reset_index()
    
    # Calculate target (example: 10% above previous year's sales)
    monthly_sales['target'] = monthly_sales['sales_amount'].shift(12) * 1.1
    
    fig = go.Figure()
    
    # Actual sales
    fig.add_trace(go.Scatter(
        x=monthly_sales['date'],
        y=monthly_sales['sales_amount'],
        name="Actual Sales",
        line=dict(color='#2ecc71', width=3)
    ))
    
    # Target line
    fig.add_trace(go.Scatter(
        x=monthly_sales['date'],
        y=monthly_sales['target'],
        name="Target",
        line=dict(color='#e74c3c', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='Monthly Sales Performance vs Target',
        xaxis_title='Date',
        yaxis_title='Sales Amount ($)',
        hovermode='x unified'
    )
    return fig

def create_customer_distribution(sales_df, customers_df):
    """Create customer distribution analysis"""
    customer_sales = pd.merge(sales_df, customers_df, on='customer_id')
    sales_by_type = customer_sales.groupby('customer_type').agg({
        'sales_amount': 'sum',
        'customer_id': 'nunique'
    }).reset_index()
    
    sales_by_type['sales_percentage'] = (sales_by_type['sales_amount'] / 
                                       sales_by_type['sales_amount'].sum() * 100)
    
    fig = go.Figure(data=[go.Pie(
        labels=sales_by_type['customer_type'],
        values=sales_by_type['sales_percentage'],
        hole=.4,
        textinfo='label+percent',
        marker=dict(colors=['#3498db', '#e74c3c', '#2ecc71'])
    )])
    
    fig.update_layout(
        title='Sales Distribution by Customer Type',
        annotations=[dict(text='Customer<br>Segments', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    return fig

def create_regional_performance(sales_df):
    """Create regional performance heatmap"""
    regional_monthly = sales_df.pivot_table(
        index=sales_df['date'].dt.strftime('%Y-%m'),
        columns='region',
        values='sales_amount',
        aggfunc='sum'
    )
    
    # Calculate YoY growth for each region
    yoy_growth = pd.DataFrame()
    for region in regional_monthly.columns:
        yoy_growth[region] = regional_monthly[region].pct_change(12) * 100
    
    fig = go.Figure(data=go.Heatmap(
        z=yoy_growth.values,
        x=yoy_growth.columns,
        y=yoy_growth.index,
        colorscale='RdYlBu',
        text=np.round(yoy_growth.values, 1),
        texttemplate='%{text:.1f}%',
        textfont={"size": 10},
        colorbar=dict(title='YoY Growth %')
    ))
    
    fig.update_layout(
        title='Regional YoY Growth Heatmap',
        xaxis_title='Region',
        yaxis_title='Month'
    )
    return fig

def create_product_performance(sales_df, products_df):
    """Create product performance analysis"""
    product_sales = pd.merge(sales_df, products_df, on='product_name')
    quarterly_sales = product_sales.groupby([
        pd.Grouper(key='date', freq='Q'),
        'category'
    ])['sales_amount'].sum().reset_index()
    
    fig = px.bar(quarterly_sales,
                 x='date',
                 y='sales_amount',
                 color='category',
                 title='Quarterly Sales by Product Category',
                 labels={'date': 'Quarter',
                        'sales_amount': 'Sales Amount ($)',
                        'category': 'Product Category'})
    
    return fig

def create_delivery_performance(sales_df):
    """Create delivery performance analysis"""
    monthly_delivery = sales_df.groupby([
        pd.Grouper(key='date', freq='M'),
        'delivery_status'
    ])['units_sold'].sum().reset_index()
    
    # Pivot the data for plotting
    delivery_pivot = monthly_delivery.pivot(
        index='date',
        columns='delivery_status',
        values='units_sold'
    ).fillna(0)
    
    # Calculate fulfillment rate
    delivery_pivot['fulfillment_rate'] = (
        delivery_pivot['delivered'] / 
        (delivery_pivot['delivered'] + delivery_pivot['pending']) * 100
    )
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bars for delivered and pending
    fig.add_trace(
        go.Bar(x=delivery_pivot.index, 
               y=delivery_pivot['delivered'],
               name='Delivered',
               marker_color='#2ecc71'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(x=delivery_pivot.index,
               y=delivery_pivot['pending'],
               name='Pending',
               marker_color='#e74c3c'),
        secondary_y=False
    )
    
    # Add line for fulfillment rate
    fig.add_trace(
        go.Scatter(x=delivery_pivot.index,
                  y=delivery_pivot['fulfillment_rate'],
                  name='Fulfillment Rate',
                  line=dict(color='#3498db', width=3)),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Monthly Delivery Performance',
        barmode='stack',
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Units", secondary_y=False)
    fig.update_yaxes(title_text="Fulfillment Rate (%)", secondary_y=True)
    
    return fig

def generate_full_report():
    """Generate and save all reports"""
    # Create reports directory if it doesn't exist
    if not os.path.exists('html_reports'):
        os.makedirs('html_reports')
    
    # Load data
    sales_df, customers_df, products_df = load_data()
    
    # Generate all visualizations
    sales_summary = create_sales_summary(sales_df)
    monthly_trend = create_monthly_trend(sales_df)
    customer_dist = create_customer_distribution(sales_df, customers_df)
    regional_perf = create_regional_performance(sales_df)
    product_perf = create_product_performance(sales_df, products_df)
    delivery_perf = create_delivery_performance(sales_df)
    
    # Create a single-row dashboard
    dashboard = make_subplots(
        rows=2, cols=3,
        subplot_titles=("Sales Summary", "Monthly Trend", "Customer Distribution",
                       "Regional Performance", "Product Performance", "Delivery Performance"),
        specs=[[{"type": "indicator"}, {"type": "xy"}, {"type": "domain"}],
               [{"type": "heatmap"}, {"type": "bar"}, {"type": "xy"}]],
        horizontal_spacing=0.05,
        vertical_spacing=0.12
    )
    
    # Add plots to dashboard
    dashboard.add_trace(sales_summary.data[0], row=1, col=1)
    dashboard.add_trace(monthly_trend.data[0], row=1, col=2)
    dashboard.add_trace(monthly_trend.data[1], row=1, col=2)
    dashboard.add_trace(customer_dist.data[0], row=1, col=3)
    dashboard.add_trace(regional_perf.data[0], row=2, col=1)
    dashboard.add_trace(product_perf.data[0], row=2, col=2)
    dashboard.add_trace(delivery_perf.data[0], row=2, col=3)
    dashboard.add_trace(delivery_perf.data[1], row=2, col=3)
    
    # Update layout with styling
    dashboard.update_layout(
        height=1200,
        width=2400,
        title_text="Pharma Sales Performance Dashboard",
        showlegend=True,
        template="plotly_dark",
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#262626',
        font=dict(color='white'),
        title=dict(
            font=dict(size=24, color='white'),
            x=0.5,
            y=0.98
        ),
        margin=dict(t=100, l=50, r=50, b=50)
    )
    
    # Update axes styling
    dashboard.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#404040')
    dashboard.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#404040')
    
    # Save dashboard with custom HTML wrapper
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pharma Sales Dashboard</title>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background-color: #1e1e1e;
                color: white;
                font-family: Arial, sans-serif;
            }}
            .dashboard-container {{
                max-width: 100%;
                margin: auto;
                background-color: #262626;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .header h1 {{
                color: white;
                margin: 0;
                padding: 10px;
            }}
            .date-range {{
                color: #888;
                font-size: 14px;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            <div class="header">
                <h1>Pharma Sales KPI Dashboard</h1>
                <div class="date-range">Data Range: {sales_df['date'].min().strftime('%Y-%m-%d')} to {sales_df['date'].max().strftime('%Y-%m-%d')}</div>
            </div>
            {dashboard.to_html(full_html=False, include_plotlyjs=True)}
        </div>
    </body>
    </html>
    """
    
    with open("html_reports/full_dashboard.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    
    print("Full report generated successfully!")
    print("Reports are available in the 'html_reports' directory")

if __name__ == "__main__":
    generate_full_report() 