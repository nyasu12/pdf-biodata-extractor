import json
from pathlib import Path

from openpyxl import load_workbook

from modules.excel_module import normalize_date_string, save_to_excel


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_profile(name: str):
    with (PROJECT_ROOT / "profiles" / f"{name}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def worksheet_values(path):
    workbook = load_workbook(path, data_only=True)
    worksheet = workbook.active
    return list(worksheet.values)


def test_date_normalization_handles_dotted_month():
    assert normalize_date_string("Oct. 20, 2010") == "2010/10/20"


def test_entertainer_profile_preserves_legacy_excel_layout(tmp_path):
    profile = load_profile("entertainer_jp")
    output = tmp_path / "entertainer.xlsx"
    data = [
        {
            "full_name": "SANTOS  MARIA  CRUZ",
            "date_of_birth": "Oct. 20, 2010",
            "passport_number": "P0000001",
            "place_of_birth": "MANILA",
            "present_address": "SAMPLE ADDRESS",
            "valid_until": "DECEMBER 31, 2030",
            "category": "舞踏",
            "employment_history": [
                {"country": "Philippines", "start_date": "JANUARY 1, 2023", "end_date": "JUNE 1, 2023"},
                {"country": "Japan", "start_date": "APRIL 19, 2025", "end_date": "JULY 19, 2025"},
                {"country": "Japan", "start_date": "MARCH 1, 2026", "end_date": "JUNE 1, 2026"},
            ],
        }
    ]

    save_to_excel(data, output, profile)
    rows = worksheet_values(output)
    headers = list(rows[0])
    values = list(rows[1])

    assert headers[:10] == [
        "Full Name",
        "Date of Birth",
        "Passport Number",
        "Place of Birth",
        "Present Address",
        "Valid Until",
        "Category",
        "Japan Entry Count",
        "Japan Work Period Start",
        "Japan Work Period End",
    ]
    assert headers[10:] == [
        "Philippines Work Period Start 1",
        "Philippines Work Period End 1",
    ]
    assert values[1] == "2010/10/20"
    assert values[7] == 2
    assert values[8] == "2026/03/01"
    assert values[9] == "2026/06/01"
    assert values[10] == "2023/01/01"
    assert values[11] == "2023/06/01"


def test_generic_profile_exports_country_and_employer(tmp_path):
    profile = load_profile("generic_biodata")
    output = tmp_path / "generic.xlsx"
    data = [
        {
            "full_name": "Alex Example",
            "date_of_birth": "JANUARY 2, 1990",
            "place_of_birth": "Example City",
            "present_address": "123 Sample Street",
            "nationality": "Exampleland",
            "passport_number": "EX123456",
            "valid_until": "DECEMBER 31, 2030",
            "category": "Engineer",
            "employment_history": [
                {
                    "country": "Exampleland",
                    "employer": "Example Works",
                    "start_date": "MARCH 1, 2020",
                    "end_date": "APRIL 1, 2022",
                }
            ],
        }
    ]

    save_to_excel(data, output, profile)
    rows = worksheet_values(output)
    headers = list(rows[0])
    values = list(rows[1])

    assert "Employment Country 1" in headers
    assert "Employer 1" in headers
    assert values[headers.index("Employment Country 1")] == "Exampleland"
    assert values[headers.index("Employer 1")] == "Example Works"
    assert values[headers.index("Employment Start 1")] == "2020/03/01"
