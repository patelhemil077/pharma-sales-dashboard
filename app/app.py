from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load and prepare data once at startup
try:
    data_dir = Path(__file__).parent.parent / 'data'
    sales_df = pd.read_csv(data_dir / 'sales.csv')
    
    # Basic data preparation
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    sales_df['Month'] = sales_df['Date'].dt.strftime('%Y-%m')
    
    print("Data loaded successfully!")
except Exception as e:
    print(f"Error loading data: {e}")
    sales_df = pd.DataFrame()

def apply_filters(df, start_date=None, end_date=None, product=None, search=None):
    filtered_df = df.copy()
    
    if start_date:
        start_date = pd.to_datetime(start_date)
        filtered_df = filtered_df[filtered_df['Date'] >= start_date]
    
    if end_date:
        end_date = pd.to_datetime(end_date)
        filtered_df = filtered_df[filtered_df['Date'] <= end_date]
    
    if product and product != 'all':
        filtered_df = filtered_df[filtered_df['Product'] == product]
    
    if search:
        search = search.lower()
        filtered_df = filtered_df[
            filtered_df['Product'].str.lower().str.contains(search) |
            filtered_df['Customer'].str.lower().str.contains(search)
        ]
    
    return filtered_df

@app.route('/api/data/overview', methods=['GET'])
def get_overview():
    try:
        if sales_df.empty:
            return jsonify({'error': 'No data available'}), 500
        
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        product = request.args.get('product')
        search = request.args.get('search')
        
        # Apply filters
        filtered_df = apply_filters(sales_df, start_date, end_date, product, search)
        
        # Calculate metrics
        monthly_sales = filtered_df.groupby('Month')['Total'].sum().reset_index()
        product_sales = filtered_df.groupby('Product')['Total'].sum().reset_index()
        product_sales = product_sales.sort_values('Total', ascending=True)
        
        response = {
            'total_sales': float(filtered_df['Total'].sum()),
            'total_units': int(filtered_df['Quantity'].sum()),
            'total_orders': len(filtered_df),
            'monthly_trend': monthly_sales.to_dict('records'),
            'product_summary': product_sales.to_dict('records'),
            'products': sorted(sales_df['Product'].unique().tolist()),
            'date_range': {
                'min': sales_df['Date'].min().strftime('%Y-%m-%d'),
                'max': sales_df['Date'].max().strftime('%Y-%m-%d')
            }
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error in overview: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 