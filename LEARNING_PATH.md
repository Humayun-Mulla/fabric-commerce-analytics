# Practice plan

Start with the official DP-600 study guide. This is a set of focused exercises,
not a replacement for the full curriculum or an exam readiness claim.

| Session | Do | Evidence |
| --- | --- | --- |
| 1 | Generate data and explain order-line versus order grain | Manifest plus explanation of duplicate shipment counts from a direct fact join |
| 2 | Load explicit schemas in Fabric and inspect Delta tables | Successful notebook output and row counts |
| 3 | Run SQL, then write your own regional return-rate query | SQL plus reconciled totals |
| 4 | Build the star schema and create the DAX measures | Relationship diagram and metric checks |
| 5 | Build sales and delivery report pages | Report screenshots and observations |
| 6 | Compare Import versus Direct Lake behavior in your environment | Storage-mode decision and measured observations |
| 7 | Create a test RLS role on customer region, test allowed and denied users | Written test results; do not publish access until tested |
| 8 | Add an incremental-load design and document update/delete handling | Design and tests; no claim of implemented CDC |

## Small challenges

1. Compute fulfilled orders with SQL without counting lines as orders.
2. Explain why a returned order has a shipment but contributes zero net sales.
3. Deliberately duplicate a CSV row; check that exact duplicates are removed.
4. Change a duplicate row's price; verify the conflicting key is rejected.
5. Add a product key not present in the dimension; verify the orphan is rejected.
6. Explain why category filters do not change the delivery KPI in this model.
7. Extend the data to a second year, then add a year-over-year measure.

## Coverage and gaps

The current starter practices ingestion, data types, quality checks, star schemas,
SQL aggregation, relationships, and DAX measures. Governance, deployment pipelines,
XMLA, advanced security, KQL/Eventhouse, calculation groups, composite models,
incremental refresh, and performance benchmarking need additional labs.

## Community contribution ideas

Useful early contributions include running the notebook in Fabric and documenting
issues, adding a reproducible bug case, improving accessibility of the report,
or extending the generator with tested partial-return logic.
Project adoption, stars, and external contributions must be earned and reported accurately.
