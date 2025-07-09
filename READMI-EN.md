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

## 📁 Directory Structure

C:  
└── temp  
    └── GodmodePy  
        ├── bio_data\         # Place your PDF files here (a shortcut is automatically created on the desktop)  
        ├── output\           # Extracted results will be saved here  
        │   └── debug\        # Debug images from OCR (optional)  

C:\Program Files\GodmodePyInstaller\
├── godmode.py               # Main script to run  
└── modules\                 # Supporting logic modules  
    ├── config_loader.py  
    ├── excel_module.py  
    ├── gpt_module.py  
    └── ocr_module.py  


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

This project includes an installer(https://github.com/nyasu12/pdf-biodata-extractor/releases/tag/v1.0.0) built with Inno Setup. It installs:
- Required folders
- Poppler binaries
- Google Vision key setup
- Required libraries via `install_libraries.bat`

## 📝 License

MIT License 

---

## 🤖 Sample Use Cases

- Extracting personal data from scanned biodata documents for administrative processing  
- Automating the extraction of passport and employment information  
- Translating official documents (e.g., family registers, birth certificates, resident records) into English using prompt customization  
- **Extending the tool to support other document types via prompt and Excel logic customization**

---

### ⚠️ Using this tool for other document formats?

To extract data from other types of documents (e.g., family registers or certificates), you must modify:

1. The **GPT prompt** (in `gpt_module.py`) to reflect the new fields and structure  
2. The **Excel export logic** (in `excel_module.py`) to match the new field layout  

> 📝 *Changing only the GPT prompt may result in Excel column mismatches or malformed output.*

---

### 📝 Optional: Word Output Support

Although this tool currently exports to Excel by default, it can be extended to generate **Word (.docx)** output using [`python-docx`](https://python-docx.readthedocs.io/).  
This may be useful when formatting or layout is more important than structured tabular data.



---

