#!/usr/bin/env python3
"""
check_thresholds.py
===================
Generic threshold enforcer used by every workflow gate.
Reads a JSON metrics report and a YAML gate spec; exits non-zero when
any blocking gate is breached (unless --no-fail is set).

Usage:
  python scripts/check_thresholds.py \
    --report  reports/retrieval_metrics.json \
    --gates   config/thresholds/retrieval.yaml \
    [--output reports/breach.json] \
    [--fail-on-breach | --no-fail]
"""

import argparse
import json
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

console = Console()


def load_report(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def load_gates(path: str) -> list[dict]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("gates", [])


def check(report: dict, gates: list[dict]) -> tuple[list[dict], list[dict]]:
    """Returns (breaches, warnings)."""
    breaches, warnings = [], []
    metrics = report.get("metrics", report)          # support flat or nested

    for gate in gates:
        metric  = gate["metric"]
        thresh  = gate["threshold"]
        dirn    = gate.get("direction", "min")       # min = value >= thresh
        sev     = gate.get("severity", "blocking")
        desc    = gate.get("description", "")

        value = metrics.get(metric)
        if value is None:
            console.print(f"[yellow]⚠  Metric '{metric}' not found in report – skipping[/]")
            continue

        if dirn == "min":
            breached = float(value) < thresh
        else:                                        # max
            breached = float(value) > thresh

        entry = {
            "metric": metric, "value": value,
            "threshold": thresh, "direction": dirn,
            "severity": sev, "description": desc,
        }

        if breached:
            if sev == "blocking":
                breaches.append(entry)
            else:
                warnings.append(entry)

    return breaches, warnings


def print_summary(breaches: list, warnings: list) -> None:
    table = Table(title="Gate Check Results", show_header=True)
    table.add_column("Status",    style="bold")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_column("Threshold")
    table.add_column("Severity")
    table.add_column("Description")

    for b in breaches:
        table.add_row(
            "❌ FAIL", b["metric"], str(b["value"]),
            f"{b['direction']} {b['threshold']}", b["severity"], b["description"],
            style="red",
        )
    for w in warnings:
        table.add_row(
            "⚠ WARN", w["metric"], str(w["value"]),
            f"{w['direction']} {w['threshold']}", w["severity"], w["description"],
            style="yellow",
        )

    console.print(table)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report",        required=True)
    ap.add_argument("--gates",         required=True)
    ap.add_argument("--output",        default=None)
    ap.add_argument("--fail-on-breach", action="store_true")
    ap.add_argument("--no-fail",        action="store_true")
    args = ap.parse_args()

    report = load_report(args.report)
    gates  = load_gates(args.gates)
    breaches, warnings = check(report, gates)

    print_summary(breaches, warnings)

    result = {
        "has_breach":     len(breaches) > 0,
        "breach_count":   len(breaches),
        "warning_count":  len(warnings),
        "breaches":       breaches,
        "warnings":       warnings,
    }

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)

    if breaches:
        console.print(f"\n[bold red]❌ {len(breaches)} blocking gate(s) breached.[/]")
        if args.fail_on_breach and not args.no_fail:
            sys.exit(1)
    else:
        console.print("\n[bold green]✅ All gates passed.[/]")


if __name__ == "__main__":
    main()
