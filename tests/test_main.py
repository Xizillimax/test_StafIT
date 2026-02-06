import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_main_success(capfd):
    """main() с валидными аргументами возвращает 0 и выводит таблицу."""
    argv = ["main.py", "--files", "economic1.csv", "--report", "average-gdp"]
    with patch.object(sys, "argv", argv):
        from main import main

        exit_code = main()
    out, err = capfd.readouterr()
    assert exit_code == 0
    assert "country" in out
    assert "average_gdp" in out
    assert "United States" in out


def test_main_multiple_files(capfd):
    """main() с несколькими файлами выводит объединённый отчёт."""
    argv = [
        "main.py",
        "--files",
        "economic1.csv",
        "economic2.csv",
        "--report",
        "average-gdp",
    ]
    with patch.object(sys, "argv", argv):
        from main import main

        exit_code = main()
    out, err = capfd.readouterr()
    assert exit_code == 0
    assert "country" in out
    assert "average_gdp" in out


def test_main_file_not_found(capfd):
    """main() при отсутствующем файле возвращает 1 и пишет в stderr."""
    argv = ["main.py", "--files", "nonexistent.csv", "--report", "average-gdp"]
    with patch.object(sys, "argv", argv):
        from main import main

        exit_code = main()
    out, err = capfd.readouterr()
    assert exit_code == 1
    assert "not found" in err or "Error" in err


def test_main_no_data(capfd):
    """main() при пустом CSV возвращает 1 и сообщение об отсутствии данных."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        newline="",
        encoding="utf-8",
    ) as f:
        f.write(
            "country,year,gdp,gdp_growth,inflation,unemployment,population,continent\n"
        )
        empty_path = f.name
    try:
        argv = ["main.py", "--files", empty_path, "--report", "average-gdp"]
        with patch.object(sys, "argv", argv):
            from main import main

            exit_code = main()
        out, err = capfd.readouterr()
        assert exit_code == 1
        assert "no data" in err.lower() or "Error" in err
    finally:
        Path(empty_path).unlink(missing_ok=True)


def test_main_os_error_on_open(capfd):
    """main() при OSError при проверке файла возвращает 1."""
    argv = ["main.py", "--files", "economic1.csv", "--report", "average-gdp"]
    with patch.object(sys, "argv", argv):
        with patch("main.open", side_effect=OSError("Permission denied")):
            from main import main

            exit_code = main()
    out, err = capfd.readouterr()
    assert exit_code == 1
    assert "Error" in err or "Permission" in err


def test_main_value_error_from_build_report(capfd):
    """main() при ValueError из build_report возвращает 1 и пишет в stderr."""
    argv = ["main.py", "--files", "economic1.csv", "--report", "average-gdp"]
    with patch.object(sys, "argv", argv):
        with patch("main.build_report", side_effect=ValueError("Unknown report")):
            from main import main

            exit_code = main()
    out, err = capfd.readouterr()
    assert exit_code == 1
    assert "Error" in err or "Unknown" in err


def test_main_os_error_on_load_csv(capfd):
    """main() при OSError при чтении CSV (в load_csv_rows) возвращает 1."""
    argv = ["main.py", "--files", "economic1.csv", "--report", "average-gdp"]
    open_calls = []

    def open_mock(path, *args, **kwargs):
        open_calls.append(path)
        if len(open_calls) >= 2:
            raise OSError("Read error")
        return open(path, *args, **kwargs)

    with patch.object(sys, "argv", argv):
        with patch("main.open", open_mock):
            from main import main

            exit_code = main()
    out, err = capfd.readouterr()
    assert exit_code == 1
    assert "Error" in err
