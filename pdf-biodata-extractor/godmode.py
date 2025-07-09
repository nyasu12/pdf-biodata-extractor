import os
from pdf2image import convert_from_path

from modules.config_loader import AppConfig
from modules.ocr_module import extract_text_from_images
from modules.gpt_module import extract_fields_with_gpt
from modules.excel_module import save_to_excel

def process_pdf(pdf_path, config: AppConfig):
    try:
        images = convert_from_path(pdf_path, dpi=config.DPI)
        ocr_text = extract_text_from_images(images, debug_folder=config.DEBUG_FOLDER)
        result = extract_fields_with_gpt(ocr_text, api_key=config.api_key)
        return result
    except Exception as e:
        print(f"エラー: {e}")
        return {}

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
        data = process_pdf(path, config)
        if data:
            results.append(data)

    save_to_excel(results, config.OUTPUT_FILE)
    print(f"完了！{config.OUTPUT_FILE} に保存しました。")

if __name__ == "__main__":
    main()
