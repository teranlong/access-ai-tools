"""TASK B: Edit the record created by TASK A, through the ContactEditor UI.

Opens the specific record (by ContactID from created_contact.json), changes
ContactValue via the same PostMessage(WM_CHAR) technique, commits with a
focus-out, saves with the layered ladder, and verifies the change via COM/DAO.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import win32com.client

import handoff_lib as hl

DB_PATH = str(Path(__file__).resolve().parents[1] / "generated" / "access_e2e_sample.accdb")
STATE_FILE = Path(__file__).resolve().parent / "created_contact.json"

NEW_VALUE = "ada.byron@example.com"


def _row_by_id(contact_id: int):
    engine = win32com.client.Dispatch("DAO.DBEngine.120")
    db = engine.OpenDatabase(DB_PATH)
    try:
        rs = db.OpenRecordset(
            "SELECT ContactID, CompanyID, ContactType, ContactValue "
            f"FROM Contacts WHERE ContactID = {int(contact_id)}"
        )
        if rs.EOF:
            return None
        row = {
            "ContactID": int(rs.Fields("ContactID").Value),
            "CompanyID": int(rs.Fields("CompanyID").Value),
            "ContactType": str(rs.Fields("ContactType").Value),
            "ContactValue": str(rs.Fields("ContactValue").Value),
        }
        rs.Close()
        return row
    finally:
        db.Close()


def main() -> int:
    print("=== TASK B: edit contact via UI (PostMessage) ===")
    if not STATE_FILE.exists():
        print("FAIL: created_contact.json missing -- run create_contact.py first.")
        return 1
    state = json.loads(STATE_FILE.read_text())
    contact_id = int(state["contact_id"])
    before = _row_by_id(contact_id)
    print(f"Before edit: {before}")
    if before is None:
        print(f"FAIL: record ContactID={contact_id} not found.")
        return 1

    access = hl.open_access(DB_PATH, visible=True)
    watchdog = hl.DialogWatchdog()
    try:
        with watchdog:
            # Open ONLY the target record via a WhereCondition filter.
            access.DoCmd.OpenForm(
                "ContactEditor", 0, "", f"ContactID={contact_id}", 1, 0
            )  # View=acNormal(0), DataMode=acFormEdit(1), WindowMode=acWindowNormal(0)
            time.sleep(0.5)

            hl.type_into_field(access, "ContactValue", NEW_VALUE)
            hl.commit_focus_out(access, "ContactType")  # focus-out commits ContactValue

            save_trace = hl.layered_save(access, "ContactEditor")
            print(f"Save ladder: {save_trace}")
            time.sleep(0.4)

            try:
                access.DoCmd.Close(hl.AC_FORM, "ContactEditor", hl.AC_SAVE_NO)
            except Exception:  # noqa: BLE001
                pass
    finally:
        hl.close_access(access)
    if watchdog.dismissed:
        print(f"Watchdog dismissed stray dialogs: {watchdog.dismissed}")

    after = _row_by_id(contact_id)
    print(f"After edit:  {after}")

    ok = after is not None and after["ContactValue"] == NEW_VALUE
    if ok:
        state["ContactValue"] = NEW_VALUE
        STATE_FILE.write_text(json.dumps(state))
        print(f"PASS: ContactID={contact_id} ContactValue changed to {NEW_VALUE!r} and verified.")
        return 0
    print("FAIL: ContactValue was not updated in the DB.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
