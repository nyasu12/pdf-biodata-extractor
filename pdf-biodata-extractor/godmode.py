import os
import re
from pdf2image import convert_from_path

from modules.config_loader import AppConfig
from modules.ocr_module import extract_text_from_images
from modules.gpt_module import extract_fields_with_gpt
from modules.excel_module import save_to_excel


def normalize_for_detection(text: str) -> str:
    if not text:
        return ""

    t = text.upper()
    t = t.replace("BL0", "BIO")
    t = t.replace("BLO", "BIO")
    t = t.replace("8IO", "BIO")
    t = t.replace("BI0", "BIO")
    t = t.replace("BlO", "BIO")
    t = t.replace("IIO", "BIO")
    t = t.replace("_", " ")
    t = t.replace("-", " ")
    t = re.sub(r"[^\w\s/]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    return t


def is_person_start_page(text: str) -> bool:
    raw = text or ""
    t = normalize_for_detection(raw)

    if not t:
        return False

    bio_patterns = [
        r"\bBIO\s+DATA\b",
        r"\bBIODATA\b",
        r"\bBIO\s+DATA\s+SHEET\b",
        r"\bBIOGRAPHICAL\s+DATA\b",
    ]
    has_bio_header = any(re.search(p, t) for p in bio_patterns)

    has_name_fields = (
        "SURNAME" in t
        and (
            "GIVEN NAME" in t
            or "GIVEN NAMES" in t
            or "FIRST NAME" in t
        )
    )

    has_identity_fields = (
        ("DATE OF BIRTH" in t or "BIRTH DATE" in t)
        and ("PLACE OF BIRTH" in t or "PASSPORT" in t)
    )

    has_profile_block = (
        ("PRESENT ADDRESS" in t or "ADDRESS" in t)
        and ("CATEGORY" in t or "PASSPORT" in t)
    )

    if has_bio_header:
        return True

    if has_name_fields and has_identity_fields:
        return True

    if has_name_fields and has_profile_block:
        return True

    return False


def split_person_texts(page_texts):
    person_starts = []

    for i, t in enumerate(page_texts):
        if is_person_start_page(t):
            print(f"[split] 人物開始を検出: page {i + 1}")
            person_starts.append(i)

    persons = []

    if not person_starts:
        if page_texts:
            print("[split] 人物開始を検出できなかったため、PDF全体を1件として処理します。")
            persons.append("\n".join(page_texts))
        return persons

    deduped_starts = []
    for idx in person_starts:
        if not deduped_starts or deduped_starts[-1] != idx:
            deduped_starts.append(idx)

    deduped_starts.append(len(page_texts))

    for idx in range(len(deduped_starts) - 1):
        s = deduped_starts[idx]
        e = deduped_starts[idx + 1]
        chunk = "\n".join(page_texts[s:e]).strip()
        if chunk:
            persons.append(chunk)

    print(f"[split] 分割結果: {len(persons)} 人分")
    return persons


def finalize_japan_fields(result):
    periods_str = (result.get("Japan Work Periods") or "").strip()
    if not periods_str or periods_str == "なし":
        result["Japan Entry Count"] = 0
        result["Japan Work Period Start"] = ""
        result["Japan Work Period End"] = ""
        return result

    lines = [l for l in periods_str.splitlines() if l.strip()]
    result["Japan Entry Count"] = len(lines)

    latest = lines[-1].strip()
    parts = re.split(r"\s+TO\s+", latest, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) == 2:
        start_str = parts[0].strip()
        end_str = parts[1].strip()
    else:
        start_str = latest
        end_str = ""

    result["Japan Work Period Start"] = start_str
    result["Japan Work Period End"] = end_str
    return result


def process_pdf(pdf_path, config: AppConfig):
    try:
        images = convert_from_path(pdf_path, dpi=config.DPI)
        page_texts = extract_text_from_images(images, debug_folder=config.DEBUG_FOLDER)

        print(f"[pdf] 総ページ数: {len(page_texts)}")
        person_texts = split_person_texts(page_texts)

        results = []
        for idx, text in enumerate(person_texts, 1):
            print(f"[gpt] {idx}/{len(person_texts)} 人目を抽出中")
            result = extract_fields_with_gpt(text, api_key=config.api_key)
            if result:
                result = finalize_japan_fields(result)
                results.append(result)
            else:
                print(f"[gpt] {idx} 人目の抽出結果が空でした。")

        print(f"[pdf] 抽出成功件数: {len(results)}")
        return results

    except Exception as e:
        print(f"エラー: {e}")
        return []


def main():
    config = AppConfig()

    os.makedirs(config.DEBUG_FOLDER, exist_ok=True)
    pdf_files = [f for f in os.listdir(config.PDF_FOLDER) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("PDFフォルダにファイルが見つかりません。")
        return

    results = []
    for file in pdf_files:
        print(f"処理中: {file}")
        path = os.path.join(config.PDF_FOLDER, file)
        data_list = process_pdf(path, config)
        if data_list:
            results.extend(data_list)

    if results:
        save_to_excel(results, config.OUTPUT_FILE)
        print(f"完了！{config.OUTPUT_FILE} に保存しました。")
    else:
        print("有効なデータがありませんでした。")


if __name__ == "__main__":
    main()
