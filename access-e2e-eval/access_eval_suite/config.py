from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "generated"
DEFAULT_DATABASE = GENERATED_DIR / "access_e2e_sample.accdb"


@dataclass(frozen=True)
class AccessEvalConfig:
    database_path: Path = DEFAULT_DATABASE
    access_exe: str | None = None
    ui_backend: str = "uia"
    startup_form: str = "CompanyList"
    visible: bool = True
    timeout_seconds: int = 15

    @classmethod
    def from_env(cls) -> "AccessEvalConfig":
        database = Path(os.environ.get("ACCESS_E2E_DB", str(DEFAULT_DATABASE)))
        return cls(
            database_path=database,
            access_exe=os.environ.get("ACCESS_EXE") or None,
            ui_backend=os.environ.get("ACCESS_E2E_BACKEND", "uia"),
            startup_form=os.environ.get("ACCESS_E2E_STARTUP_FORM", "CompanyList"),
            visible=os.environ.get("ACCESS_E2E_VISIBLE", "1") != "0",
            timeout_seconds=int(os.environ.get("ACCESS_E2E_TIMEOUT", "15")),
        )
