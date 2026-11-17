# Fabric setup and report walkthrough

## 1. Prepare the files

Use `sample_data.zip`, or run the generator as described in the README. The local
generator uses Python's standard library. The Fabric notebook needs the PySpark
runtime provided by Fabric; it is not a local Python script.

## 2. Create a demo lakehouse

In a workspace assigned to Fabric capacity or an eligible trial, create a new
lakehouse named `commerce_demo`. Keep **Lakehouse schemas** enabled. Do not use
a lakehouse with production tables for this exercise.

In Files, create a `commerce` folder and upload the **six extracted CSV files** there.
The Spark paths should look like `Files/commerce/fact_sales.csv`. Keep `manifest.json`
alongside them for reconciliation. Upload the files themselves, not the ZIP.

## 3. Import and run the notebook

Import `fabric_load.ipynb` into Fabric. Attach `commerce_demo` as the default lakehouse.
Review the first code cell. `BASE_PATH` is `Files/commerce`; adjust it only if you
used a different folder. Run all cells in order.

The notebook reads with explicit types, removes identical duplicate rows, rejects
conflicting primary keys and missing required fields, checks foreign keys and
financial rules, and then writes six Delta tables in `dbo`.

By default it refuses to replace existing output tables. For a deliberate full
refresh in this **demo lakehouse**, set `REPLACE_DEMO_TABLES = True` and rerun.
That setting replaces the six project tables. Writes are separate per table,
not a multi-table transaction; rerun the full notebook after any failed load.

## 4. Query and reconcile

Switch to the lakehouse's **SQL analytics endpoint** after table synchronization.
Run the statements in `analytics.sql`. The endpoint reads Delta table data;
perform ingestion and table-data changes through the Spark notebook.

Compare the total net sales with `manifest.json`: divide `net_sales_cents` by 100.
Compare table counts too. Do not proceed to reporting if these differ.

## 5. Build the semantic model

Create a new semantic model from the six Delta tables. Use Direct Lake if available
in your capacity/setup. As an alternative learning path, connect Power BI Desktop
to the SQL analytics endpoint using Import, and document that storage-mode choice.
Create these **one-to-many, single-direction** relationships:

| One side | Many side |
| --- | --- |
| `dim_date[date_key]` | `fact_sales[order_date_key]` |
| `dim_date[date_key]` | `fact_shipments[order_date_key]` |
| `dim_customer[customer_key]` | `fact_sales[customer_key]` |
| `dim_customer[customer_key]` | `fact_shipments[customer_key]` |
| `dim_warehouse[warehouse_key]` | `fact_sales[warehouse_key]` |
| `dim_warehouse[warehouse_key]` | `fact_shipments[warehouse_key]` |
| `dim_product[product_key]` | `fact_sales[product_key]` |

Do not create a direct relationship between the two facts. Mark `dim_date` as the
date table using its unique, continuous `date` column. Sort `month_name` by
`month_number`. Hide technical keys from report consumers. Set monetary formats
to INR, percentages to percent, and keys to Do not summarize.

Create each measure in `measures.dax` separately. Its expressions are a reference,
not a file that automatically deploys a semantic model.

## 6. Build two report pages

| Page | Suggested visuals | Slicers |
| --- | --- | --- |
| Sales and returns | Net Sales card; Fulfilled Orders card; Return Rate card; monthly net sales line chart; category net sales bar chart | Date, customer region, category |
| Delivery performance | Shipments card; On-Time Delivery Rate card; Average Delivery Days card; warehouse comparison | Order date, warehouse region, customer region |

Avoid a product slicer on the delivery page: product does not filter the shipment
fact in this model. Returned shipments are included in delivery performance.
YTD is based on order date; the dataset contains a single order year, so do not
claim year-over-year analysis from this sample.

## 7. Record evidence

After validation, add screenshots of the relationship diagram and report, a note
with your run date and Fabric runtime, and results of the SQL reconciliation.
Save a `.pbip` project if available. Never commit secrets, connection tokens, or
real customer data. Update `VALIDATION.md` with what you personally verified.

## References checked 2026-11-17

- [Notebook loading and paths](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-notebook-load-data)
- [Lakehouse schemas](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-schemas)
- [SQL analytics endpoint](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-sql-analytics-endpoint)
- [DP-600 study guide](https://learn.microsoft.com/credentials/certifications/resources/study-guides/dp-600)

Interfaces and exam objectives can change. This repository does not provision a
workspace, enable billable capacity, or deploy a report automatically.
