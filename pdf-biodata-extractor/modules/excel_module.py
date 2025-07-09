import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

def save_to_excel(data_list, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    columns = [
        "Full Name", "Date of Birth", "Passport Number", "Place of Birth",
        "Present Address", "Valid Until", "Category",
        "Japan Work Period Start", "Japan Work Period End"
    ]
    df = pd.DataFrame(data_list, columns=columns)
    df.to_excel(output_path, index=False)

    wb = load_workbook(output_path)
    ws = wb.active
    widths = [40, 20, 20, 30, 45, 20, 20, 25, 25]
    for i, width in enumerate(widths, 1):
        col = chr(64 + i) if i <= 26 else 'A' + chr(64 + (i - 26))
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows():
        ws.row_dimensions[row[0].row].height = 25
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="center")
    wb.save(output_path)