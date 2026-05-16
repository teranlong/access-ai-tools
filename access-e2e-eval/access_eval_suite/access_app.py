from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Any

from . import constants as ac
from .config import AccessEvalConfig


class AccessAppError(RuntimeError):
    pass


@dataclass
class AccessAppSession:
    config: AccessEvalConfig
    app: object
    window: object

    @classmethod
    def open(cls, config: AccessEvalConfig) -> "AccessAppSession":
        try:
            import win32com.client
            from pywinauto import Desktop
        except ImportError as exc:
            raise AccessAppError(
                "pywin32 and pywinauto are required for Access UI automation."
            ) from exc

        app = win32com.client.Dispatch("Access.Application")
        try:
            app.Visible = config.visible
        except Exception:
            pass
        app.OpenCurrentDatabase(str(config.database_path))
        app.DoCmd.OpenForm(config.startup_form)
        time.sleep(1)

        errors: list[str] = []
        window = None
        window_handle = app.hWndAccessApp
        if callable(window_handle):
            window_handle = window_handle()

        for backend in _backend_candidates(config.ui_backend):
            try:
                candidate = Desktop(backend=backend).window(handle=window_handle)
                candidate.wait("visible ready", timeout=config.timeout_seconds)
                window = candidate
                break
            except Exception as exc:  # noqa: BLE001 - include pywinauto diagnostic.
                errors.append(f"{backend}: {exc}")

        if window is None:
            app.Quit(ac.AC_QUIT_SAVE_NONE)
            raise AccessAppError(
                "Could not attach pywinauto to the Access window. "
                "Run from an interactive Windows desktop session. "
                f"Backend errors: {' | '.join(errors)}"
            )

        return cls(config=config, app=app, window=window)

    def close(self) -> None:
        try:
            self.app.CloseCurrentDatabase()
        finally:
            self.app.Quit(ac.AC_QUIT_SAVE_NONE)
            time.sleep(0.5)

    def open_form(self, form_name: str, where: str | None = None) -> None:
        if where:
            self.app.DoCmd.OpenForm(form_name, ac.AC_NORMAL, "", where)
        else:
            self.app.DoCmd.OpenForm(form_name, ac.AC_NORMAL)
        time.sleep(0.5)
        self.window.set_focus()

    def go_to_new_record(self) -> None:
        import pythoncom

        self.app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.25)
        self.window.set_focus()

    def go_to_control(self, control_name: str) -> None:
        self.app.DoCmd.GoToControl(control_name)
        time.sleep(0.1)
        self.window.set_focus()

    def save_record(self) -> None:
        from pywinauto.keyboard import send_keys

        self.window.set_focus()
        send_keys("^s")
        time.sleep(0.5)
        try:
            active_form = self.app.Screen.ActiveForm
            if active_form.Dirty:
                raise AccessAppError(
                    f"Access did not save the active form {active_form.Name!r}; "
                    "the record is still dirty, likely because validation failed."
                )
        except AccessAppError:
            raise
        except Exception:
            pass

    def refresh(self) -> None:
        from pywinauto.keyboard import send_keys

        self.app.RefreshDatabaseWindow()
        self.window.set_focus()
        send_keys("{F5}")
        time.sleep(0.5)

    def rows(self, sql: str) -> list[dict[str, Any]]:
        recordset = self.app.CurrentDb().OpenRecordset(sql)
        try:
            if recordset.EOF:
                return []
            fields = [recordset.Fields(index).Name for index in range(recordset.Fields.Count)]
            results: list[dict[str, Any]] = []
            while not recordset.EOF:
                results.append(
                    {
                        field_name: recordset.Fields(field_name).Value
                        for field_name in fields
                    }
                )
                recordset.MoveNext()
            return results
        finally:
            recordset.Close()

    def scalar(self, sql: str) -> Any:
        rows = self.rows(sql)
        if not rows:
            return None
        return next(iter(rows[0].values()))


def build_config_for_database(database_path: Path, startup_form: str = "CompanyList") -> AccessEvalConfig:
    env_config = AccessEvalConfig.from_env()
    return AccessEvalConfig(
        database_path=database_path,
        access_exe=env_config.access_exe,
        ui_backend=env_config.ui_backend,
        startup_form=startup_form,
        visible=env_config.visible,
        timeout_seconds=env_config.timeout_seconds,
    )


def _backend_candidates(preferred: str) -> tuple[str, ...]:
    candidates = [preferred]
    for backend in ("uia", "win32"):
        if backend not in candidates:
            candidates.append(backend)
    return tuple(candidates)
