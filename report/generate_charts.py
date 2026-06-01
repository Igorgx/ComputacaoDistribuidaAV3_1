from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def read_stats(path: Path) -> dict[str, float]:
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    aggregate = next((row for row in rows if row.get("Name") == "Aggregated"), rows[-1])
    return {
        "rps": float(aggregate.get("Requests/s", 0) or 0),
        "avg": float(aggregate.get("Average Response Time", 0) or 0),
        "p95": float(aggregate.get("95%", 0) or 0),
        "failures": float(aggregate.get("Failure Count", 0) or 0),
    }


def svg_bar(title: str, values: dict[str, float], unit: str) -> str:
    width = 900
    height = 80 + 42 * max(1, len(values))
    label_width = 230
    max_value = max(values.values(), default=1) or 1
    rows = []
    for index, (name, value) in enumerate(sorted(values.items())):
        y = 60 + index * 42
        bar_width = int((width - label_width - 80) * (value / max_value))
        rows.append(
            f'<text x="20" y="{y + 18}" font-size="14">{name}</text>'
            f'<rect x="{label_width}" y="{y}" width="{bar_width}" height="24" fill="#2563eb"/>'
            f'<text x="{label_width + bar_width + 8}" y="{y + 18}" font-size="13">{value:.2f} {unit}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<rect width="100%" height="100%" fill="white"/>'
        f'<text x="20" y="32" font-size="20" font-weight="700">{title}</text>'
        + "".join(rows)
        + "</svg>"
    )


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    stats_files = sorted(RESULTS.glob("*_stats.csv"))
    if not stats_files:
        print("Nenhum *_stats.csv encontrado em report/results.")
        return

    metrics = {"rps": {}, "avg": {}, "p95": {}, "failures": {}}
    for path in stats_files:
        label = path.name.removesuffix("_stats.csv")
        data = read_stats(path)
        for key in metrics:
            metrics[key][label] = data[key]

    charts = {
        "requests_per_second.svg": ("Requisicoes por segundo", metrics["rps"], "req/s"),
        "average_response_time.svg": ("Tempo medio de resposta", metrics["avg"], "ms"),
        "p95_response_time.svg": ("Percentil 95", metrics["p95"], "ms"),
        "failures.svg": ("Falhas", metrics["failures"], "falhas"),
    }
    for filename, (title, values, unit) in charts.items():
        (RESULTS / filename).write_text(svg_bar(title, values, unit), encoding="utf-8")
        print(f"Gerado {RESULTS / filename}")


if __name__ == "__main__":
    main()
