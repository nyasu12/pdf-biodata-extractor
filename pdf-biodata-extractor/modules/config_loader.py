import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class AppConfig:
    """Runtime configuration with backward-compatible defaults.

    Existing installations that only contain ``OPENAI_API_KEY`` in
    ``Credentials/config.json`` continue to use the legacy entertainer profile
    and legacy working directory. New installations can override every runtime
    path and OCR/model option through config.json or CLI arguments.
    """

    DEFAULT_PROFILE = "entertainer_jp"
    DEFAULT_MODEL = "gpt-5-mini"
    DEFAULT_DPI = 800

    def __init__(
        self,
        config_path: Optional[str] = None,
        profile_override: Optional[str] = None,
        input_override: Optional[str] = None,
        output_file_override: Optional[str] = None,
        output_folder_override: Optional[str] = None,
        debug_folder_override: Optional[str] = None,
        model_override: Optional[str] = None,
        dpi_override: Optional[int] = None,
        debug_enabled_override: Optional[bool] = None,
    ) -> None:
        self.app_root = self._detect_app_root()
        self.config_path = self._resolve_config_path(config_path)
        self.config_dir = self.config_path.parent
        self._raw = self._load_json(self.config_path) if self.config_path.exists() else {}

        self.api_key = self._load_openai_api_key()
        self.model = model_override or self._get("OPENAI_MODEL", "model", default=self.DEFAULT_MODEL)

        env_profile = os.getenv("BIODATA_PROFILE")
        selected_profile = profile_override or env_profile or self._get("PROFILE", "profile", default=self.DEFAULT_PROFILE)
        profile_base = Path.cwd() if (profile_override or env_profile) else self.config_dir
        self.profile_name, self.profile_path, self.profile = self._load_profile(
            selected_profile, relative_base=profile_base
        )

        self.base_dir = self._resolve_runtime_path(
            self._get("BASE_DIR", "base_dir", default=self._default_base_dir()),
            base=self.app_root,
        )

        self.pdf_folder = (
            self._resolve_runtime_path(input_override, base=Path.cwd())
            if input_override
            else self._resolve_runtime_path(
                self._get("INPUT_FOLDER", "input_folder", default="bio_data"),
                base=self.base_dir,
            )
        )
        self.output_folder = (
            self._resolve_runtime_path(output_folder_override, base=Path.cwd())
            if output_folder_override
            else self._resolve_runtime_path(
                self._get("OUTPUT_FOLDER", "output_folder", default="output"),
                base=self.base_dir,
            )
        )
        self.debug_folder = (
            self._resolve_runtime_path(debug_folder_override, base=Path.cwd())
            if debug_folder_override
            else self._resolve_runtime_path(
                self._get("DEBUG_FOLDER", "debug_folder", default="debug"),
                base=self.output_folder,
            )
        )
        self.output_file = (
            self._resolve_runtime_path(output_file_override, base=Path.cwd())
            if output_file_override
            else self._resolve_runtime_path(
                self._get("OUTPUT_FILE", "output_file", default="combined_extracted_data.xlsx"),
                base=self.output_folder,
            )
        )

        self.dpi = int(dpi_override or self._get("DPI", "dpi", default=self.DEFAULT_DPI))
        self.debug_enabled = (
            bool(debug_enabled_override)
            if debug_enabled_override is not None
            else bool(self._get("DEBUG_ENABLED", "debug_enabled", default=True))
        )

        self.ocr = self._load_ocr_settings()
        self.poppler_path = self._load_poppler_path()
        self.vision_credentials = self._configure_google_credentials()

        # Backward-compatible aliases used by older code or external scripts.
        self.BASE_DIR = str(self.base_dir)
        self.PDF_FOLDER = str(self.pdf_folder)
        self.OUTPUT_FOLDER = str(self.output_folder)
        self.DEBUG_FOLDER = str(self.debug_folder)
        self.OUTPUT_FILE = str(self.output_file)
        self.DPI = self.dpi

    @staticmethod
    def _detect_app_root() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent.parent

    def _resolve_config_path(self, explicit_path: Optional[str]) -> Path:
        candidate = explicit_path or os.getenv("BIODATA_CONFIG")
        if candidate:
            path = Path(candidate).expanduser()
            if not path.is_absolute():
                path = (Path.cwd() / path).resolve()
            if not path.exists():
                raise FileNotFoundError(f"Config file was not found: {path}")
            return path

        # The default config file is optional when credentials are supplied via
        # environment variables. Keeping this path still gives relative settings
        # (for example VISION_CREDENTIALS) a stable base directory.
        return self.app_root / "Credentials" / "config.json"

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Config must be a JSON object: {path}")
        return data

    def _get(self, *keys: str, default: Any = None) -> Any:
        for key in keys:
            if key in self._raw:
                return self._raw[key]
        return default

    def _load_openai_api_key(self) -> str:
        key = os.getenv("OPENAI_API_KEY") or self._get("OPENAI_API_KEY", "openai_api_key")
        if not key:
            raise KeyError("OPENAI_API_KEY が設定されていません。")
        os.environ["OPENAI_API_KEY"] = str(key)
        return str(key)

    def _default_base_dir(self) -> str:
        if os.name == "nt":
            # Preserve the path used by existing installations.
            return r"C:\temp\GodmodePy"
        return str(self.app_root / "data")

    @staticmethod
    def _resolve_runtime_path(value: Any, base: Path) -> Path:
        path = Path(str(value)).expanduser()
        if not path.is_absolute():
            path = base / path
        return path.resolve(strict=False)

    def _profiles_dir(self) -> Path:
        configured = self._get("PROFILES_DIR", "profiles_dir")
        if configured:
            return self._resolve_runtime_path(configured, self.app_root)
        return self.app_root / "profiles"

    def _load_profile(self, profile_value: Any, relative_base: Optional[Path] = None):
        if not profile_value:
            profile_value = self.DEFAULT_PROFILE

        raw_value = str(profile_value)
        candidate = Path(raw_value).expanduser()
        if candidate.suffix.lower() == ".json" or candidate.parent != Path("."):
            if not candidate.is_absolute():
                candidate = ((relative_base or self.config_dir) / candidate).resolve(strict=False)
            profile_path = candidate
            profile_name = profile_path.stem
        else:
            profile_name = raw_value
            profile_path = self._profiles_dir() / f"{profile_name}.json"

        if not profile_path.exists():
            raise FileNotFoundError(f"Profile was not found: {profile_path}")

        profile = self._load_json(profile_path)
        self._validate_profile(profile, profile_path)
        return profile_name, profile_path, profile

    @staticmethod
    def _validate_profile(profile: Dict[str, Any], profile_path: Path) -> None:
        extraction = profile.get("extraction")
        excel = profile.get("excel")
        if not isinstance(extraction, dict):
            raise ValueError(f"Profile is missing extraction settings: {profile_path}")
        if not isinstance(extraction.get("fields"), list):
            raise ValueError(f"Profile extraction.fields must be a list: {profile_path}")
        if not isinstance(excel, dict):
            raise ValueError(f"Profile is missing excel settings: {profile_path}")
        if not isinstance(excel.get("columns", []), list):
            raise ValueError(f"Profile excel.columns must be a list: {profile_path}")

    def _load_ocr_settings(self) -> Dict[str, Any]:
        configured = self._get("OCR", "ocr", default={})
        if not isinstance(configured, dict):
            raise ValueError("OCR setting must be a JSON object.")

        return {
            "language_hints": configured.get("language_hints", ["en"]),
            "grayscale": bool(configured.get("grayscale", True)),
            "contrast": float(configured.get("contrast", 1.5)),
            "sharpen": bool(configured.get("sharpen", True)),
        }

    def _load_poppler_path(self) -> Optional[str]:
        configured = self._get("POPPLER_PATH", "poppler_path")
        if configured:
            path = self._resolve_runtime_path(configured, self.config_dir)
            return str(path)

        bundled = self.app_root / "poppler" / "bin"
        if bundled.exists():
            return str(bundled)
        return None

    def _configure_google_credentials(self) -> str:
        existing = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if existing and Path(existing).expanduser().exists():
            return str(Path(existing).expanduser())

        configured = self._get("VISION_CREDENTIALS", "vision_credentials")
        if configured:
            vision_path = self._resolve_runtime_path(configured, self.config_dir)
        else:
            vision_path = self.config_dir / "vision-api-key.json"

        if not vision_path.exists():
            raise FileNotFoundError(
                f"Google Vision credentials were not found: {vision_path}"
            )

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(vision_path)
        return str(vision_path)

    def describe(self) -> str:
        return (
            f"profile={self.profile_name}, input={self.pdf_folder}, "
            f"output={self.output_file}, model={self.model}, dpi={self.dpi}"
        )
