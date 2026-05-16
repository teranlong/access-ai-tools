from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FieldEntry:
    control_name: str
    value: Any


class AccessUiDriver:
    def __init__(self, session):
        self.session = session

    def type_into_control(self, control_name: str, value: Any) -> None:
        from pywinauto.keyboard import send_keys

        self.session.go_to_control(control_name)
        if isinstance(value, bool):
            if value:
                send_keys("{SPACE}")
            return
        text = "" if value is None else str(value)
        send_keys("^a{BACKSPACE}")
        if text:
            send_keys(text, with_spaces=True, pause=0.01)

    def fill_form(self, fields: list[FieldEntry] | dict[str, Any]) -> None:
        entries = _normalize_fields(fields)
        for entry in entries:
            self.type_into_control(entry.control_name, entry.value)

    def save(self) -> None:
        self.session.save_record()

    def click_submit(self) -> None:
        """Click the Submit button on the form like a human user."""
        import time

        self.session.window.set_focus()
        time.sleep(0.3)
        try:
            btn = self.session.window.child_window(title="Submit", control_type="Button")
            btn.wait("visible ready", timeout=5)
            btn.click_input()
            time.sleep(0.5)
        except Exception as exc:
            raise RuntimeError(
                f"Could not find or click the Submit button on the active form. "
                f"Diagnostic: {exc}"
            ) from exc

        # Verify the record was saved; force COM save if button handler didn't commit
        try:
            active_form = self.session.app.Screen.ActiveForm
            if active_form.Dirty:
                active_form.Dirty = False
                time.sleep(0.5)
        except Exception:
            pass

    def new_record(self) -> None:
        self.session.go_to_new_record()

    def read_focused_value(self) -> str:
        from pywinauto.keyboard import send_keys

        send_keys("^a^c")
        return ""


def _normalize_fields(fields: list[FieldEntry] | dict[str, Any]) -> list[FieldEntry]:
    if isinstance(fields, dict):
        return [FieldEntry(control_name=name, value=value) for name, value in fields.items()]
    return fields
