import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_and_process_data():
    """
    Load and process data from CSV files.
    Implements data validation rules and cleaning.
    """
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    # Load data
    sales_df = pd.read_csv(os.path.join(data_dir, 'sales.csv'))
    products_df = pd.read_csv(os.path.join(data_dir, 'products.csv'))
    customers_df = pd.read_csv(os.path.join(data_dir, 'customers.csv'))

    # Data cleaning and validation
    sales_df = clean_sales_data(sales_df)
    products_df = clean_products_data(products_df)
    customers_df = clean_customers_data(customers_df)

    return sales_df, products_df, customers_df

def clean_sales_data(df):
    """
    Clean and validate sales data.
    """
    # Convert date
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Remove future dates
    df = df[df['Date'] <= datetime.now()]
    
    # Validate quantities and prices
    df = df[df['Quantity'] > 0]
    df = df[df['Unit_Price'] > 0]
    
    # Validate total amount
    df['Calculated_Total'] = df['Quantity'] * df['Unit_Price']
    df = df[np.isclose(df['Total'], df['Calculated_Total'], rtol=1e-05)]
    
    return df

def clean_products_data(df):
    """
    Clean and validate products data.
    """
    # Remove duplicates
    df = df.drop_duplicates(subset=['product_id'])
    
    # Ensure required fields are not null
    df = df.dropna(subset=['Product', 'Category', 'product_id'])
    
    return df

def clean_customers_data(df):
    """
    Clean and validate customers data.
    """
    # Remove duplicates
    df = df.drop_duplicates(subset=['customer_id'])
    
    # Ensure required fields are not null
    df = df.dropna(subset=['Customer', 'Region', 'Customer_Type'])
    
    # Validate customer types
    valid_types = ['Hospital', 'Clinic', 'Pharmacy']
    df = df[df['Customer_Type'].isin(valid_types)]
    
    return df 