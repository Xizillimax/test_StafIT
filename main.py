import argparse
import csv
import sys

from tabulate import tabulate

from reports import build_report, get_report_names


def load_csv_rows(file_paths: list[str]) -> list[dict]:
    """Читает все CSV-файлы и возвращает объединённый список строк (dict)."""
    all_rows = []
    for path in file_paths:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_rows.extend(list(reader))
    return all_rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Form reports from macroeconomic CSV data."
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Paths to CSV files with economic data",
    )
    parser.add_argument(
        "--report",
        required=True,
        choices=get_report_names(),
        help="Report type to generate",
    )
    args = parser.parse_args()

    for path in args.files:
        try:
            with open(path, encoding="utf-8"):
                pass
        except FileNotFoundError:
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 1
        except OSError as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            return 1

    try:
        rows = load_csv_rows(args.files)
    except OSError as e:
        print(f"Error reading files: {e}", file=sys.stderr)
        return 1

    if not rows:
        print("Error: no data in the given files", file=sys.stderr)
        return 1

    try:
        headers, table_rows = build_report(args.report, rows)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(tabulate(table_rows, headers=headers, tablefmt="grid"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
