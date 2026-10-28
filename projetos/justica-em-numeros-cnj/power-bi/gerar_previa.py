#!/usr/bin/env python3
"""Gera uma prévia estática de layout a partir do CSV preparado.
Requer matplotlib: python -m pip install matplotlib
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
DATA = HERE / "dados_fluxo_cnj_powerbi.csv"
OUT = HERE / "dashboard_preview.png"
YEAR = 2025


def value(row: dict[str, str], field: str) -> float | None:
    raw = row.get(field, "")
    return float(raw) if raw else None


def sum_values(rows, field):
    vals = [value(row, field) for row in rows]
    vals = [v for v in vals if v is not None]
    return sum(vals) if vals else None


def fmt_int(x: float | None) -> str:
    if x is None:
        return "n/d"
    return f"{int(round(x)):,}".replace(",", ".")


def main():
    with DATA.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    totals = [r for r in rows if r["tipo_registro"] == "TOTAL_JUSTICA"]
    current = [r for r in totals if int(r["ano"]) == YEAR]

    fields = {
        "Novos": "cn1_casos_novos_1g",
        "Pendentes": "cp1_casos_pendentes_1g",
        "Baixados": "tbaix1_processos_baixados_1g",
    }
    kpis = {label: sum_values(current, field) for label, field in fields.items()}
    iad = kpis["Baixados"] / kpis["Novos"] if kpis["Novos"] else None
    tc_den = kpis["Pendentes"] + kpis["Baixados"] if kpis["Pendentes"] is not None and kpis["Baixados"] is not None else None
    tc = kpis["Pendentes"] / tc_den if tc_den else None

    by_branch = defaultdict(list)
    for row in current:
        by_branch[row["justica"]].append(row)
    categories = sorted(by_branch, key=lambda b: sum_values(by_branch[b], fields["Novos"]) or 0, reverse=True)
    branches = [b for b in categories if any(sum_values(by_branch[b], f) not in (None, 0) for f in fields.values())]

    trend = defaultdict(list)
    years = list(range(2015, YEAR + 1))
    for year in years:
        year_rows = [r for r in totals if int(r["ano"]) == year]
        for label, field in fields.items():
            trend[label].append((sum_values(year_rows, field) or 0) / 1_000_000)

    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(16, 9), dpi=120, facecolor="#08111f")
    fig.text(0.055, 0.94, "JUSTIÇA EM NÚMEROS", color="#eaf4ff", fontsize=22, fontweight="bold")
    fig.text(0.055, 0.905, "Fluxo processual • 1º grau • ano-base 2025", color="#9db2c8", fontsize=12)
    fig.text(0.945, 0.94, "PRÉVIA ESTÁTICA  |  POWER BI", color="#30d5e8", fontsize=10, ha="right", fontweight="bold")

    card_x = [0.055, 0.235, 0.415, 0.595, 0.775]
    kpi_data = [
        ("CASOS NOVOS", fmt_int(kpis["Novos"]), "1º grau"),
        ("PENDENTES", fmt_int(kpis["Pendentes"]), "1º grau"),
        ("BAIXADOS", fmt_int(kpis["Baixados"]), "1º grau"),
        ("IAD", f"{iad:.1%}" if iad is not None else "n/d", "baixados ÷ novos"),
        ("CONGESTIONAMENTO", f"{tc:.1%}" if tc is not None else "n/d", "pendentes ÷ (pendentes + baixados)"),
    ]
    for x, (label, val, note) in zip(card_x, kpi_data):
        box = FancyBboxPatch((x, 0.765), 0.16, 0.105, boxstyle="round,pad=0.012,rounding_size=0.012", transform=fig.transFigure, facecolor="#111f33", edgecolor="#203751", linewidth=1)
        fig.patches.append(box)
        fig.text(x + 0.012, 0.84, label, color="#82a0bd", fontsize=8, fontweight="bold")
        fig.text(x + 0.012, 0.80, val, color="#f1f7ff", fontsize=15, fontweight="bold")
        fig.text(x + 0.012, 0.777, note, color="#98aec4", fontsize=7)

    ax1 = fig.add_axes([0.065, 0.19, 0.405, 0.50], facecolor="#0c1828")
    colors = ["#27c5dc", "#7b88ff", "#4bd6a2"]
    y = list(range(len(branches)))
    height = 0.23
    for i, (label, field) in enumerate(fields.items()):
        vals = [(sum_values(by_branch[b], field) or 0) / 1_000_000 for b in branches]
        ax1.barh([v + (i-1)*height for v in y], vals, height=0.19, color=colors[i], label=label)
    ax1.set_yticks(y, branches, color="#d6e4f2", fontsize=9)
    ax1.invert_yaxis()
    ax1.set_xlabel("milhões de processos", color="#91a9c1", fontsize=9)
    ax1.set_title("Volumes por ramo da Justiça", color="#e8f2fc", loc="left", fontsize=12, pad=12, fontweight="bold")
    ax1.tick_params(axis="x", colors="#91a9c1", labelsize=8)
    ax1.grid(axis="x", color="#26384e", alpha=0.8)
    ax1.set_axisbelow(True)
    for spine in ax1.spines.values(): spine.set_color("#26384e")
    ax1.legend(frameon=False, labelcolor="#d6e4f2", ncol=3, fontsize=8, loc="lower right")

    ax2 = fig.add_axes([0.53, 0.19, 0.405, 0.50], facecolor="#0c1828")
    for (label, _), color in zip(fields.items(), colors):
        ax2.plot(years, trend[label], color=color, linewidth=2.3, marker="o", markersize=3.5, label=label)
    ax2.set_title("Evolução anual dos volumes", color="#e8f2fc", loc="left", fontsize=12, pad=12, fontweight="bold")
    ax2.set_ylabel("milhões de processos", color="#91a9c1", fontsize=9)
    ax2.set_xticks(years[::2])
    ax2.tick_params(axis="x", colors="#91a9c1", labelsize=8)
    ax2.tick_params(axis="y", colors="#91a9c1", labelsize=8)
    ax2.grid(color="#26384e", alpha=0.8)
    ax2.set_axisbelow(True)
    for spine in ax2.spines.values(): spine.set_color("#26384e")
    ax2.legend(frameon=False, labelcolor="#d6e4f2", ncol=3, fontsize=8, loc="upper left")

    fig.text(0.055, 0.09, "Fonte: CNJ • arquivo de 23/06/2026 • linhas TOTAL_JUSTICA • cálculos agregados por volume", color="#9db2c8", fontsize=9)
    fig.text(0.055, 0.055, "Mockup de referência, não é uma captura do Power BI. Taxas recalculadas sobre volumes; ausências mantidas como nulas.", color="#708aa4", fontsize=8)
    fig.savefig(OUT, facecolor=fig.get_facecolor(), bbox_inches="tight")
    print(f"Imagem criada: {OUT}")


if __name__ == "__main__":
    main()
