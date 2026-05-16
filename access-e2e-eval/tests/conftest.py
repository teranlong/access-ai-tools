from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys
import time

import pytest

from access_eval_suite.config import DEFAULT_DATABASE, ROOT
from access_eval_suite.environment import access_skip_reason, inspect_environment


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "access_e2e: requires Microsoft Access desktop application and interactive Windows session",
    )


@pytest.fixture(scope="session")
def dependency_status():
    return inspect_environment()


@pytest.fixture(scope="session")
def built_database(dependency_status):
    reason = access_skip_reason()
    if reason:
        pytest.skip(reason)
    if DEFAULT_DATABASE.exists():
        DEFAULT_DATABASE.unlink()

    env = os.environ.copy()
    env["ACCESS_E2E_DB"] = str(DEFAULT_DATABASE)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_sample_db.py")],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
        check=False,
    )
    if result.returncode != 0 or not DEFAULT_DATABASE.exists():
        pytest.skip(
            "Could not build sample Access database in isolated subprocess. "
            f"Exit code: {result.returncode}. Output:\n{result.stdout[-4000:]}"
        )

    class Built:
        path = DEFAULT_DATABASE

    return Built()


@pytest.fixture()
def test_database(tmp_path: Path, built_database):
    destination = tmp_path / "access_e2e_under_test.accdb"
    shutil.copy2(built_database.path, destination)
    yield destination
    lock_file = destination.with_suffix(".laccdb")
    if lock_file.exists():
        deadline = time.time() + 5
        while lock_file.exists() and time.time() < deadline:
            time.sleep(0.25)
        if lock_file.exists():
            try:
                lock_file.unlink()
            except OSError:
                pass
