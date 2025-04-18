-- Year-to-Date Sales
SELECT 
    SUM(sales_amount) as ytd_sales,
    SUM(sales_amount) / LAG(SUM(sales_amount)) OVER (ORDER BY DATE_TRUNC('year', date)) - 1 as yoy_growth
FROM pharma_sales
WHERE date >= DATE_TRUNC('year', CURRENT_DATE);

-- Month-to-Date Sales with Plan Comparison
WITH monthly_plan AS (
    SELECT date_trunc('month', date) as month,
           SUM(sales_amount) as actual_sales,
           1000000 as planned_sales  -- Example target, should be replaced with actual plan data
    FROM pharma_sales
    GROUP BY date_trunc('month', date)
)
SELECT 
    month,
    actual_sales,
    planned_sales,
    (actual_sales / planned_sales - 1) * 100 as plan_variance_percentage
FROM monthly_plan
ORDER BY month DESC;

-- Sales by Customer Group
SELECT 
    c.customer_type,
    SUM(s.sales_amount) as total_sales,
    COUNT(DISTINCT s.customer_id) as customer_count,
    SUM(s.sales_amount) / SUM(SUM(s.sales_amount)) OVER () * 100 as sales_percentage
FROM pharma_sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.customer_type;

-- Monthly Quantity Ordered vs Delivered
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', date) as month,
        SUM(units_sold) as quantity_ordered,
        SUM(CASE WHEN delivery_status = 'delivered' THEN units_sold ELSE 0 END) as quantity_delivered
    FROM pharma_sales
    GROUP BY DATE_TRUNC('month', date)
)
SELECT 
    month,
    quantity_ordered,
    quantity_delivered,
    ROUND((quantity_delivered::FLOAT / NULLIF(quantity_ordered, 0)) * 100, 2) as fulfillment_rate
FROM monthly_metrics
ORDER BY month;

-- Top 5 Customers by Sales
SELECT 
    c.customer_name,
    c.customer_type,
    SUM(s.sales_amount) as total_sales,
    COUNT(DISTINCT DATE_TRUNC('month', s.date)) as months_active
FROM pharma_sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.customer_name, c.customer_type
ORDER BY total_sales DESC
LIMIT 5;

-- YOY Growth by Region
WITH yearly_sales AS (
    SELECT 
        region,
        DATE_TRUNC('year', date) as year,
        SUM(sales_amount) as yearly_sales
    FROM pharma_sales
    GROUP BY region, DATE_TRUNC('year', date)
)
SELECT 
    region,
    year,
    yearly_sales,
    (yearly_sales / LAG(yearly_sales) OVER (PARTITION BY region ORDER BY year) - 1) * 100 as yoy_growth
FROM yearly_sales
ORDER BY region, year;

-- Monthly Churn Rate
WITH customer_activity AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', date) as month,
        LEAD(DATE_TRUNC('month', date)) OVER (PARTITION BY customer_id ORDER BY date) as next_purchase
    FROM pharma_sales
)
SELECT 
    month,
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(DISTINCT CASE WHEN next_purchase IS NULL OR next_purchase > month + INTERVAL '3 months' 
          THEN customer_id END) as churned_customers,
    ROUND((COUNT(DISTINCT CASE WHEN next_purchase IS NULL OR next_purchase > month + INTERVAL '3 months'
          THEN customer_id END)::FLOAT / NULLIF(COUNT(DISTINCT customer_id), 0)) * 100, 2) as churn_rate
FROM customer_activity
GROUP BY month
ORDER BY month; 