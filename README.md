# PDF BioData Extractor

[![Tests](https://github.com/nyasu12/pdf-biodata-extractor/actions/workflows/tests.yml/badge.svg)](https://github.com/nyasu12/pdf-biodata-extractor/actions/workflows/tests.yml)

PDF BioData Extractor converts scanned biodata/resume-style PDFs into structured Excel data using Google Cloud Vision OCR and OpenAI.

The project is profile-driven: document detection rules, extracted fields, category mappings, employment handling, and Excel columns can be changed without editing the Python modules.

## Support status

| Profile | Status | Intended use |
| --- | --- | --- |
| `entertainer_jp` | Primary / regression-tested | Existing Philippines-to-Japan entertainer biodata workflow |
| `generic_biodata` | Starter / reference profile | General biodata and resume-style documents |
| Custom profile | Configurable | User-defined document markers, extraction fields, employment rules, and Excel layout |

`generic_biodata` is intentionally provided as a starting point rather than a claim that every biodata or resume layout will work without adjustment. Documents with different headings, fields, languages, or employment formats may require a custom profile.

## Default behavior and backward compatibility

The default profile is `pdf-biodata-extractor/profiles/entertainer_jp.json`. It preserves the repository's existing Philippines-to-Japan entertainer workflow:

- surname / given names / middle name extraction
- birth, address, passport, validity, and category extraction
- `DANCER` -> `舞踏`
- `SINGER` -> `歌謡`
- Japan employment count and latest Japan work period
- non-Japan employment exported to the existing Philippines work-period columns
- multiple-person PDF splitting using biodata page markers

An existing `Credentials/config.json` containing only `OPENAI_API_KEY` continues to select this profile automatically.

## Architecture

```text
repository-root/
├── .github/
│   └── workflows/
│       └── tests.yml
├── README.md
├── LICENSE
└── pdf-biodata-extractor/
    ├── godmode.py
    ├── godmode_install.iss
    ├── config.example.json
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── examples/
    │   ├── sample_generic_input.txt
    │   ├── sample_generic_result.json
    │   └── sample_generic_output.csv
    ├── profiles/
    │   ├── entertainer_jp.json
    │   └── generic_biodata.json
    ├── tests/
    │   ├── test_document_detector.py
    │   ├── test_excel_output.py
    │   └── test_profiles.py
    └── modules/
        ├── config_loader.py
        ├── document_detector.py
        ├── excel_module.py
        ├── gpt_module.py
        └── ocr_module.py
```

### Responsibilities

- `config_loader.py` — runtime paths, credentials, profile loading, OCR/model settings
- `document_detector.py` — configurable person/page-start detection
- `ocr_module.py` — Google Vision OCR and configurable image preprocessing
- `gpt_module.py` — profile-driven prompt generation and structured JSON extraction
- `excel_module.py` — profile-driven Excel schema, date formatting, and repeatable employment columns
- `godmode.py` — CLI and processing pipeline

## Requirements

- Python 3.10+
- Google Cloud Vision credentials
- OpenAI API key
- Poppler for PDF rendering

Enter the source directory and install Python dependencies:

```bash
cd pdf-biodata-extractor
pip install -r requirements.txt
```

`requirements.txt` uses supported version ranges instead of completely unbounded dependencies so normal updates are allowed while future major-version breaking changes are not pulled in automatically.

## Credentials

By default the application uses the `Credentials/` directory:

```text
Credentials/
├── config.json
└── vision-api-key.json
```

`config.json` is optional when `OPENAI_API_KEY` and `GOOGLE_APPLICATION_CREDENTIALS` are supplied as environment variables.

Minimal backward-compatible `config.json`:

```json
{
  "OPENAI_API_KEY": "sk-..."
}
```

A full example is available in `pdf-biodata-extractor/config.example.json`.

Never commit real API keys or Google service-account credentials.

### Environment variables

The following can also be used:

- `OPENAI_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `BIODATA_CONFIG`
- `BIODATA_PROFILE`

## Runtime paths

For backward compatibility, Windows defaults to:

```text
C:\temp\GodmodePy\
├── bio_data\
└── output\
    └── debug\
```

All locations can be changed in `config.json`:

```json
{
  "OPENAI_API_KEY": "sk-...",
  "BASE_DIR": "./data",
  "INPUT_FOLDER": "incoming",
  "OUTPUT_FOLDER": "results",
  "DEBUG_FOLDER": "debug",
  "OUTPUT_FILE": "biodata.xlsx"
}
```

Relative paths in `config.json` are resolved from their logical parent directory. CLI path overrides such as `--input` and `--output` are resolved from the current working directory.

## Profiles

### `entertainer_jp`

Optimized for the original entertainer biodata workflow and selected by default. The automated regression tests preserve the existing Excel output contract, including Japan entry count/latest work period, dynamic Philippines work-period columns, and date normalization.

### `generic_biodata`

A country-neutral starter/reference profile that extracts:

- full name
- date/place of birth
- address
- nationality
- passport details
- occupation/category
- employment country, employer, start date, and end date

Use it with:

```bash
python godmode.py --profile generic_biodata
```

### Fictional example

The `pdf-biodata-extractor/examples/` directory contains a completely fictional example so the data flow can be inspected without exposing real personal information:

```text
sample_generic_input.txt
        ↓
sample_generic_result.json
        ↓
sample_generic_output.csv
```

The CSV is a human-readable preview of the columns that the generic profile writes to Excel. The application itself continues to produce `.xlsx` files.

## Creating a custom profile

Copy one of the files in `profiles/` and edit the JSON.

A profile controls three major areas:

### 1. Page/person detection

```json
{
  "page_detection": {
    "headers": ["BIO DATA", "PERSONAL INFORMATION"],
    "start_rules": [
      [
        ["SURNAME", "FULL NAME"],
        ["DATE OF BIRTH"],
        ["ADDRESS", "PASSPORT"]
      ]
    ]
  }
}
```

Each `start_rules` entry is an AND rule. Each nested list contains alternative phrases.

### 2. Extraction schema

```json
{
  "extraction": {
    "fields": [
      {
        "key": "full_name",
        "label": "Full Name",
        "description": "Complete name as written in the document."
      }
    ]
  }
}
```

Employment history is represented internally as structured objects rather than newline-delimited strings:

```json
{
  "employment_history": [
    {
      "country": "Japan",
      "start_date": "APRIL 19, 2025",
      "end_date": "JULY 19, 2025"
    }
  ]
}
```

This makes country filtering, counting, sorting, and Excel layout independent from the GPT prompt.

### 3. Excel schema

Normal columns and repeated employment sections are configured in the profile:

```json
{
  "excel": {
    "columns": [
      {
        "source": "full_name",
        "header": "Full Name",
        "width": 40
      }
    ],
    "repeat_sections": []
  }
}
```

Supported computed column sources include:

- `employment_count`
- `employment_latest_start`
- `employment_latest_end`

## OCR settings

OCR preprocessing can be changed without editing Python:

```json
{
  "DPI": 800,
  "OCR": {
    "language_hints": ["en"],
    "grayscale": true,
    "contrast": 1.5,
    "sharpen": true
  }
}
```

The original defaults are preserved.

## Command-line overrides

```bash
python godmode.py \
  --profile generic_biodata \
  --input ./sample_pdfs \
  --output ./results/output.xlsx \
  --dpi 600 \
  --no-debug
```

Available options:

```text
--config
--profile
--input / --input-folder
--output / --output-file
--output-folder
--debug-folder
--model
--dpi
--no-debug
```

## Poppler

When `poppler/bin` exists next to the executable, it is detected automatically. A custom location can be set with:

```json
{
  "POPPLER_PATH": "C:/path/to/poppler/bin"
}
```

This avoids requiring a machine-wide PATH modification.

## Windows installer

`godmode_install.iss` uses relative build inputs by default:

```text
dist\godmode.exe
profiles\*
vendor\poppler\Library\bin\*
```

It installs Poppler under the application directory, and the Python code auto-detects that bundled copy.

The source locations can also be overridden at compile time with Inno Setup preprocessor definitions:

```text
/DExeSource="C:\build\godmode.exe"
/DProfilesSource="C:\build\profiles\*"
/DPopplerBinSource="C:\poppler\Library\bin\*"
/DInstallerOutputDir="C:\InstallerOutput"
```

## Building an executable

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Example PyInstaller build:

```bash
pyinstaller --onefile --name godmode godmode.py
```

Keep the `profiles` directory beside `godmode.exe`, or include/copy it as part of your packaging workflow. The provided Inno Setup script copies `profiles/` beside the installed executable.

## Testing

The test suite does not require real OpenAI or Google Cloud credentials. It tests local behavior including:

- bundled profile structure
- country-neutral generic profile behavior
- configurable person/page detection
- OCR-tolerant BIO DATA header detection
- multiple-person text splitting
- `Oct. 20, 2010` date normalization
- backward-compatible entertainer Excel columns
- Japan entry count and latest Japan work period
- dynamic Philippines work-period columns
- generic employment country/employer output

Run locally:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions runs the same suite on Python 3.10 and Python 3.13 for pull requests and pushes to `main` that affect the project.

## Date normalization

Excel output normalizes supported date strings such as:

```text
Oct. 20, 2010 -> 2010/10/20
```

The original source text is kept during extraction and normalized only when an Excel column is configured with `"format": "date"`.

## Limitations

- `generic_biodata` is a starter/reference profile, not a guarantee of compatibility with every biodata, resume, or application form.
- OCR accuracy depends on scan resolution, contrast, orientation, handwriting, compression, and source-document quality.
- Documents with substantially different headings, languages, table structures, or employment-history formats may need profile adjustments.
- OpenAI extraction is probabilistic. Review extracted data before using it for decisions, records, or other workflows where mistakes matter.
- The automated tests validate the local parsing, profile, and Excel-output layers; they do not make live Google Cloud Vision or OpenAI API calls.
- The `entertainer_jp` profile is the compatibility-focused profile for the original workflow and is more specifically tuned than `generic_biodata`.

## Security

- Never commit `Credentials/config.json` with a real API key.
- Never commit `Credentials/vision-api-key.json`.
- Environment variables may be used instead of credential files.
- If a credential is accidentally published, revoke/rotate it rather than only deleting it from Git history.

## License

MIT
