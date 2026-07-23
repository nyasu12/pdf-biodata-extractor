import re
from typing import Any, Dict, Iterable, List


def normalize_for_detection(text: str, detection: Dict[str, Any]) -> str:
    if not text:
        return ""

    value = text.upper()

    replacements = detection.get("ocr_replacements", {}) or {}
    if isinstance(replacements, dict):
        for old, new in replacements.items():
            value = value.replace(str(old).upper(), str(new).upper())

    value = value.replace("_", " ")
    value = value.replace("-", " ")
    value = re.sub(r"[^\w\s/]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _contains_any(text: str, phrases: Iterable[str]) -> bool:
    return any(str(phrase).upper() in text for phrase in phrases if str(phrase).strip())


def _rule_matches(text: str, rule: Any) -> bool:
    """A rule is a list of required groups; each group may contain alternatives."""
    if not isinstance(rule, list) or not rule:
        return False

    for group in rule:
        if isinstance(group, str):
            alternatives = [group]
        elif isinstance(group, list):
            alternatives = group
        else:
            return False

        if not _contains_any(text, alternatives):
            return False

    return True


def is_person_start_page(text: str, profile: Dict[str, Any]) -> bool:
    detection = profile.get("page_detection", {}) or {}
    normalized = normalize_for_detection(text or "", detection)
    if not normalized:
        return False

    headers = detection.get("headers", []) or []
    if _contains_any(normalized, headers):
        return True

    start_rules = detection.get("start_rules", []) or []
    return any(_rule_matches(normalized, rule) for rule in start_rules)


def split_person_texts(page_texts: List[str], profile: Dict[str, Any]) -> List[str]:
    person_starts = []

    for index, text in enumerate(page_texts):
        if is_person_start_page(text, profile):
            print(f"[split] 人物開始を検出: page {index + 1}")
            person_starts.append(index)

    if not person_starts:
        if page_texts:
            print("[split] 人物開始を検出できなかったため、PDF全体を1件として処理します。")
            return ["\n".join(page_texts)]
        return []

    starts = []
    for index in person_starts:
        if not starts or starts[-1] != index:
            starts.append(index)
    starts.append(len(page_texts))

    persons = []
    for index in range(len(starts) - 1):
        start = starts[index]
        end = starts[index + 1]
        chunk = "\n".join(page_texts[start:end]).strip()
        if chunk:
            persons.append(chunk)

    print(f"[split] 分割結果: {len(persons)} 人分")
    return persons
