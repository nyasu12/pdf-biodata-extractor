import json
from pathlib import Path

from modules.document_detector import is_person_start_page, split_person_texts


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_profile(name: str):
    with (PROJECT_ROOT / "profiles" / f"{name}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def test_generic_profile_detects_standard_header():
    profile = load_profile("generic_biodata")
    text = "PERSONAL INFORMATION\nFULL NAME: Alex Example\nDATE OF BIRTH: JANUARY 1, 1990"
    assert is_person_start_page(text, profile)


def test_entertainer_profile_tolerates_bio_ocr_confusion():
    profile = load_profile("entertainer_jp")
    text = "BL0 DATA\nSURNAME: SAMPLE\nGIVEN NAME: MARIA"
    assert is_person_start_page(text, profile)


def test_split_person_texts_splits_multiple_biodata_records():
    profile = load_profile("generic_biodata")
    pages = [
        "BIO DATA\nFULL NAME: ALEX EXAMPLE\nDATE OF BIRTH: JANUARY 1, 1990",
        "EMPLOYMENT HISTORY\nExample Company",
        "BIO DATA\nFULL NAME: JAMIE SAMPLE\nDATE OF BIRTH: FEBRUARY 2, 1991",
        "EMPLOYMENT HISTORY\nSample Company",
    ]

    persons = split_person_texts(pages, profile)

    assert len(persons) == 2
    assert "ALEX EXAMPLE" in persons[0]
    assert "JAMIE SAMPLE" in persons[1]


def test_split_falls_back_to_single_record_without_marker():
    profile = load_profile("generic_biodata")
    pages = ["UNFAMILIAR FORM", "SECOND PAGE"]
    assert split_person_texts(pages, profile) == ["UNFAMILIAR FORM\nSECOND PAGE"]
