import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_sales_data(sales_df, products_df, customers_df):
    """Preprocess sales data to match expected format"""
    try:
        # Convert date column to datetime before merging
        sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')
        
        # Drop rows with null dates
        if sales_df['Date'].isnull().any():
            logger.warning(f"Dropping {sales_df['Date'].isnull().sum()} rows with null dates")
            sales_df = sales_df.dropna(subset=['Date'])
        
        # Merge sales with products
        sales_df = sales_df.merge(
            products_df[['Product', 'Category', 'product_id']],
            on='Product',
            how='left'
        )
        
        # Merge with customers to get region
        sales_df = sales_df.merge(
            customers_df[['Customer', 'Region']],
            on='Customer',
            how='left'
        )
        
        # Rename columns to match expected format
        sales_df = sales_df.rename(columns={
            'Date': 'date',
            'Product': 'product_name',
            'Customer': 'customer_id',
            'Quantity': 'units_sold',
            'Total': 'sales_amount',
            'Region': 'region',
            'Category': 'category'
        })
        
        # Fill missing values
        sales_df['region'] = sales_df['region'].fillna('Unknown')
        sales_df['category'] = sales_df['category'].fillna('Unknown')
        
        # Validate data
        validate_sales_data(sales_df)
        
        return sales_df
    except Exception as e:
        logger.error(f"Error preprocessing sales data: {str(e)}")
        raise

def validate_sales_data(df):
    """Validate sales data for required columns and data types"""
    required_columns = ['date', 'product_name', 'customer_id', 'units_sold', 'sales_amount', 'region', 'category']
    
    # Check for missing columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Check for null values
    null_counts = df.isnull().sum()
    if null_counts.any():
        logger.warning(f"Null values found in columns: {null_counts[null_counts > 0]}")
    
    # Validate data types
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        raise ValueError("Date column must be datetime type")
    
    if not pd.api.types.is_numeric_dtype(df['units_sold']):
        raise ValueError("Units sold must be numeric")
    
    if not pd.api.types.is_numeric_dtype(df['sales_amount']):
        raise ValueError("Sales amount must be numeric")
    
    return True

def load_and_preprocess_data():
    """Load and preprocess all data files"""
    try:
        data_dir = Path(__file__).parent.parent / 'data'
        
        # Load raw data
        sales_df = pd.read_csv(data_dir / 'sales.csv')
        products_df = pd.read_csv(data_dir / 'products.csv')
        customers_df = pd.read_csv(data_dir / 'customers.csv')
        
        # Preprocess sales data
        sales_df = preprocess_sales_data(sales_df, products_df, customers_df)
        
        return sales_df, products_df, customers_df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise 