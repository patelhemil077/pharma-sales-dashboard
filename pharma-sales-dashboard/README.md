# Pharmaceutical Sales Dashboard

A Streamlit-based interactive dashboard for analyzing pharmaceutical sales data, providing insights into sales trends, product performance, and regional distribution.

## Features

- 📊 Interactive visualizations
- 🔄 Real-time data filtering
- 📱 Responsive design
- 🔍 Detailed sales analytics
- 📈 Trend analysis
- 🌍 Regional performance tracking

## Dashboard Screenshots

### Sales Overview
![Sales Overview Dashboard](docs/images/dashboard_overview.png)

**Key Metrics:**
- Total Sales: $2,083,417.33
- Total Units Sold: 37,809
- Average Order Value: $2,854.00
- Total Orders: 730

### Product Performance
![Product Performance](docs/images/product_performance.png)

**Product Analysis:**
- Top performing products led by Amoxicillin
- Category-wise performance breakdown
- Sales distribution by region
- Interactive filters for detailed analysis

## Project Structure
```
pharma-sales-dashboard/
├── data/               # Sample data files
│   ├── sales.csv      # Sales transaction data
│   ├── products.csv   # Product information
│   └── customers.csv  # Customer information
├── pharma_dashboard/  # Main application package
│   ├── dashboard.py   # Streamlit dashboard implementation
│   └── data_processor.py  # Data processing and validation
├── tests/            # Unit tests
├── docs/             # Documentation
├── requirements.txt  # Python dependencies
├── setup.py         # Package installation script
├── LICENSE          # MIT License
└── README.md        # Project documentation
```

## Data Requirements
- Sales transaction data with dates, products, and amounts
- Product catalog with categories and pricing
- Customer information for segmentation
- Regional sales data for geographical analysis

## Installation & Usage
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the dashboard: `streamlit run pharma_dashboard/dashboard.py`
4. Access via browser at `http://localhost:8501`

## Technical Stack
- Python 3.8+
- Streamlit for dashboard interface
- Pandas for data processing
- Plotly for interactive visualizations

## License
MIT License - See LICENSE file for details

## Contact
For questions or suggestions, please contact the BI team. 