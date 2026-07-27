# PDF BioData Extractor

[![Tests](https://github.com/nyasu12/pdf-biodata-extractor/actions/workflows/tests.yml/badge.svg)](https://github.com/nyasu12/pdf-biodata-extractor/actions/workflows/tests.yml)

PDF BioData Extractor is a profile-driven scanned-document extraction pipeline built with Google Cloud Vision OCR and OpenAI.

It converts semi-structured PDF documents such as biodata sheets and resume-style forms into configurable Excel output. Document detection rules, extracted fields, category mappings, employment handling, OCR settings, and Excel columns are defined by profiles instead of being hard-coded into the Python modules.

The repository keeps a compatibility profile for the original workflow, but new users can start from the country-neutral generic profile or create their own profile without rewriting the extraction pipeline.

## Key capabilities

- OCR for scanned PDFs using Google Cloud Vision
- structured field extraction with OpenAI
- configurable page/person detection
- profile-defined extraction fields and instructions
- structured employment-history handling
- configurable Excel columns and repeatable sections
- command-line overrides for input, output, model, profile, and OCR settings
- fictional example data for safe inspection of the data flow
- regression tests for generic and compatibility behavior
- automated public-repository safety checks for common secrets and sensitive artifacts

## Profiles at a glance

| Profile | Role | Intended use |
| --- | --- | --- |
| `generic_biodata` | Recommended starting point | Country-neutral biodata and resume-style documents |
| Custom profile | Extensible | User-defined document markers, extraction fields, employment rules, mappings, and Excel layout |
| `entertainer_jp` | Compatibility / regression-tested | Original Philippines-to-Japan entertainer biodata workflow |

`generic_biodata` is a starter profile, not a claim that every document layout works without adjustment. Documents with different headings, fields, languages, tables, or employment formats may require a custom profile.

The default profile remains `entertainer_jp` for backward compatibility with existing installations.

## Quick start for a new project

Enter the source directory and install the runtime dependencies:

```bash
cd pdf-biodata-extractor
pip install -r requirements.txt
```

Configure your Google Cloud Vision credentials and OpenAI API key, then run the generic profile:

```bash
python godmode.py \
  --profile generic_biodata \
  --input ./sample_pdfs \
  --output ./results/output.xlsx
```

For a different document type, copy one of the files in `profiles/`, adjust the JSON configuration, and pass the new profile with `--profile`.

## Requirements

- Python 3.10+
- Google Cloud Vision credentials
- OpenAI API key
- Poppler for PDF rendering

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

## Architecture

```text
repository-root/
├── .github/
│   └── workflows/
│       └── tests.yml
├── scripts/
│   └── check_public_safety.py
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
    │   ├── test_gpt_postprocess.py
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
- `scripts/check_public_safety.py` — repository-level checks for common secrets, credential artifacts, and sensitive tracked file types
- `.github/workflows/tests.yml` — public-safety validation followed by the Python test matrix

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

### `generic_biodata`

The recommended starting point for new integrations is the country-neutral generic profile. It extracts:

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

### Custom profiles

A custom profile can redefine document-start markers, extraction fields, instructions, mappings, employment rules, OCR behavior, and Excel output without editing the core Python modules.

This is the main extension point for adapting the pipeline to another document layout or business workflow.

### `entertainer_jp`

`entertainer_jp` preserves the repository's original Philippines-to-Japan entertainer workflow and remains the default for backward compatibility.

Its regression-tested behavior includes:

- surname / given names / middle name extraction
- birth, address, passport, validity, and category extraction
- `DANCER` -> `舞踏`
- `SINGER` -> `歌謡`
- Japan employment count and latest Japan work period
- non-Japan employment exported to the existing Philippines work-period columns
- multiple-person PDF splitting using biodata page markers

An existing `Credentials/config.json` containing only `OPENAI_API_KEY` continues to select this profile automatically.

## Fictional example

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

A profile controls three major areas.

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

The original defaults are preserved for compatibility.

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

## Testing and public-repository safety

The test suite does not require real OpenAI or Google Cloud credentials. It validates local behavior including:

- bundled profile structure
- country-neutral generic profile behavior
- configurable person/page detection
- OCR-tolerant BIO DATA header detection
- multiple-person text splitting
- category mapping and full-name postprocessing
- structured employment-record normalization
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

The repository also includes a public-safety scanner:

```bash
python3 scripts/check_public_safety.py
```

It inspects Git-tracked files for common API-key/token patterns, private keys, credential directories, local environment files, Google service-account indicators, and sensitive tracked file types such as PDFs and Excel workbooks. The scanner is intentionally conservative and is not a substitute for dedicated secret-management or security-review tooling.

GitHub Actions runs the public-safety check first. The Python 3.10 and Python 3.13 test jobs run only after that check passes. The workflow runs for pushes to `main` and for pull-request updates so repository-wide safety checks are not skipped just because a change is outside the Python source directory.

## Date normalization

Excel output normalizes supported date strings such as:

```text
Oct. 20, 2010 -> 2010/10/20
```

The original source text is kept during extraction and normalized only when an Excel column is configured with `"format": "date"`.

## Limitations

- `generic_biodata` is a starter profile, not a guarantee of compatibility with every biodata, resume, application form, or document layout.
- OCR accuracy depends on scan resolution, contrast, orientation, handwriting, compression, and source-document quality.
- Documents with substantially different headings, languages, table structures, or employment-history formats may need profile adjustments.
- OpenAI extraction is probabilistic. Review extracted data before using it for decisions, records, or other workflows where mistakes matter.
- The automated tests validate local parsing, profile, postprocessing, and Excel-output layers; they do not make live Google Cloud Vision or OpenAI API calls.
- The `entertainer_jp` profile is compatibility-focused and more specifically tuned than `generic_biodata`.

## Security and data handling

- Never commit `Credentials/config.json` with a real API key.
- Never commit `Credentials/vision-api-key.json` or other service-account credentials.
- Prefer environment variables or an external secret store for production credentials.
- Run `python3 scripts/check_public_safety.py` before publishing changes when working outside GitHub Actions.
- The safety scanner reduces the chance of accidental publication but cannot detect every possible secret or sensitive value.
- If a credential is accidentally published, revoke/rotate it rather than only deleting it from Git history.
- Scanned documents may contain personal or sensitive data. Live processing sends document content to the configured cloud OCR and language-model services, so confirm your privacy, retention, and organizational data-handling requirements before processing real documents.

## License

MIT
