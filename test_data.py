"""Business-grain and reconciliation tests; no external dependencies."""
import csv
import hashlib
import tempfile
import unittest
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from generate_data import generate


class CommerceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name) / "a"
        cls.manifest = generate(cls.root, orders=400, seed=600)
        cls.tables = {}
        for name in cls.manifest["row_counts"]:
            with (cls.root / f"{name}.csv").open(encoding="utf-8", newline="") as stream:
                cls.tables[name] = list(csv.DictReader(stream))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_grain_and_foreign_keys(self):
        sales = self.tables["fact_sales"]
        self.assertEqual(len(sales), len({r["sales_line_key"] for r in sales}))
        self.assertEqual(len({r["order_id"] for r in sales}), 400)
        for fact in ("fact_sales", "fact_shipments"):
            for key, dim in [("customer_key", "dim_customer"), ("warehouse_key", "dim_warehouse"),
                             ("order_date_key", "dim_date")]:
                dimkey = "date_key" if key == "order_date_key" else key
                members = {r[dimkey] for r in self.tables[dim]}
                self.assertTrue(all(r[key] in members for r in self.tables[fact]))
        self.assertTrue({r["product_key"] for r in sales} <= {r["product_key"] for r in self.tables["dim_product"]})

    def test_money_and_order_status(self):
        statuses = defaultdict(set)
        total = Decimal(0)
        for row in self.tables["fact_sales"]:
            statuses[row["order_id"]].add(row["order_status"])
            sales, refund, net = [Decimal(row[c]) for c in
                                  ("sales_before_refunds_inr", "refund_inr", "net_sales_inr")]
            gross = int(row["quantity"]) * Decimal(row["unit_price_inr"])
            self.assertGreaterEqual(Decimal(row["discount_inr"]), 0)
            self.assertLessEqual(Decimal(row["discount_inr"]), gross)
            self.assertEqual(sales - refund, net)
            self.assertEqual(sales, 0 if row["order_status"] == "CANCELLED" else gross - Decimal(row["discount_inr"]))
            self.assertEqual(refund, sales if row["order_status"] == "RETURNED" else 0)
            total += net
        self.assertTrue(all(len(s) == 1 for s in statuses.values()))
        self.assertEqual(int(total * 100), self.manifest["totals"]["net_sales_cents"])
        self.assertEqual(set.union(*statuses.values()), {"COMPLETED", "CANCELLED", "RETURNED"})

    def test_shipments_do_not_duplicate_order_grain(self):
        shipments = self.tables["fact_shipments"]
        self.assertEqual(len(shipments), len({r["order_id"] for r in shipments}))
        order_ids = {r["order_id"] for r in self.tables["fact_sales"] if r["order_status"] != "CANCELLED"}
        self.assertEqual({r["order_id"] for r in shipments}, order_ids)
        for row in shipments:
            order_date = date.fromisoformat(f'{row["order_date_key"][:4]}-{row["order_date_key"][4:6]}-{row["order_date_key"][6:]}')
            delivery = date.fromisoformat(row["delivered_date"])
            promise = date.fromisoformat(row["promised_date"])
            self.assertEqual(int(row["on_time_flag"]), int(delivery <= promise))
            self.assertEqual(int(row["delivery_days"]), (delivery - order_date).days)
            self.assertGreaterEqual(delivery, order_date)

    def test_manifest_counts_and_hashes(self):
        for name, rows in self.tables.items():
            self.assertEqual(len(rows), self.manifest["row_counts"][name])
        for filename, checksum in self.manifest["sha256"].items():
            self.assertEqual(hashlib.sha256((self.root / filename).read_bytes()).hexdigest(), checksum)

    def test_reproducible_and_seed_sensitive(self):
        second = Path(self.temp.name) / "b"
        third = Path(self.temp.name) / "c"
        self.assertEqual(generate(second, 400, 600), self.manifest)
        self.assertNotEqual(generate(third, 400, 601)["sha256"], self.manifest["sha256"])

    def test_refuses_existing_data_and_invalid_size(self):
        before = (self.root / "manifest.json").read_bytes()
        with self.assertRaises(ValueError):
            generate(self.root, 10)
        self.assertEqual(before, (self.root / "manifest.json").read_bytes())
        with self.assertRaises(ValueError):
            generate(Path(self.temp.name) / "invalid", 0)


if __name__ == "__main__":
    unittest.main()
