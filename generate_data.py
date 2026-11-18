"""Generate reproducible commerce order books using Python's standard library."""
import argparse
import csv
import hashlib
import json
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path


def money(cents):
    return f"{Decimal(cents) / 100:.2f}"


def generate(output, orders=10000, seed=600):
    if orders < 1:
        raise ValueError("orders must be at least 1")
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output must be empty: choose a new directory to preserve existing data")
    output.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    counts = {}
    hashes = {}

    def write(name, columns, rows):
        path = output / (name + ".csv")
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(columns)
            count = 0
            for row in rows:
                writer.writerow(row)
                count += 1
        counts[name] = count
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()

    locations = [("Bengaluru", "South"), ("Chennai", "South"),
                 ("Mumbai", "West"), ("Delhi", "North"), ("Kolkata", "East")]
    write("dim_customer", ["customer_key", "customer_label", "city", "region"],
          ((i, f"Customer {i:05}", *locations[(i - 1) % 5]) for i in range(1, 1001)))
    categories = ["Electronics", "Home", "Books", "Clothing", "Sports"]
    prices = {i: rng.randint(19900, 2499900) for i in range(1, 101)}
    write("dim_product", ["product_key", "product_label", "category", "list_price_inr"],
          ((i, f"Product {i:03}", categories[(i - 1) % 5], money(prices[i])) for i in prices))
    write("dim_warehouse", ["warehouse_key", "warehouse_label", "city", "region"],
          ((i, f"Warehouse {i:02}", *locations[i - 1]) for i in range(1, 6)))
    dates = [date(2025, 1, 1) + timedelta(days=i) for i in range(365)]
    write("dim_date", ["date_key", "date", "year", "month_number", "month_name", "day_of_week"],
          ((int(d.strftime("%Y%m%d")), d.isoformat(), d.year, d.month,
            ("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec").split()[d.month - 1],
            d.isoweekday()) for d in dates))
    shipments = []
    status_counts = {"COMPLETED": 0, "RETURNED": 0, "CANCELLED": 0}
    totals = {"sales_before_refunds_cents": 0, "refund_cents": 0, "net_sales_cents": 0}

    def sales_rows():
        for order in range(1, orders + 1):
            order_id = f"ORD{order:09}"
            order_date = rng.choices(dates, weights=[3 if d.month in (10, 11, 12) else 1 for d in dates])[0]
            date_key = int(order_date.strftime("%Y%m%d"))
            customer = rng.randint(1, 1000)
            warehouse = rng.randint(1, 5)
            status = rng.choices(["COMPLETED", "RETURNED", "CANCELLED"], [87, 8, 5])[0]
            status_counts[status] += 1
            if status != "CANCELLED":
                promise = order_date + timedelta(days=rng.randint(2, 6))
                offset = rng.choices([-1, 0, 1, 3], [20, 60, 15, 5])[0]
                delivery = promise + timedelta(days=offset)
                shipments.append((order_id, date_key, customer, warehouse, promise.isoformat(),
                                  delivery.isoformat(), int(delivery <= promise),
                                  (delivery - order_date).days))
            for line in range(1, rng.randint(1, 4) + 1):
                product = rng.randint(1, 100)
                qty = rng.randint(1, 3)
                gross = prices[product] * qty
                discount = gross * rng.choice([0, 0, 5, 10, 15]) // 100
                sales = gross - discount if status != "CANCELLED" else 0
                refund = sales if status == "RETURNED" else 0
                totals["sales_before_refunds_cents"] += sales
                totals["refund_cents"] += refund
                totals["net_sales_cents"] += sales - refund
                yield (f"{order_id}-{line}", order_id, line, date_key, customer, product,
                       warehouse, status, qty, money(prices[product]), money(discount),
                       money(sales), money(refund), money(sales - refund))

    write("fact_sales", ["sales_line_key", "order_id", "line_number", "order_date_key", "customer_key",
          "product_key", "warehouse_key", "order_status", "quantity", "unit_price_inr",
          "discount_inr", "sales_before_refunds_inr", "refund_inr", "net_sales_inr"], sales_rows())
    write("fact_shipments", ["order_id", "order_date_key", "customer_key", "warehouse_key", "promised_date",
          "delivered_date", "on_time_flag", "delivery_days"], shipments)
    manifest = {"project": "fabric-commerce-analytics", "synthetic": True, "seed": seed,
                "orders": orders, "currency": "INR", "order_status_counts": status_counts,
                "row_counts": counts, "totals": totals, "sha256": hashes}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    parser.add_argument("--orders", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=600)
    args = parser.parse_args()
    try:
        result = generate(args.output, args.orders, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
