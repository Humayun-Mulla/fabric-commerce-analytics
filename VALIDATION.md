# Validation record

Checked on 2026-11-17 using Python 3.12.14 on Windows.

## Passed locally

- `python -m unittest -v test_data.py`: **6 tests passed**.
- Same-seed generation produced identical manifests and checksums; a different seed changed the data.
- Primary-key, foreign-key, monetary, order-status, and shipment-grain assertions passed.
- Nonempty output folders were protected from overwrite; zero orders were rejected.
- Generated the 200-order sample and a separate 10,000-order dataset.
- Notebook JSON parsed and all code cells passed Python syntax parsing; nbformat not installed locally.
- Relative Markdown file links checked.

| Table | Extract rows (200 orders) | Standard rows (10,000 orders) |
| --- | ---: | ---: |
| `dim_customer` | 1,000 | 1,000 |
| `dim_product` | 100 | 100 |
| `dim_warehouse` | 5 | 5 |
| `dim_date` | 365 | 365 |
| `fact_sales` | 524 | 25,020 |
| `fact_shipments` | 188 | 9,450 |

Extract net sales: **INR 11,228,743.58**.
Standard net sales: **INR 533,653,449.78**.
Both runs used seed 600. The sample ZIP contains the six CSVs and its own manifest.

## Not yet validated

- Execution in a Microsoft Fabric Spark runtime, Delta table writes, and SQL endpoint synchronization.
- T-SQL execution, semantic-model relationships, DAX results, storage-mode behavior, or report visuals.
- Tenant permissions, row-level security, refresh, deployment pipelines, and large-scale performance.

Workspace execution and report reconciliation are pending.

