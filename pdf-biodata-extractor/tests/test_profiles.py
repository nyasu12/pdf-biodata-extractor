import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = PROJECT_ROOT / "profiles"


def load_profile(name: str):
    with (PROFILES_DIR / f"{name}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def test_bundled_profiles_have_required_sections():
    for name in ("entertainer_jp", "generic_biodata"):
        profile = load_profile(name)
        assert isinstance(profile.get("page_detection"), dict)
        assert isinstance(profile.get("extraction", {}).get("fields"), list)
        assert profile["extraction"]["fields"]
        assert isinstance(profile.get("excel", {}).get("columns"), list)
        assert profile["excel"]["columns"]


def test_profile_field_keys_are_unique():
    for name in ("entertainer_jp", "generic_biodata"):
        profile = load_profile(name)
        keys = [field["key"] for field in profile["extraction"]["fields"]]
        assert len(keys) == len(set(keys))


def test_entertainer_profile_preserves_business_mapping():
    profile = load_profile("entertainer_jp")
    mapping = profile["extraction"]["category_map"]
    assert mapping["DANCER"] == "舞踏"
    assert mapping["SINGER"] == "歌謡"


def test_generic_profile_is_country_neutral():
    profile = load_profile("generic_biodata")
    employment = profile["extraction"]["employment"]
    instructions = " ".join(employment.get("instructions", [])).casefold()
    assert "set country exactly to \"philippines\"" not in instructions
    assert "set country exactly to \"japan\"" not in instructions
    assert "employer" in employment["object_fields"]
