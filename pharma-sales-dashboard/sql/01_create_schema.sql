-- Create the main sales table
CREATE TABLE IF NOT EXISTS pharma_sales (
    transaction_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    sales_amount DECIMAL(10,2) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    units_sold INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create customer dimension table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_type VARCHAR(50) NOT NULL,  -- Hospital, Doctor, Pharmacy
    region VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create product dimension table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_sales_date ON pharma_sales(date);
CREATE INDEX idx_sales_region ON pharma_sales(region);
CREATE INDEX idx_sales_customer ON pharma_sales(customer_id);
CREATE INDEX idx_sales_product ON pharma_sales(product_name); 