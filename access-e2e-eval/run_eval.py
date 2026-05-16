from __future__ import annotations

import subprocess
import sys

from access_eval_suite.config import AccessEvalConfig
from access_eval_suite.db_builder import create_sample_database
from access_eval_suite.environment import inspect_environment


def main() -> int:
    status = inspect_environment()
    print(f"Python bitness: {status.python_bitness}")
    print(f"pywin32 installed: {status.has_pywin32}")
    print(f"pywinauto installed: {status.has_pywinauto}")
    print(f"pyodbc installed: {status.has_pyodbc}")
    print(f"ACE drivers: {', '.join(status.ace_drivers) or 'none detected'}")

    config = AccessEvalConfig.from_env()
    if status.has_pywin32:
        create_sample_database(config.database_path)
        print(f"Sample database ready: {config.database_path}")

    return subprocess.call([sys.executable, "-m", "pytest"])


if __name__ == "__main__":
    raise SystemExit(main())
