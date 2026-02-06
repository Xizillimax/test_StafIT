import pytest

from reports import build_report, get_report_names


def test_get_report_names():
    """Должен возвращать список с average-gdp."""
    names = get_report_names()
    assert "average-gdp" in names
    assert isinstance(names, list)


def test_average_gdp_single_country():
    """Среднее ВВП для одной страны — среднее арифметическое по gdp."""
    rows = [
        {"country": "Germany", "gdp": "100", "year": "2021"},
        {"country": "Germany", "gdp": "200", "year": "2022"},
    ]
    headers, table_rows = build_report("average-gdp", rows)
    assert headers == ["country", "average_gdp"]
    assert len(table_rows) == 1
    assert table_rows[0][0] == "Germany"
    assert table_rows[0][1] == 150.0


def test_average_gdp_sorted_descending():
    """Страны должны быть отсортированы по убыванию среднего ВВП."""
    rows = [
        {"country": "A", "gdp": "100"},
        {"country": "B", "gdp": "300"},
        {"country": "C", "gdp": "200"},
    ]
    _, table_rows = build_report("average-gdp", rows)
    assert [r[0] for r in table_rows] == ["B", "C", "A"]
    assert [r[1] for r in table_rows] == [300.0, 200.0, 100.0]


def test_average_gdp_multiple_years_per_country():
    """Несколько лет по одной стране — одно значение, среднее."""
    rows = [
        {"country": "USA", "gdp": "1000"},
        {"country": "USA", "gdp": "2000"},
        {"country": "USA", "gdp": "3000"},
    ]
    _, table_rows = build_report("average-gdp", rows)
    assert len(table_rows) == 1
    assert table_rows[0][1] == 2000.0


def test_average_gdp_rounding():
    """Значения average_gdp округляются до 2 знаков."""
    rows = [
        {"country": "X", "gdp": "1"},
        {"country": "X", "gdp": "2"},
    ]
    _, table_rows = build_report("average-gdp", rows)
    assert table_rows[0][1] == 1.5


def test_average_gdp_empty_rows():
    """Пустой список строк — пустая таблица."""
    headers, table_rows = build_report("average-gdp", [])
    assert headers == ["country", "average_gdp"]
    assert table_rows == []


def test_unknown_report_raises():
    """Неизвестный отчёт вызывает ValueError."""
    with pytest.raises(ValueError, match="Unknown report"):
        build_report("unknown-report", [{"country": "A", "gdp": "1"}])


def test_average_gdp_float_gdp():
    """gdp может быть дробным (как в CSV)."""
    rows = [
        {"country": "Y", "gdp": "1.5"},
        {"country": "Y", "gdp": "2.5"},
    ]
    _, table_rows = build_report("average-gdp", rows)
    assert table_rows[0][1] == 2.0
