-- Calculate total sales
SELECT
    product_id,
    SUM(quantity * price) as total_sales
FROM sales
GROUP BY product_id;