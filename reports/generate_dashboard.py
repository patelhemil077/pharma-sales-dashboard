import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore
from plotly.subplots import make_subplots # type: ignore
from datetime import datetime
import os

def load_data():
    """Load the processed CSV files"""
    sales_df = pd.read_csv('../data/processed_sales.csv')
    customers_df = pd.read_csv('../data/processed_customers.csv')
    products_df = pd.read_csv('../data/processed_products.csv')
    
    # Convert date column
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    return sales_df, customers_df, products_df 