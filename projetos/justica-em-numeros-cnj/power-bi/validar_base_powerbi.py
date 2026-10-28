#!/usr/bin/env python3
"""Valida a base Power BI sem bibliotecas de terceiros."""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("dados_fluxo_cnj_powerbi.csv")
NUMERIC = [
    "cn1_casos_novos_1g", "cp1_casos_pendentes_1g", "tbaix1_processos_baixados_1g",
    "iad1_atendimento_demanda_1g", "tc1_congestionamento_1g",
    "cn2_casos_novos_2g", "cp2_casos_pendentes_2g", "tbaix2_processos_baixados_2g",
    "iad2_atendimento_demanda_2g", "tc2_congestionamento_2g",
    "cnje_casos_novos_juizados", "cpje_casos_pendentes_juizados",
    "tbaixje_processos_baixados_juizados", "iadje_atendimento_demanda_juizados",
    "tcje_congestionamento_juizados",
]
GROUPS = {
    "1G": ("cn1_casos_novos_1g", "cp1_casos_pendentes_1g", "tbaix1_processos_baixados_1g", "iad1_atendimento_demanda_1g", "tc1_congestionamento_1g"),
    "2G": ("cn2_casos_novos_2g", "cp2_casos_pendentes_2g", "tbaix2_processos_baixados_2g", "iad2_atendimento_demanda_2g", "tc2_congestionamento_2g"),
    "JE": ("cnje_casos_novos_juizados", "cpje_casos_pendentes_juizados", "tbaixje_processos_baixados_juizados", "iadje_atendimento_demanda_juizados", "tcje_congestionamento_juizados"),
}
TOLERANCE = Decimal("0.000000000001")


def dec(value: str) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def main() -> None:
    with FILE.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit("ERRO: CSV vazio")

    keys = [(r["ano"], r["justica"], r["sigla_tribunal"], r["seq_orgao"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise SystemExit("ERRO: chave duplicada")

    detail_sums: dict[tuple[str, str, str], Decimal] = {}
    totals = [r for r in rows if r["tipo_registro"] == "TOTAL_JUSTICA"]
    details = [r for r in rows if r["tipo_registro"] == "TRIBUNAL"]
    recon_counts = {name: 0 for name in ("cn1", "cp1", "tbaix1", "cn2", "cp2", "tbaix2", "cnje", "cpje", "tbaixje")}

    for code in recon_counts:
        total_field = next(field for group in GROUPS.values() for field in group[:3] if field.startswith(code + "_"))
        sums: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
        seen: set[tuple[str, str]] = set()
        for row in details:
            value = dec(row[total_field])
            if value is not None:
                key = (row["ano"], row["justica"])
                sums[key] += value
                seen.add(key)
        for row in totals:
            value = dec(row[total_field])
            key = (row["ano"], row["justica"])
            if value is None or key not in seen:
                continue
            if value != sums[key]:
                raise SystemExit(f"ERRO: divergência de {code} em {key}: total={value}, soma={sums[key]}")
            recon_counts[code] += 1

    rate_counts: dict[str, int] = {}
    max_diffs: dict[str, Decimal] = {}
    for label, (new_f, pending_f, down_f, iad_f, tc_f) in GROUPS.items():
        iad_n = tc_n = 0
        iad_diff = tc_diff = Decimal(0)
        for row in totals:
            new, pending, down, iad, tc = (dec(row[f]) for f in (new_f, pending_f, down_f, iad_f, tc_f))
            if new is not None and new != 0 and down is not None and iad is not None:
                diff = abs(iad - down / new)
                iad_diff = max(iad_diff, diff)
                if diff > TOLERANCE:
                    raise SystemExit(f"ERRO: IAD {label} divergente em {row['ano']}/{row['justica']}")
                iad_n += 1
            if pending is not None and down is not None and tc is not None and pending + down != 0:
                diff = abs(tc - pending / (pending + down))
                tc_diff = max(tc_diff, diff)
                if diff > TOLERANCE:
                    raise SystemExit(f"ERRO: TC {label} divergente em {row['ano']}/{row['justica']}")
                tc_n += 1
        rate_counts[f"IAD_{label}"] = iad_n
        rate_counts[f"TC_{label}"] = tc_n
        max_diffs[f"IAD_{label}"] = iad_diff
        max_diffs[f"TC_{label}"] = tc_diff

    print(f"OK — {len(rows)} linhas, {len(NUMERIC) + 5} campos, sem duplicidade na chave.")
    print(f"Linhas consolidadas: {len(totals)}; linhas de tribunal/unidade: {len(details)}.")
    print("Reconciliação total vs. soma detalhada:")
    for name, count in recon_counts.items():
        print(f"  {name}: {count} combinações ano/Justiça, sem divergência.")
    print("Conferência de taxas publicadas contra fórmulas:")
    for name, count in rate_counts.items():
        print(f"  {name}: {count} linhas; diferença máxima {max_diffs[name]}.")


if __name__ == "__main__":
    main()
