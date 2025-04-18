import matplotlib.pyplot as plt
import numpy as np
import os

# Create directory if it doesn't exist
os.makedirs('docs/images', exist_ok=True)

# Regional Sales Mockup
plt.figure(figsize=(12, 6))
regions = ['North', 'South', 'East', 'West', 'Central']
sales = [2.5, 1.8, 2.2, 1.5, 1.9]
growth = [15, -5, 8, 12, 3]

ax1 = plt.gca()
ax2 = ax1.twinx()

bars = ax1.bar(regions, sales, color='navy', alpha=0.7)
line = ax2.plot(regions, growth, color='red', linewidth=2, marker='o')

ax1.set_ylabel('Sales (M$)')
ax2.set_ylabel('YoY Growth %')
plt.title('Regional Sales Distribution')
plt.savefig('docs/images/regional_sales.png', dpi=300, bbox_inches='tight')
plt.close()

# Customer Segmentation Mockup
plt.figure(figsize=(12, 6))
segments = ['Hospital', 'Clinic', 'Pharmacy']
customers = [350, 280, 100]
avg_order = [5200, 3800, 1500]

ax1 = plt.gca()
ax2 = ax1.twinx()

bars = ax1.bar(segments, customers, color='blue', alpha=0.7)
line = ax2.plot(segments, avg_order, color='orange', linewidth=2, marker='o')

ax1.set_ylabel('Number of Customers')
ax2.set_ylabel('Average Order Value ($)')
plt.title('Customer Segmentation Analysis')
plt.savefig('docs/images/customer_segments.png', dpi=300, bbox_inches='tight')
plt.close()

# Dashboard Overview Mockup
plt.figure(figsize=(12, 6))
dates = ['Jan 1', 'Jan 8', 'Jan 15', 'Jan 22', 'Jan 29', 'Feb 5']
daily_sales = [1.2, 1.8, 1.5, 2.2, 1.9, 2.5]

plt.plot(dates, daily_sales, marker='o', linewidth=2, color='green')
plt.title('Sales Dashboard Overview')
plt.ylabel('Daily Sales (M$)')
plt.grid(True, alpha=0.3)
plt.savefig('docs/images/dashboard_overview.png', dpi=300, bbox_inches='tight')
plt.close()

# Product Performance Mockup
plt.figure(figsize=(12, 6))
products = ['Amoxicillin', 'Lisinopril', 'Metformin', 'Omeprazole']
performance = [95, 82, 78, 88]

plt.bar(products, performance, color='purple', alpha=0.7)
plt.title('Product Performance Analysis')
plt.ylabel('Performance Score')
plt.ylim(0, 100)
plt.savefig('docs/images/product_performance.png', dpi=300, bbox_inches='tight')
plt.close() 