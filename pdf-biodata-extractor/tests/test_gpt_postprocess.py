import json
from pathlib import Path

from modules.gpt_module import _postprocess_result


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_profile(name: str):
    with (PROJECT_ROOT / "profiles" / f"{name}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def test_entertainer_category_and_full_name_postprocessing():
    profile = load_profile("entertainer_jp")
    raw = {
        "surname": "SANTOS",
        "given_names": "MARIA",
        "middle_name": "CRUZ",
        "category": "dancer",
        "employment_history": [],
    }

    result = _postprocess_result(raw, profile)

    assert result["category"] == "舞踏"
    assert result["full_name"] == "SANTOS  MARIA  CRUZ"


def test_entertainer_full_name_preserves_empty_middle_name_slot():
    profile = load_profile("entertainer_jp")
    raw = {
        "surname": "SANTOS",
        "given_names": "MARIA",
        "middle_name": "",
        "category": "SINGER",
        "employment_history": [],
    }

    result = _postprocess_result(raw, profile)

    assert result["category"] == "歌謡"
    assert result["full_name"] == "SANTOS  MARIA  "


def test_employment_records_are_normalized_to_configured_fields():
    profile = load_profile("generic_biodata")
    raw = {
        "full_name": "Alex Example",
        "employment_history": [
            {
                "country": " Exampleland ",
                "employer": " Example Works ",
                "start_date": None,
                "end_date": " APRIL 1, 2022 ",
                "ignored": "not part of schema",
            }
        ],
    }

    result = _postprocess_result(raw, profile)
    record = result["employment_history"][0]

    assert record == {
        "country": "Exampleland",
        "employer": "Example Works",
        "start_date": "",
        "end_date": "APRIL 1, 2022",
    }
