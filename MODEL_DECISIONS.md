# Sales and delivery model decisions

## Count a shipment once

A late three-line order and an on-time one-line order represent two deliveries. The warehouse delivered one of two on time (50%). A sales-line join produces four rows, only one of which is on time (25%). The result would depend on the size of the basket.

The model keeps a separate shipment fact. Date, customer and warehouse filter both facts in one direction. Product filters sales only. For a daily view of revenue alongside delivery volume, aggregate each fact to order date first. Query 4 in [analytics.sql](analytics.sql) joins those aggregates to the calendar so days with no activity are visible.

## Count returns in the right denominator

Of 10,000 orders, 550 were cancelled before shipment. Of the remaining 9,450 orders, 757 were returned. The fulfilled-order return rate is 8.01%. Dividing by all orders would give 7.57% and mix pre-shipment cancellations into an after-fulfillment metric. A returned order still counts as an outbound shipment and contributes zero net sales after the full refund.

## Interpret a warehouse comparison

Compare both the late shipment count and the on-time rate. The rate describes service reliability, while the count shows how many orders missed their promise. Compare the same order-date range across warehouses. The current snapshot contains completed deliveries, so an open-order backlog would require a separate measure with an explicit as-of date.

## Limits of the current grain

An order can have several products but only one shipment in this model. A category-specific delivery question needs a definition of attribution for mixed baskets. If the business introduces split shipments, give each shipment its own key and map shipped quantities to order lines. The existing order-level shipment count would then understate outbound volume.
