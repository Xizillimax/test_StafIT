import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def run_report(files: list[str], report: str) -> subprocess.CompletedProcess:
    """Запуск main.py с заданными --files и --report."""
    cmd = [sys.executable, str(ROOT / "main.py"), "--files", *files, "--report", report]
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )


def test_cli_average_gdp_single_file():
    """Запуск с одним файлом возвращает 0 и выводит таблицу."""
    result = run_report(["economic1.csv"], "average-gdp")
    assert result.returncode == 0
    assert "country" in result.stdout
    assert "average_gdp" in result.stdout
    assert "United States" in result.stdout


def test_cli_average_gdp_multiple_files():
    """Запуск с несколькими файлами объединяет данные."""
    result = run_report(["economic1.csv", "economic2.csv"], "average-gdp")
    assert result.returncode == 0
    assert "country" in result.stdout
    assert "average_gdp" in result.stdout
    assert "United States" in result.stdout or "Germany" in result.stdout
    assert "Spain" in result.stdout or "Mexico" in result.stdout


def test_cli_missing_file():
    """Несуществующий файл — код 1, сообщение в stderr."""
    result = run_report(["nonexistent.csv"], "average-gdp")
    assert result.returncode == 1
    assert "not found" in result.stderr or "Error" in result.stderr


def test_cli_no_files():
    """Без --files argparse выдаёт ошибку."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), "--report", "average-gdp"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_cli_no_report():
    """Без --report argparse выдаёт ошибку."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), "--files", "economic1.csv"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_cli_invalid_report():
    """Неверное значение --report — ошибка."""
    result = run_report(["economic1.csv"], "invalid-report")
    assert result.returncode != 0


def test_cli_empty_csv_no_data():
    """Пустой CSV (только заголовок) — код 1, сообщение об отсутствии данных."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        newline="",
        encoding="utf-8",
    ) as f:
        f.write("country,year,gdp,gdp_growth,inflation,unemployment,population,continent\n")
        empty_path = f.name
    try:
        result = run_report([empty_path], "average-gdp")
        assert result.returncode == 1
        assert "no data" in result.stderr.lower() or "Error" in result.stderr
    finally:
        Path(empty_path).unlink(missing_ok=True)
