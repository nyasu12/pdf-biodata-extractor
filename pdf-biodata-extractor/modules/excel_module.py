import os
import re
import datetime
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter


def normalize_date_string(value):
    text = (value or "").strip()
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\b([A-Za-z]{3,9})\.(\s+\d{1,2},\s+\d{4}\b)", r"\1\2", text, flags=re.IGNORECASE)
    text = re.sub(r"\bSEPT\b", "SEP", text, flags=re.IGNORECASE)

    patterns = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
    ]

    for fmt in patterns:
        try:
            dt = datetime.datetime.strptime(text.title(), fmt)
            return dt.strftime("%Y/%m/%d")
        except ValueError:
            pass

    return text


def parse_date_for_sort(value):
    text = normalize_date_string(value)
    if not text:
        return None

    try:
        return datetime.datetime.strptime(text, "%Y/%m/%d")
    except ValueError:
        return None


def split_period_line(text):
    s = (text or "").strip()
    if not s:
        return "", ""

    parts = re.split(r"\s+TO[:\s-]*", s, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()

    return s, ""


def save_to_excel(data_list, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    base_columns = [
        "Full Name", "Date of Birth", "Passport Number", "Place of Birth",
        "Present Address", "Valid Until", "Category",
        "Japan Entry Count",
        "Japan Work Period Start", "Japan Work Period End"
    ]

    max_ph_periods = 0
    for row in data_list:
        periods_str = (row.get("Philippines Work Periods") or "").strip()
        if not periods_str or periods_str == "なし":
            continue
        lines = [l for l in periods_str.splitlines() if l.strip()]
        if len(lines) > max_ph_periods:
            max_ph_periods = len(lines)

    ph_columns = []
    for i in range(1, max_ph_periods + 1):
        ph_columns.append(f"Philippines Work Period Start {i}")
        ph_columns.append(f"Philippines Work Period End {i}")

    columns = base_columns + ph_columns

    rows = []
    for row in data_list:
        out = {}
        for k in base_columns:
            out[k] = row.get(k, "")

        out["Date of Birth"] = normalize_date_string(out.get("Date of Birth", ""))
        out["Valid Until"] = normalize_date_string(out.get("Valid Until", ""))
        out["Japan Work Period Start"] = normalize_date_string(out.get("Japan Work Period Start", ""))
        out["Japan Work Period End"] = normalize_date_string(out.get("Japan Work Period End", ""))

        periods_str = (row.get("Philippines Work Periods") or "").strip()
        lines_raw = [l for l in periods_str.splitlines() if l.strip()]

        entries = []
        for line in lines_raw:
            start_str, end_str = split_period_line(line)

            start_norm = normalize_date_string(start_str)
            end_norm = normalize_date_string(end_str)
            start_dt = parse_date_for_sort(start_str)

            entries.append({
                "start": start_norm,
                "end": end_norm,
                "start_dt": start_dt
            })

        with_date = [e for e in entries if e["start_dt"] is not None]
        without_date = [e for e in entries if e["start_dt"] is None]
        with_date.sort(key=lambda e: e["start_dt"])
        ordered = with_date + without_date

        for idx in range(max_ph_periods):
            start_col = f"Philippines Work Period Start {idx+1}"
            end_col = f"Philippines Work Period End {idx+1}"
            if idx < len(ordered):
                out[start_col] = ordered[idx]["start"]
                out[end_col] = ordered[idx]["end"]
            else:
                out[start_col] = ""
                out[end_col] = ""

        rows.append(out)

    df = pd.DataFrame(rows, columns=columns)
    df.to_excel(output_path, index=False)

    wb = load_workbook(output_path)
    ws = wb.active

    widths = [40, 20, 20, 30, 45, 20, 20, 10, 25, 25]
    for _ in range(max_ph_periods):
        widths.append(25)
        widths.append(25)

    for i, width in enumerate(widths, 1):
        col = get_column_letter(i)
        ws.column_dimensions[col].width = width

    for row in ws.iter_rows():
        ws.row_dimensions[row[0].row].height = 25
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="center")

    wb.save(output_path)
