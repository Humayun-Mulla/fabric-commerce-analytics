-- T-SQL: run on the lakehouse SQL analytics endpoint after the notebook completes.
-- Tables use the dbo schema. These queries do not modify data.

-- 1. Net sales by month. Sort by a numeric month rather than the month label.
SELECT d.[year], d.month_number, d.month_name,
       COUNT(DISTINCT CASE WHEN s.order_status <> 'CANCELLED' THEN s.order_id END) AS fulfilled_orders,
       SUM(s.sales_before_refunds_inr) AS sales_before_refunds_inr,
       SUM(s.refund_inr) AS refunds_inr, SUM(s.net_sales_inr) AS net_sales_inr
FROM dbo.fact_sales AS s
JOIN dbo.dim_date AS d ON d.date_key = s.order_date_key
GROUP BY d.[year], d.month_number, d.month_name
ORDER BY d.[year], d.month_number;

-- 2. Product/category performance at the sales-line grain.
SELECT p.category, SUM(s.net_sales_inr) AS net_sales_inr,
       SUM(CASE WHEN s.order_status = 'COMPLETED' THEN s.quantity ELSE 0 END) AS retained_units
FROM dbo.fact_sales AS s
JOIN dbo.dim_product AS p ON p.product_key = s.product_key
GROUP BY p.category ORDER BY net_sales_inr DESC;

-- 3. Warehouse on-time percentage: keep the shipment fact separate from sales lines.
SELECT w.warehouse_label, w.region, COUNT(*) AS shipments,
       100.0 * SUM(h.on_time_flag) / NULLIF(COUNT(*), 0) AS on_time_percent,
       AVG(CAST(h.delivery_days AS decimal(10,2))) AS average_delivery_days
FROM dbo.fact_shipments AS h
JOIN dbo.dim_warehouse AS w ON w.warehouse_key = h.warehouse_key
GROUP BY w.warehouse_label, w.region ORDER BY on_time_percent;

-- 4. Combine facts only AFTER aggregating to a common date grain.
WITH sales_daily AS (
    SELECT order_date_key, SUM(net_sales_inr) AS net_sales_inr
    FROM dbo.fact_sales GROUP BY order_date_key
), shipments_daily AS (
    SELECT order_date_key, COUNT(*) AS shipments, SUM(on_time_flag) AS on_time_shipments
    FROM dbo.fact_shipments GROUP BY order_date_key
)
SELECT d.[date], COALESCE(s.net_sales_inr, 0) AS net_sales_inr,
       COALESCE(h.shipments, 0) AS shipments, COALESCE(h.on_time_shipments, 0) AS on_time_shipments
FROM dbo.dim_date AS d
LEFT JOIN sales_daily AS s ON s.order_date_key = d.date_key
LEFT JOIN shipments_daily AS h ON h.order_date_key = d.date_key
ORDER BY d.[date];

-- 5. Both checks should return zero rows.
SELECT sales_line_key, COUNT(*) AS duplicate_count
FROM dbo.fact_sales GROUP BY sales_line_key HAVING COUNT(*) > 1;
SELECT sales_line_key FROM dbo.fact_sales
WHERE net_sales_inr <> sales_before_refunds_inr - refund_inr;

-- 6. Compare this total with manifest.json totals.net_sales_cents / 100.
SELECT SUM(net_sales_inr) AS net_sales_inr FROM dbo.fact_sales;
