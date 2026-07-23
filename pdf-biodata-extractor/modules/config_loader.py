import os
import json
import sys
from pathlib import Path

class AppConfig:
    BASE_DIR = os.path.normpath("C:\\temp\\GodmodePy")
    PDF_FOLDER = os.path.join(BASE_DIR, "bio_data")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
    DEBUG_FOLDER = os.path.join(OUTPUT_FOLDER, "debug")
    OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "combined_extracted_data.xlsx")
    DPI = 800

    def __init__(self):
        if getattr(sys, "frozen", False):
            app_root = Path(sys.executable).resolve().parent
        else:
            app_root = Path(__file__).resolve().parent.parent

        cred_dir = app_root / "Credentials"
        vision_path = cred_dir / "vision-api-key.json"
        config_path = cred_dir / "config.json"

        if not vision_path.exists():
            raise FileNotFoundError("vision-api-key.json が Credentials にありません。")

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(vision_path)

        if not config_path.exists():
            raise FileNotFoundError(f"{config_path} が見つかりません。APIキーを config.json に設定してください。")

        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)

        self.api_key = cfg.get("OPENAI_API_KEY")
        if not self.api_key:
            raise KeyError("config.json に OPENAI_API_KEY が設定されていません。")

        os.environ["OPENAI_API_KEY"] = self.api_key
