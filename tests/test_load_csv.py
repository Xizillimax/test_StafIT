import csv
import tempfile
from pathlib import Path

from main import load_csv_rows


def test_load_csv_rows_single_file():
    """Читает один CSV и возвращает список словарей."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["country", "year", "gdp"])
        writer.writerow(["Germany", "2021", "4000"])
        writer.writerow(["France", "2021", "3000"])
        path = f.name
    try:
        rows = load_csv_rows([path])
        assert len(rows) == 2
        assert rows[0]["country"] == "Germany" and rows[0]["gdp"] == "4000"
        assert rows[1]["country"] == "France" and rows[1]["gdp"] == "3000"
    finally:
        Path(path).unlink(missing_ok=True)


def test_load_csv_rows_merges_files():
    """Несколько файлов — строки объединяются в один список."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        newline="",
        encoding="utf-8",
    ) as f1:
        writer = csv.writer(f1)
        writer.writerow(["country", "gdp"])
        writer.writerow(["A", "1"])
        path1 = f1.name
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        newline="",
        encoding="utf-8",
    ) as f2:
        writer = csv.writer(f2)
        writer.writerow(["country", "gdp"])
        writer.writerow(["B", "2"])
        path2 = f2.name
    try:
        rows = load_csv_rows([path1, path2])
        assert len(rows) == 2
        assert rows[0]["country"] == "A"
        assert rows[1]["country"] == "B"
    finally:
        Path(path1).unlink(missing_ok=True)
        Path(path2).unlink(missing_ok=True)
