# Commerce and fulfillment analytics

How much revenue remains after refunds, and how often does a warehouse deliver by its promised date? This Microsoft Fabric project answers both questions from the same orders. Sales are recorded by order line. Delivery is measured once per shipment.

## Operating snapshot

The reproducible 2025 order book covers five warehouses. The figures below come from the 10,000-order run with seed 600.

| Measure | Result | Calculation |
| --- | ---: | --- |
| Fulfilled orders | 9,450 | 10,000 placed less 550 cancellations |
| Net sales | ₹533,653,449.78 | ₹582,378,313.68 after discounts less ₹48,724,863.90 in refunds |
| Return rate | 8.01% | 757 returned orders divided by 9,450 fulfilled |
| On-time delivery | 79.31% | 7,495 deliveries on or before promise divided by 9,450 shipments |

**Why the model has two facts.** Joining shipments to sales lines by order ID expands 9,450 shipments to 23,634 rows. A four-line order would carry four times the weight of a single-line order in a delivery KPI. The warehouse query counts shipments directly. The daily comparison aggregates each fact by order date before joining the results. [Inspect the SQL](analytics.sql) and the [worked modeling example](MODEL_DECISIONS.md).

## Explore the implementation

| Question | Implementation |
| --- | --- |
| How does the load handle duplicate keys and invalid monetary amounts? | [PySpark ingestion notebook](fabric_load.ipynb) |
| How do refunds and cancellations affect sales? | [Data dictionary and business rules](DATA_DICTIONARY.md) |
| Which dimensions can filter delivery performance? | [Model relationships and report setup](FABRIC_SETUP.md) |
| How do the metrics respond to report filters? | [DAX measures](measures.dax) |
| How do the totals reconcile? | [Validation record](VALIDATION.md) |

## Reproduce the numbers

From the repository root, use Python 3.10+ and an empty output directory.

```sh
python generate_data.py --orders 10000 --seed 600 --output data/commerce
python -m unittest -v test_data.py
```

The generator writes six CSV files and a manifest with row counts, financial totals in paise and SHA-256 checksums. The [200-order extract](sample_data.zip) uses the same schema and has its own control totals.

For Fabric, upload the six CSVs, attach the lakehouse to the notebook and validate the Delta tables against the manifest. Then use the SQL endpoint and semantic model to reconcile the same measures. [Fabric setup](FABRIC_SETUP.md).

[MIT license](LICENSE)
