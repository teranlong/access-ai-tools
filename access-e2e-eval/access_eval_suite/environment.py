from __future__ import annotations

import importlib.util
import platform
from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyStatus:
    python_bitness: str
    has_pywin32: bool
    has_pywinauto: bool
    has_pyodbc: bool
    ace_drivers: tuple[str, ...]

    @property
    def has_access_com_support(self) -> bool:
        return self.has_pywin32


def module_available(module_name: str) -> bool:
    root_name = module_name.split(".", 1)[0]
    return importlib.util.find_spec(root_name) is not None


def inspect_environment() -> DependencyStatus:
    ace_drivers: tuple[str, ...] = ()
    if module_available("pyodbc"):
        import pyodbc

        ace_drivers = tuple(
            driver
            for driver in pyodbc.drivers()
            if "Access Driver" in driver or "Microsoft Access" in driver
        )

    return DependencyStatus(
        python_bitness=platform.architecture()[0],
        has_pywin32=module_available("win32com.client"),
        has_pywinauto=module_available("pywinauto"),
        has_pyodbc=module_available("pyodbc"),
        ace_drivers=ace_drivers,
    )


def access_skip_reason() -> str | None:
    status = inspect_environment()
    missing = []
    if not status.has_pywin32:
        missing.append("pywin32")
    if not status.has_pywinauto:
        missing.append("pywinauto")

    if missing:
        return (
            f"Missing required Python package(s): {', '.join(missing)}. "
            "Install requirements.txt on a Windows machine with Microsoft Access."
        )
    return None
