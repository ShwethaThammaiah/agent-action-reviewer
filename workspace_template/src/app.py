"""A tiny stand-in for a real service: prints the items that are low on stock."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
settings = json.loads((ROOT / "config" / "settings.json").read_text())

with (ROOT / "data" / "inventory.csv").open() as file:
    for row in csv.DictReader(file):
        if int(row["quantity"]) < settings["low_stock_threshold"]:
            print(f"Low stock: {row['item']} ({row['quantity']} left)")
