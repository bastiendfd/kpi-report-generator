# KPI Report Generator

A small, dependency-free Python CLI that turns a well-formed financial CSV into a clear Markdown KPI report. It is designed as a focused portfolio example of input validation, deterministic calculations, automated tests, and CI—not as a production finance system.

## What it does

- Reads CSV records with `month`, `revenue`, and `cost` columns.
- Validates required columns, non-empty months, numeric finite values, and non-negative revenue/cost.
- Calculates total revenue, cost, profit, and profit margin.
- Writes a portable Markdown report.
- Includes only synthetic sample data; no real customer, employer, or personal data is included.

## Quick start

Requires Python 3.10+.

```bash
python -m pip install -e ".[dev]"
python -m kpi_report_generator.cli \
  --input data/sample_monthly_financials.csv \
  --output reports/q1-2026.md \
  --title "Q1 2026 KPI Snapshot"
```

The same functionality is available after installation as:

```bash
kpi-report --input data/sample_monthly_financials.csv --output reports/q1-2026.md
```

Example output:

```markdown
# Q1 2026 KPI Snapshot

Source rows: 3

| KPI | Value |
| --- | ---: |
| Revenue | $398,500.00 |
| Cost | $244,550.00 |
| Profit | $153,950.00 |
| Profit margin | 38.6% |
```

## Input format

```csv
month,revenue,cost
2026-01,125000.00,78250.00
```

The CLI returns exit code `2` and prints a useful error message when the CSV has missing columns, blank months, invalid numeric values, negative amounts, or no data rows. Report titles must be single-line plain text: HTML and Markdown formatting syntax are rejected so the title cannot alter the report structure.

## Development

```bash
python -m pytest
```

## Limitations

This project deliberately keeps the reporting scope small. It does not provide accounting controls, currency conversion, period reconciliation, tax treatment, authentication, multi-tenant storage, audit trails, or regulatory compliance. Review source data and outputs before using them for decisions.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.

## License

This repository is available under the [MIT License](LICENSE).
