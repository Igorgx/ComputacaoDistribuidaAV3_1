from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
CHARTS = RESULTS / "charts"


def normalize_label(label: str) -> str:
    if label == "python_soap_alt":
        return "python_soap_alta"
    return label


def parse_label(label: str) -> tuple[str, str, str]:
    label = normalize_label(label)
    parts = label.split("_")
    if len(parts) < 3:
        return label, "", ""
    language = parts[0]
    load = parts[-1]
    technology = "_".join(parts[1:-1])
    return language, technology, load


def read_stats(path: Path) -> dict[str, float]:
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    aggregate = next((row for row in rows if row.get("Name") == "Aggregated"), rows[-1])
    requests = float(aggregate.get("Request Count", 0) or 0)
    failures = float(aggregate.get("Failure Count", 0) or 0)
    return {
        "requests": requests,
        "rps": float(aggregate.get("Requests/s", 0) or 0),
        "avg": float(aggregate.get("Average Response Time", 0) or 0),
        "p95": float(aggregate.get("95%", 0) or 0),
        "failures": failures,
        "failure_rate": (failures / requests * 100) if requests else 0,
    }


def load_results() -> list[dict[str, object]]:
    results = []
    for path in sorted(RESULTS.glob("*_stats.csv")):
        label = normalize_label(path.name.removesuffix("_stats.csv"))
        if label.startswith("smoke_"):
            continue
        language, technology, load = parse_label(label)
        if load not in {"moderada", "alta"}:
            continue
        data = read_stats(path)
        results.append(
            {
                "label": label,
                "language": language,
                "technology": technology,
                "load": load,
                **data,
            }
        )
    return results


def write_summary(results: list[dict[str, object]]) -> None:
    fields = [
        "label",
        "language",
        "technology",
        "load",
        "requests",
        "rps",
        "avg",
        "p95",
        "failures",
        "failure_rate",
    ]
    with (RESULTS / "summary_metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


def ordered_labels(results: list[dict[str, object]]) -> list[str]:
    order = {"python": 0, "java": 1}
    tech_order = {"rest": 0, "grpc": 1, "graphql": 2, "soap": 3}
    load_order = {"moderada": 0, "alta": 1}
    return [
        item["label"]
        for item in sorted(
            results,
            key=lambda item: (
                order.get(str(item["language"]), 99),
                tech_order.get(str(item["technology"]), 99),
                load_order.get(str(item["load"]), 99),
            ),
        )
    ]


def plot_horizontal(
    results: list[dict[str, object]],
    metric: str,
    title: str,
    unit: str,
    filename: str,
) -> None:
    labels = ordered_labels(results)
    by_label = {item["label"]: item for item in results}
    values = [float(by_label[label][metric]) for label in labels]
    colors = [
        "#60a5fa" if str(by_label[label]["load"]) == "moderada" else "#2563eb"
        for label in labels
    ]

    height = max(6, len(labels) * 0.45)
    fig, ax = plt.subplots(figsize=(12, height))
    bars = ax.barh(labels, values, color=colors)
    ax.set_title(title, fontsize=15, fontweight="bold", loc="left")
    ax.set_xlabel(unit)
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.invert_yaxis()
    ax.spines[["top", "right", "left"]].set_visible(False)

    max_value = max(values) if values else 0
    offset = max_value * 0.01 if max_value else 0.5
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f} {unit}",
            va="center",
            fontsize=9,
        )

    handles = [
        plt.Rectangle((0, 0), 1, 1, color="#60a5fa", label="Carga moderada"),
        plt.Rectangle((0, 0), 1, 1, color="#2563eb", label="Carga alta"),
    ]
    ax.legend(handles=handles, loc="lower right")
    fig.tight_layout()
    fig.savefig(CHARTS / f"{filename}.png", dpi=180)
    fig.savefig(CHARTS / f"{filename}.svg")
    plt.close(fig)


def plot_load_delta(results: list[dict[str, object]]) -> None:
    pairs: dict[tuple[str, str], dict[str, dict[str, object]]] = {}
    for item in results:
        key = (str(item["language"]), str(item["technology"]))
        pairs.setdefault(key, {})[str(item["load"])] = item

    labels = []
    avg_ratios = []
    p95_ratios = []
    for (language, technology), pair in sorted(pairs.items()):
        if "moderada" not in pair or "alta" not in pair:
            continue
        moderate_avg = float(pair["moderada"]["avg"])
        high_avg = float(pair["alta"]["avg"])
        moderate_p95 = float(pair["moderada"]["p95"])
        high_p95 = float(pair["alta"]["p95"])
        labels.append(f"{language}_{technology}")
        avg_ratios.append(high_avg / moderate_avg if moderate_avg else 0)
        p95_ratios.append(high_p95 / moderate_p95 if moderate_p95 else 0)

    fig, ax = plt.subplots(figsize=(12, max(5, len(labels) * 0.45)))
    y = range(len(labels))
    ax.barh([item - 0.18 for item in y], avg_ratios, height=0.35, color="#2563eb", label="Media")
    ax.barh([item + 0.18 for item in y], p95_ratios, height=0.35, color="#f97316", label="P95")
    ax.set_yticks(list(y), labels)
    ax.invert_yaxis()
    ax.set_title("Aumento da latencia da carga moderada para a alta", fontsize=15, fontweight="bold", loc="left")
    ax.set_xlabel("Multiplicador")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(loc="lower right")
    for index, (avg, p95) in enumerate(zip(avg_ratios, p95_ratios)):
        ax.text(avg + 0.05, index - 0.18, f"{avg:.1f}x", va="center", fontsize=9)
        ax.text(p95 + 0.05, index + 0.18, f"{p95:.1f}x", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(CHARTS / "latency_growth_moderada_to_alta.png", dpi=180)
    fig.savefig(CHARTS / "latency_growth_moderada_to_alta.svg")
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)
    results = load_results()
    if not results:
        print("Nenhum *_stats.csv encontrado em report/results.")
        return

    write_summary(results)
    plot_horizontal(results, "rps", "Requisicoes por segundo", "req/s", "requests_per_second")
    plot_horizontal(results, "avg", "Tempo medio de resposta", "ms", "average_response_time")
    plot_horizontal(results, "p95", "Percentil 95 de resposta", "ms", "p95_response_time")
    plot_horizontal(results, "failure_rate", "Taxa de falha", "%", "failure_rate_percent")
    plot_horizontal(results, "failures", "Falhas absolutas", "falhas", "failures_absolute")
    plot_load_delta(results)

    print(f"Resumo: {RESULTS / 'summary_metrics.csv'}")
    for path in sorted(CHARTS.glob("*")):
        print(f"Gerado {path}")


if __name__ == "__main__":
    main()
