# PDF Biodata Extractor

This tool extracts structured personal information from **scanned biodata PDF files** using:

- 🧠 [OpenAI GPT-4o](https://platform.openai.com/)
- 🔍 [Google Cloud Vision OCR](https://cloud.google.com/vision/)
- 📄 Output to formatted **Excel spreadsheet (.xlsx)**

## 🔧 Features

- Converts scanned PDFs into high-resolution images (DPI = 800)
- Uses Google Vision API to perform OCR
- Sends the text to GPT-4o for structured field extraction
- Outputs to Excel with clean formatting
- Supports Japanese + English documents

## 📁 Folder Structure


## 🚀 How to Use

1. Place your scanned PDF files in `C:\temp\GodmodePy\bio_data\`
2. Ensure you have the following:
    - `vision-api-key.json` (for Google Cloud Vision)
    - `config.json` containing:
      ```json
      {
        "OPENAI_API_KEY": "sk-..."
      }
      ```
3. Run the script:
    ```bash
    python godmode.py
    ```
4. Extracted data will appear in:
    ```
    C:\temp\GodmodePy\output\combined_extracted_data.xlsx
    ```

## 🛠 Requirements

- Python 3.13
- `pandas`, `pdf2image`, `openpyxl`, `openai`, `google-cloud-vision`
- Poppler (included in installer)

## 📦 Installer

This project includes an installer built with Inno Setup. It installs:
- Required folders
- Poppler binaries
- Google Vision key setup
- Required libraries via `install_libraries.bat`

## 📝 License

MIT License (or specify another if needed)

---

## 🤖 Sample Use Cases

- Extracting bio-data for visa processing
- Automating passport + employment info parsing
- Translating official documents via prompt customization

---

Let me know if you want a Japanese version too! 😊
