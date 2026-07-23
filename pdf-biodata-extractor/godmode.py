import argparse
from pathlib import Path

from pdf2image import convert_from_path

from modules.config_loader import AppConfig
from modules.document_detector import split_person_texts
from modules.excel_module import save_to_excel
from modules.gpt_module import extract_fields_with_gpt
from modules.ocr_module import extract_text_from_images


def build_parser():
    parser = argparse.ArgumentParser(
        description="Extract structured data from scanned biodata PDFs."
    )
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--profile", help="Profile name or profile JSON path")
    parser.add_argument("--input", "--input-folder", dest="input_folder", help="Input PDF folder")
    parser.add_argument("--output", "--output-file", dest="output_file", help="Output .xlsx path")
    parser.add_argument("--output-folder", help="Output folder used when OUTPUT_FILE is relative")
    parser.add_argument("--debug-folder", help="Debug image folder")
    parser.add_argument("--model", help="OpenAI model override")
    parser.add_argument("--dpi", type=int, help="PDF render DPI override")
    parser.add_argument("--no-debug", action="store_true", help="Do not save OCR debug images")
    return parser


def process_pdf(pdf_path, config: AppConfig):
    try:
        images = convert_from_path(
            str(pdf_path),
            dpi=config.dpi,
            poppler_path=config.poppler_path,
        )

        debug_folder = str(config.debug_folder) if config.debug_enabled else None
        page_texts = extract_text_from_images(
            images,
            debug_folder=debug_folder,
            settings=config.ocr,
        )

        print(f"[pdf] 総ページ数: {len(page_texts)}")
        person_texts = split_person_texts(page_texts, config.profile)

        results = []
        for index, text in enumerate(person_texts, 1):
            print(f"[gpt] {index}/{len(person_texts)} 人目を抽出中")
            result = extract_fields_with_gpt(
                text,
                api_key=config.api_key,
                profile=config.profile,
                model=config.model,
            )
            if result:
                results.append(result)
            else:
                print(f"[gpt] {index} 人目の抽出結果が空でした。")

        print(f"[pdf] 抽出成功件数: {len(results)}")
        return results

    except Exception as e:
        print(f"エラー: {e}")
        return []


def main(argv=None):
    args = build_parser().parse_args(argv)
    config = AppConfig(
        config_path=args.config,
        profile_override=args.profile,
        input_override=args.input_folder,
        output_file_override=args.output_file,
        output_folder_override=args.output_folder,
        debug_folder_override=args.debug_folder,
        model_override=args.model,
        dpi_override=args.dpi,
        debug_enabled_override=False if args.no_debug else None,
    )

    print(f"[config] {config.describe()}")

    Path(config.pdf_folder).mkdir(parents=True, exist_ok=True)
    Path(config.output_folder).mkdir(parents=True, exist_ok=True)
    if config.debug_enabled:
        Path(config.debug_folder).mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(
        path for path in Path(config.pdf_folder).iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    )

    if not pdf_files:
        print(f"PDFフォルダにファイルが見つかりません: {config.pdf_folder}")
        return 0

    results = []
    for pdf_file in pdf_files:
        print(f"処理中: {pdf_file.name}")
        data_list = process_pdf(pdf_file, config)
        if data_list:
            results.extend(data_list)

    if results:
        save_to_excel(results, config.output_file, config.profile)
        print(f"完了！{config.output_file} に保存しました。")
    else:
        print("有効なデータがありませんでした。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
