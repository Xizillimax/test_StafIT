from collections import defaultdict


def _build_average_gdp(rows: list[dict]) -> tuple[list[str], list[list]]:

    by_country: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        country = row["country"]
        gdp = float(row["gdp"])
        by_country[country].append(gdp)
    result = [
        (country, sum(gdps) / len(gdps))
        for country, gdps in by_country.items()
    ]
    result.sort(key=lambda x: x[1], reverse=True)
    headers = ["country", "average_gdp"]
    table_rows = [[c, round(avg, 2)] for c, avg in result]
    return headers, table_rows


REPORTS = {
    "average-gdp": _build_average_gdp,
}


def get_report_names():

    return list(REPORTS.keys())


def build_report(report_name: str, rows: list[dict]) -> tuple[list[str], list[list]]:

    if report_name not in REPORTS:
        available = ", ".join(REPORTS)
        raise ValueError(f"Unknown report: {report_name!r}. Available: {available}")
    return REPORTS[report_name](rows)
