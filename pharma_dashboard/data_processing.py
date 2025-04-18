import pandas as pd
import requests
from pathlib import Path
import io

def download_and_process_data(data_dir=None):
    """Download and process the pharmaceutical data"""
    if data_dir is None:
        data_dir = Path.cwd() / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # URL of the Excel file
    excel_url = "https://github.com/Dogukan-gur/Pharmaceutical-Company-s-Wholesale-Retail-Data/files/10006360/Pharm.Data.xlsx"
    
    try:
        # Download the file
        print("Downloading data...")
        response = requests.get(excel_url)
        response.raise_for_status()
        
        # Read Excel file
        print("Processing data...")
        excel_data = pd.read_excel(io.BytesIO(response.content))
        
        # Process and split data into relevant tables
        # Sales data
        sales_df = excel_data[['Invoice ID', 'Date', 'Customer', 'Product', 'Quantity', 'Unit Price', 'Total']].copy()
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])
        
        # Products data
        products_df = excel_data[['Product', 'Category']].drop_duplicates().reset_index(drop=True)
        products_df['product_id'] = products_df.index + 1
        
        # Customers data
        customers_df = excel_data[['Customer', 'Region', 'Customer Type']].drop_duplicates().reset_index(drop=True)
        customers_df['customer_id'] = customers_df.index + 1
        
        # Save processed data
        sales_df.to_csv(data_dir / 'processed_sales.csv', index=False)
        products_df.to_csv(data_dir / 'processed_products.csv', index=False)
        customers_df.to_csv(data_dir / 'processed_customers.csv', index=False)
        
        print("Data processed and saved successfully!")
        return sales_df, products_df, customers_df
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return None, None, None 