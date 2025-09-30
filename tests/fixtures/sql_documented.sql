-- # Calculate Customer Revenue
--
-- ## Description
-- This query calculates total revenue per customer by summing up
-- all their order totals. It joins the customers and orders tables
-- and groups results by customer information.
--
-- ## Parameters
-- - None (operates on full dataset)
--
-- ## Returns
-- - customer_id (INTEGER): Unique customer identifier
-- - customer_name (VARCHAR): Full name of customer
-- - total_revenue (DECIMAL): Sum of all order amounts
--
-- ## Example
-- ```sql
-- -- Returns top 10 customers by revenue
-- SELECT * FROM customer_revenue ORDER BY total_revenue DESC LIMIT 10;
-- ```

CREATE VIEW customer_revenue AS
SELECT
    c.customer_id,
    c.customer_name,
    SUM(o.order_total) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;