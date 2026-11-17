# Data dictionary

The default run has 10,000 orders, 1,000 customers, 100 products, five warehouses,
and 365 date records. Sales line and shipment counts depend on the seed.

## Dimensions

| Table | Columns and meaning |
| --- | --- |
| `dim_date` | `date_key` integer YYYYMMDD; `date` ISO date; `year`; `month_number` 1-12; `month_name` English abbreviation; `day_of_week` ISO Monday=1 |
| `dim_customer` | `customer_key` unique integer; fictional `customer_label`; illustrative `city` and `region` |
| `dim_product` | `product_key` unique integer; fictional `product_label`; `category`; `list_price_inr` decimal(18,2) |
| `dim_warehouse` | `warehouse_key` unique integer; fictional `warehouse_label`; illustrative `city` and `region` |

## Sales: one order line per row

| Column | Type | Rule |
| --- | --- | --- |
| `sales_line_key` | string | Unique order ID plus line number |
| `order_id` | string | Repeats across lines within an order |
| `line_number` | integer | Starts at one within an order |
| `order_date_key` | integer | References `dim_date.date_key` |
| `customer_key` | integer | References `dim_customer` |
| `product_key` | integer | References `dim_product` |
| `warehouse_key` | integer | References `dim_warehouse` |
| `order_status` | string | COMPLETED, RETURNED, or CANCELLED; consistent within an order |
| `quantity` | integer | Ordered quantity, 1-3; includes cancelled/returned lines |
| `unit_price_inr` | decimal(18,2) | Product list price at order time |
| `discount_inr` | decimal(18,2) | Whole-line discount, not a per-unit amount |
| `sales_before_refunds_inr` | decimal(18,2) | Quantity * price - discount; zero for cancellations |
| `refund_inr` | decimal(18,2) | Full sales amount for returned orders; otherwise zero |
| `net_sales_inr` | decimal(18,2) | Sales before refunds minus refunds |

Discounts are calculated in integer paise and rounded down to the paise.
The notebook reads monetary columns as decimals, not floating-point numbers.
Repeated products within an order are allowed as separate lines.

## Shipments: one non-cancelled order per row

| Column | Type | Rule |
| --- | --- | --- |
| `order_id` | string | Unique in this fact |
| `order_date_key` | integer | Order date, not delivery date |
| `customer_key`, `warehouse_key` | integer | Shared dimension keys |
| `promised_date`, `delivered_date` | date | Actual delivery can be after year-end 2025 |
| `on_time_flag` | integer | 1 when delivered_date <= promised_date; otherwise 0 |
| `delivery_days` | integer | Calendar days from order date to delivered date |

Returned orders still had an outbound shipment. This project does not model return transport.
All shipments in this historical snapshot have been delivered; there are no open shipments.
Delivery metrics are analyzed by **order date**. To analyze by delivery date, extend
the date dimension beyond 2025 and add a role-playing date relationship.

## Intentional simplifications

- One country and currency; city/region values are illustrative categories.
- Fixed product prices and no slowly changing dimensions in the starter.
- Weighted order dates give Oct-Dec a higher frequency. These are invented weights.
- Approximate status probabilities: 87% completed, 8% returned, 5% cancelled.
  Actual sample percentages vary. Do not present them as real company statistics.
- One warehouse and one shipment per order; no split shipments or partial returns.
- Local generation holds shipment records in memory. Start at 10,000 orders;
  this is a learning dataset, not an enterprise-scale load benchmark.
- No names, emails, addresses, payment data, or employer information from real people.
