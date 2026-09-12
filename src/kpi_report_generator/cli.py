from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

REQUIRED_COLUMNS = ("month", "revenue", "cost")


class ValidationError(ValueError):
    """Raised when an input CSV cannot support a reliable KPI calculation."""


@dataclass(frozen=True)
class Record:
    month: str
    revenue: Decimal
    cost: Decimal


def load_records(path: Path) -> list[Record]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = [column for column in REQUIRED_COLUMNS if column not in columns]
        if missing:
            raise ValidationError(f"missing required columns: {', '.join(missing)}")

        records: list[Record] = []
        for row_number, row in enumerate(reader, start=2):
            month = (row["month"] or "").strip()
            if not month:
                raise ValidationError(f"row {row_number}: month must not be blank")
            revenue = parse_amount(row["revenue"], "revenue", row_number)
            cost = parse_amount(row["cost"], "cost", row_number)
            records.append(Record(month=month, revenue=revenue, cost=cost))

    if not records:
        raise ValidationError("input CSV must contain at least one data row")
    return records


def parse_amount(value: str | None, name: str, row_number: int) -> Decimal:
    try:
        amount = Decimal((value or "").strip())
    except InvalidOperation as error:
        raise ValidationError(f"row {row_number}: {name} must be a number") from error
    if not amount.is_finite() or amount < 0:
        raise ValidationError(f"row {row_number}: {name} must be non-negative")
    return amount


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown KPI report from a CSV file.")
    parser.add_argument("--input", required=True, type=Path, help="CSV input file")
    parser.add_argument("--output", required=True, type=Path, help="Markdown report path")
    parser.add_argument("--title", default="KPI Report", help="Report title")
    args = parser.parse_args(argv)

    try:
        records = load_records(args.input)
    except (OSError, ValidationError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    revenue = sum((record.revenue for record in records), Decimal())
    cost = sum((record.cost for record in records), Decimal())
    profit = revenue - cost
    margin = profit / revenue * Decimal("100") if revenue else Decimal()
    report = "\n".join(
        [
            f"# {args.title}",
            "",
            f"Source rows: {len(records)}",
            "",
            "| KPI | Value |",
            "| --- | ---: |",
            f"| Revenue | ${revenue:,.2f} |",
            f"| Cost | ${cost:,.2f} |",
            f"| Profit | ${profit:,.2f} |",
            f"| Profit margin | {margin:.1f}% |",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
