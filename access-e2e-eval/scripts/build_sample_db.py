from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from access_eval_suite.config import AccessEvalConfig
from access_eval_suite.db_builder import create_sample_database


def main() -> None:
    config = AccessEvalConfig.from_env()
    built = create_sample_database(config.database_path)
    print(f"Built Access evaluation database: {built.path}")
    print(f"Tables: {', '.join(built.tables)}")
    print(f"Forms: {', '.join(built.forms)}")


if __name__ == "__main__":
    main()
