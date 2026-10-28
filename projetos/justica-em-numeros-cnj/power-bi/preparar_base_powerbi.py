#!/usr/bin/env python3
"""Baixa a publicação oficial CNJ 23-Jun-2026 e prepara CSV para Power BI.

Uso: python preparar_base_powerbi.py [caminho_saida.csv]
Requer apenas Python 3 (biblioteca padrão).
"""
from __future__ import annotations

import csv
import io
import sys
import urllib.request
import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

URL = "https://www.cnj.jus.br/wp-content/uploads/2026/06/23-jun-2026.zip"
SOURCE_CSV = "JN_23-Jun-2026.csv"
DEFAULT_OUTPUT = Path(__file__).with_name("dados_fluxo_cnj_powerbi.csv")

METRICS = {
    "cn1": "cn1_casos_novos_1g",
    "cp1": "cp1_casos_pendentes_1g",
    "tbaix1": "tbaix1_processos_baixados_1g",
    "iad1": "iad1_atendimento_demanda_1g",
    "tc1": "tc1_congestionamento_1g",
    "cn2": "cn2_casos_novos_2g",
    "cp2": "cp2_casos_pendentes_2g",
    "tbaix2": "tbaix2_processos_baixados_2g",
    "iad2": "iad2_atendimento_demanda_2g",
    "tc2": "tc2_congestionamento_2g",
    "cnje": "cnje_casos_novos_juizados",
    "cpje": "cpje_casos_pendentes_juizados",
    "tbaixje": "tbaixje_processos_baixados_juizados",
    "iadje": "iadje_atendimento_demanda_juizados",
    "tcje": "tcje_congestionamento_juizados",
}
DIMENSIONS = ["ano", "justica", "sigla", "seq_orgao"]
OUTPUT_FIELDS = [
    "ano", "justica", "sigla_tribunal", "seq_orgao", "tipo_registro",
    *METRICS.values(),
]
AGGREGATE_SEQUENCE_CODES = {"999991", "999992"}
MISSING = {"", "nd", "n/a", "na", "null", "none", "inf", "-"}


def clean_number(value: str | None) -> str:
    """Return decimal-dot text for Power BI; preserve missing values as blank."""
    text = (value or "").strip()
    if text.lower() in MISSING:
        return ""
    text = text.replace(" ", "").replace(",", ".")
    try:
        number = Decimal(text)
    except InvalidOperation:
        return ""
    if not number.is_finite():
        return ""
    return format(number, "f")


def main() -> None:
    output = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        archive_bytes = response.read()
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        with archive.open(SOURCE_CSV) as source:
            text = io.TextIOWrapper(source, encoding="latin-1", newline="")
            reader = csv.DictReader(text, delimiter=";")
            source_fields = set(reader.fieldnames or [])
            required = set(DIMENSIONS) | set(METRICS)
            missing = sorted(required - source_fields)
            if missing:
                raise ValueError(f"Colunas esperadas ausentes na publicação CNJ: {missing}")

            seen: set[tuple[str, str, str, str]] = set()
            rows_written = 0
            with output.open("w", encoding="utf-8-sig", newline="") as destination:
                writer = csv.DictWriter(destination, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
                writer.writeheader()
                for row in reader:
                    key = tuple((row.get(col) or "").strip() for col in DIMENSIONS)
                    if key in seen:
                        raise ValueError(f"Chave duplicada na fonte: {key}")
                    seen.add(key)
                    seq = key[3]
                    result = {
                        "ano": key[0],
                        "justica": key[1],
                        "sigla_tribunal": key[2],
                        "seq_orgao": seq,
                        "tipo_registro": (
                            "TOTAL_JUSTICA" if seq in AGGREGATE_SEQUENCE_CODES else "TRIBUNAL"
                        ),
                    }
                    for source_name, output_name in METRICS.items():
                        result[output_name] = clean_number(row.get(source_name))
                    writer.writerow(result)
                    rows_written += 1

    if rows_written == 0:
        raise ValueError("A fonte foi baixada, mas nenhuma linha foi processada.")
    print(f"Arquivo criado: {output.resolve()}")
    print(f"Linhas: {rows_written:,}; colunas: {len(OUTPUT_FIELDS)}")
    print(f"Fonte: {URL} | arquivo interno: {SOURCE_CSV}")


if __name__ == "__main__":
    main()
