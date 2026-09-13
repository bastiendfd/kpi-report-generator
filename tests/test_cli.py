from __future__ import annotations

import csv
from pathlib import Path

import pytest

from kpi_report_generator.cli import main


def test_cli_generates_markdown_report_with_financial_kpis(tmp_path: Path) -> None:
    source = tmp_path / "input.csv"
    output = tmp_path / "report.md"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["month", "revenue", "cost"])
        writer.writeheader()
        writer.writerows(
            [
                {"month": "2026-01", "revenue": "1200", "cost": "700"},
                {"month": "2026-02", "revenue": "800", "cost": "500"},
            ]
        )

    exit_code = main(["--input", str(source), "--output", str(output), "--title", "Q1 Snapshot"])

    assert exit_code == 0
    report = output.read_text(encoding="utf-8")
    assert "# Q1 Snapshot" in report
    assert "| Revenue | $2,000.00 |" in report
    assert "| Cost | $1,200.00 |" in report
    assert "| Profit | $800.00 |" in report
    assert "| Profit margin | 40.0% |" in report


def test_cli_rejects_missing_required_columns(tmp_path: Path, capsys) -> None:
    source = tmp_path / "missing-cost.csv"
    output = tmp_path / "report.md"
    source.write_text("month,revenue\n2026-01,1200\n", encoding="utf-8")

    exit_code = main(["--input", str(source), "--output", str(output)])

    assert exit_code == 2
    assert "missing required columns: cost" in capsys.readouterr().err
    assert not output.exists()


def test_cli_rejects_negative_revenue(tmp_path: Path, capsys) -> None:
    source = tmp_path / "negative-revenue.csv"
    output = tmp_path / "report.md"
    source.write_text("month,revenue,cost\n2026-01,-1,0\n", encoding="utf-8")

    exit_code = main(["--input", str(source), "--output", str(output)])

    assert exit_code == 2
    assert "row 2: revenue must be non-negative" in capsys.readouterr().err
    assert not output.exists()


@pytest.mark.parametrize("title", ["Bad\nTitle", "Bad\rTitle", "Bad\x00Title", "Bad\u0085Title"])
def test_cli_rejects_title_with_control_characters(tmp_path: Path, capsys, title: str) -> None:
    source = tmp_path / "input.csv"
    output = tmp_path / "report.md"
    source.write_text("month,revenue,cost\n2026-01,1,0\n", encoding="utf-8")

    exit_code = main(["--input", str(source), "--output", str(output), "--title", title])

    assert exit_code == 2
    assert capsys.readouterr().err == "error: title must not contain control characters\n"
    assert not output.exists()


def test_cli_rejects_invalid_utf8_input(tmp_path: Path, capsys) -> None:
    source = tmp_path / "invalid.csv"
    output = tmp_path / "report.md"
    source.write_bytes(b"month,revenue,cost\n2026-01,1,0\xff\n")

    exit_code = main(["--input", str(source), "--output", str(output)])

    assert exit_code == 2
    assert capsys.readouterr().err == "error: invalid UTF-8 input\n"
    assert not output.exists()


def test_cli_rejects_output_path_that_is_a_directory(tmp_path: Path, capsys) -> None:
    source = tmp_path / "input.csv"
    output = tmp_path / "report-directory"
    source.write_text("month,revenue,cost\n2026-01,1,0\n", encoding="utf-8")
    output.mkdir()

    exit_code = main(["--input", str(source), "--output", str(output)])

    assert exit_code == 2
    assert capsys.readouterr().err == "error: unable to write output\n"


def test_cli_rejects_html_in_title(tmp_path: Path, capsys) -> None:
    source = tmp_path / "input.csv"
    output = tmp_path / "report.md"
    source.write_text("month,revenue,cost\n2026-01,100,50\n", encoding="utf-8")

    exit_code = main(
        ["--input", str(source), "--output", str(output), "--title", '<img src=x onerror="alert(1)">']
    )

    assert exit_code == 2
    assert capsys.readouterr().err == "error: title contains Markdown or HTML syntax\n"
    assert not output.exists()


def test_cli_rejects_markdown_syntax_in_title(tmp_path: Path, capsys) -> None:
    source = tmp_path / "input.csv"
    output = tmp_path / "report.md"
    source.write_text("month,revenue,cost\n2026-01,100,50\n", encoding="utf-8")

    exit_code = main(
        ["--input", str(source), "--output", str(output), "--title", "**Quarterly** KPI Snapshot"]
    )

    assert exit_code == 2
    assert capsys.readouterr().err == "error: title contains Markdown or HTML syntax\n"
    assert not output.exists()
