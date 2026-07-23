# PDF BioData Extractor

PDF BioData Extractor reads scanned biodata PDFs, extracts structured personal and employment information, and exports the result to Excel.

## Current stack

- OpenAI GPT-5 mini via the Responses API
- Google Cloud Vision `document_text_detection`
- `pdf2image` for PDF rendering
- `pandas` + `openpyxl` for Excel output
- Inno Setup for the Windows installer

## Current features

- High-resolution PDF rendering (DPI 800)
- OCR preprocessing with grayscale, contrast enhancement, and sharpening
- Page-by-page OCR using Google Cloud Vision
- Automatic detection and splitting of multiple people contained in one PDF
- Structured extraction of name, birth details, passport details, address, category, and employment history
- Separate Japan and Philippines employment-period extraction
- Japan entry count and latest Japan work-period calculation
- Excel export with dynamically generated Philippines work-period columns
- Date normalization such as `Oct. 20, 2010` -> `2010/10/20`
- Packaged Windows executable support with a local `Credentials` folder

## Source structure

```text
pdf-biodata-extractor/
├── godmode.py
├── godmode_install.iss
└── modules/
    ├── config_loader.py
    ├── excel_module.py
    ├── gpt_module.py
    └── ocr_module.py
```

## Runtime folders

```text
C:\temp\GodmodePy\
├── bio_data\
├── output\
└── output\debug\
```

The installed application keeps API credentials in:

```text
C:\Program Files\GodmodePyInstaller\Credentials\
```

Place these two files in the `Credentials` folder:

- `vision-api-key.json` — Google Cloud Vision service-account credentials
- `config.json` — OpenAI API configuration

Example `config.json`:

```json
{
  "OPENAI_API_KEY": "sk-..."
}
```

> Never commit real API keys or credential JSON files to this repository.

## Running from source

Install the Python dependencies required by the source version, then run:

```bash
python godmode.py
```

Place input PDFs in:

```text
C:\temp\GodmodePy\bio_data\
```

The combined Excel result is written to:

```text
C:\temp\GodmodePy\output\combined_extracted_data.xlsx
```

## Windows installer

`godmode_install.iss` is the current Inno Setup definition. Version 2 installs the packaged `godmode.exe`, creates the working folders and shortcuts, and leaves credentials outside the repository/source package.

## Notes

The extraction prompt and Excel schema are intentionally coupled. When adding or renaming extracted fields, update both `modules/gpt_module.py` and `modules/excel_module.py` together.

## License

MIT
