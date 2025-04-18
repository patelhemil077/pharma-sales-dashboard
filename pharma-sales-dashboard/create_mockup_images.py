import matplotlib.pyplot as plt
import numpy as np

# Create directory if it doesn't exist
import os
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