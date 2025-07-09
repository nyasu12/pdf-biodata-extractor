import os
import json
from pathlib import Path

class AppConfig:
    BASE_DIR = os.path.normpath("C:\\temp\\GodmodePy")
    PDF_FOLDER = os.path.join(BASE_DIR, "bio_data")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
    DEBUG_FOLDER = os.path.join(OUTPUT_FOLDER, "debug")
    OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "combined_extracted_data.xlsx")
    DPI = 800

    def __init__(self):
        svc_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not svc_json:
            raise RuntimeError("環境変数 GOOGLE_APPLICATION_CREDENTIALS が設定されていません。")
        key_dir = Path(svc_json).parent
        config_path = key_dir / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"{config_path} が見つかりません。APIキーを config.json に設定してください。")
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        self.api_key = cfg.get("OPENAI_API_KEY")
        if not self.api_key:
            raise KeyError("config.json に OPENAI_API_KEY が設定されていません。")