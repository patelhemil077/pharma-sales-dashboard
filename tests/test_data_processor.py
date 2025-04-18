import pytest
import pandas as pd
from datetime import datetime
from pharma_dashboard.data_processor import preprocess_sales_data, validate_sales_data

@pytest.fixture
def sample_sales_data():
    return pd.DataFrame({
        'Date': ['2023-01-01', '2023-01-02'],
        'Product': ['Aspirin', 'Paracetamol'],
        'Customer': ['Customer_1', 'Customer_2'],
        'Quantity': [10, 20],
        'Unit Price': [5.0, 10.0],
        'Total': [50.0, 200.0]
    })

@pytest.fixture
def sample_products_data():
    return pd.DataFrame({
        'Product': ['Aspirin', 'Paracetamol'],
        'Category': ['Pain Relief', 'Pain Relief'],
        'product_id': [1, 2]
    })

@pytest.fixture
def sample_customers_data():
    return pd.DataFrame({
        'Customer': ['Customer_1', 'Customer_2'],
        'Region': ['East', 'South'],
        'Customer Type': ['Hospital', 'Clinic'],
        'customer_id': [1, 2]
    })

def test_preprocess_sales_data(sample_sales_data, sample_products_data, sample_customers_data):
    processed_data = preprocess_sales_data(sample_sales_data, sample_products_data, sample_customers_data)
    
    # Check column names
    expected_columns = ['date', 'product_name', 'customer_id', 'units_sold', 
                       'sales_amount', 'region', 'category']
    assert all(col in processed_data.columns for col in expected_columns)
    
    # Check data types
    assert pd.api.types.is_datetime64_any_dtype(processed_data['date'])
    assert pd.api.types.is_numeric_dtype(processed_data['units_sold'])
    assert pd.api.types.is_numeric_dtype(processed_data['sales_amount'])
    
    # Check values
    assert processed_data['region'].iloc[0] == 'East'
    assert processed_data['category'].iloc[0] == 'Pain Relief'

def test_validate_sales_data(sample_sales_data, sample_products_data, sample_customers_data):
    processed_data = preprocess_sales_data(sample_sales_data, sample_products_data, sample_customers_data)
    assert validate_sales_data(processed_data) is True

def test_validate_sales_data_missing_columns():
    invalid_data = pd.DataFrame({
        'date': ['2023-01-01'],
        'product_name': ['Aspirin']
    })
    with pytest.raises(ValueError):
        validate_sales_data(invalid_data) 