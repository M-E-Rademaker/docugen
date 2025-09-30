SELECT product_id, COUNT(*) as order_count
FROM order_items
GROUP BY product_id
HAVING COUNT(*) > 10;