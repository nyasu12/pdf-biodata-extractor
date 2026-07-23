import json
import re
from typing import Any, Dict, List

from openai import OpenAI


def _empty_result(profile: Dict[str, Any]) -> Dict[str, Any]:
    extraction = profile.get("extraction", {}) or {}
    result = {}
    for field in extraction.get("fields", []) or []:
        key = field.get("key")
        if key:
            result[key] = ""

    employment = extraction.get("employment", {}) or {}
    if employment.get("enabled", False):
        result[employment.get("key", "employment_history")] = []

    return _postprocess_result(result, profile)


def _json_example(profile: Dict[str, Any]) -> Dict[str, Any]:
    extraction = profile.get("extraction", {}) or {}
    example = {}

    for field in extraction.get("fields", []) or []:
        key = field.get("key")
        if key:
            example[key] = ""

    employment = extraction.get("employment", {}) or {}
    if employment.get("enabled", False):
        object_fields = employment.get("object_fields") or ["country", "start_date", "end_date"]
        example[employment.get("key", "employment_history")] = [
            {field: "" for field in object_fields}
        ]

    return example


def _build_prompt(ocr_text: str, profile: Dict[str, Any]) -> str:
    extraction = profile.get("extraction", {}) or {}
    lines: List[str] = []
    lines.append("Extract structured information from the OCR text below.")
    lines.append("")
    lines.append("Fields:")

    for field in extraction.get("fields", []) or []:
        key = field.get("key", "")
        label = field.get("label", key)
        description = field.get("description", "")
        lines.append(f'- "{key}" ({label}): {description}'.rstrip())

    employment = extraction.get("employment", {}) or {}
    if employment.get("enabled", False):
        key = employment.get("key", "employment_history")
        object_fields = employment.get("object_fields") or ["country", "start_date", "end_date"]
        lines.append("")
        lines.append(f'Employment records must be returned in "{key}" as a JSON array.')
        lines.append("Each item must contain: " + ", ".join(f'"{f}"' for f in object_fields) + ".")
        for instruction in employment.get("instructions", []) or []:
            lines.append(f"- {instruction}")

    category_map = extraction.get("category_map", {}) or {}
    if category_map:
        lines.append("")
        lines.append("Category values may be returned as written in the source; the program applies configured category mapping after extraction.")

    instructions = extraction.get("general_instructions", []) or []
    if instructions:
        lines.append("")
        lines.append("Rules:")
        for instruction in instructions:
            lines.append(f"- {instruction}")

    lines.append("")
    lines.append("Return only one valid JSON object. Do not add explanations or Markdown code fences.")
    lines.append("Use empty strings for missing scalar fields and [] when there are no employment records.")
    lines.append("")
    lines.append("Required JSON shape:")
    lines.append(json.dumps(_json_example(profile), ensure_ascii=False, indent=2))
    lines.append("")
    lines.append("OCR text:")
    lines.append(ocr_text)
    return "\n".join(lines)


def _extract_response_text(response: Any) -> str:
    content = getattr(response, "output_text", None)
    if content:
        return str(content)

    texts = []
    for item in getattr(response, "output", []) or []:
        for content_item in getattr(item, "content", []) or []:
            text_obj = getattr(content_item, "text", None)
            if text_obj:
                if hasattr(text_obj, "value"):
                    texts.append(str(text_obj.value))
                else:
                    texts.append(str(text_obj))
    return "\n".join(texts)


def _clean_json_text(content: str) -> str:
    text = (content or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _normalize_employment_records(value: Any, object_fields: List[str]) -> List[Dict[str, str]]:
    if not isinstance(value, list):
        return []

    records = []
    for item in value:
        if not isinstance(item, dict):
            continue
        normalized = {}
        for field in object_fields:
            raw = item.get(field, "")
            normalized[field] = "" if raw is None else str(raw).strip()
        records.append(normalized)
    return records


def _apply_category_map(result: Dict[str, Any], extraction: Dict[str, Any]) -> None:
    category_map = extraction.get("category_map", {}) or {}
    category_field = extraction.get("category_field", "category")
    raw = result.get(category_field)
    if raw is None or not category_map:
        return

    normalized_map = {str(k).strip().upper(): v for k, v in category_map.items()}
    mapped = normalized_map.get(str(raw).strip().upper())
    if mapped is not None:
        result[category_field] = mapped


def _build_full_name(result: Dict[str, Any], extraction: Dict[str, Any]) -> None:
    full_name = extraction.get("full_name") or {}
    if not full_name:
        return

    target = full_name.get("target", "full_name")
    parts = full_name.get("parts", []) or []
    separator = str(full_name.get("separator", " "))
    preserve_empty = bool(full_name.get("preserve_empty_parts", False))

    values = [str(result.get(part, "") or "").strip() for part in parts]
    if not any(values):
        result[target] = ""
        return
    if not preserve_empty:
        values = [value for value in values if value]
    result[target] = separator.join(values)


def _postprocess_result(result: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    extraction = profile.get("extraction", {}) or {}
    cleaned: Dict[str, Any] = {}

    for field in extraction.get("fields", []) or []:
        key = field.get("key")
        if not key:
            continue
        raw = result.get(key, "")
        cleaned[key] = "" if raw is None else str(raw).strip()

    employment = extraction.get("employment", {}) or {}
    if employment.get("enabled", False):
        key = employment.get("key", "employment_history")
        object_fields = employment.get("object_fields") or ["country", "start_date", "end_date"]
        cleaned[key] = _normalize_employment_records(result.get(key, []), object_fields)

    _apply_category_map(cleaned, extraction)
    _build_full_name(cleaned, extraction)
    return cleaned


def extract_fields_with_gpt(ocr_text, api_key, profile, model="gpt-5-mini"):
    if not (ocr_text or "").strip():
        print("⚠️ OCR結果が空だったため、GPTによる抽出をスキップします。")
        return _empty_result(profile)

    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(ocr_text, profile)

    system_prompt = (
        profile.get("extraction", {}).get("system_prompt")
        or "You extract structured data from documents accurately. Return only valid JSON."
    )

    try:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )

        content = _extract_response_text(response)
        if not content.strip():
            print("⚠️ GPT応答が空でした。")
            return {}

        parsed = json.loads(_clean_json_text(content))
        if not isinstance(parsed, dict):
            raise ValueError("GPT output JSON was not an object.")

        return _postprocess_result(parsed, profile)

    except Exception as e:
        print("❌ GPT出力のJSON変換またはAPI呼び出しに失敗:", e)
        return {}
