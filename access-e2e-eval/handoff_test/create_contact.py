"""TASK A: Create a NEW Contacts record purely through the ContactEditor UI.

Methodology (handoff only): COM stages -> PostMessage(WM_CHAR) types ->
focus-out commit -> layered COM save -> COM/DAO verifies the row exists.

The Contacts table schema is (CompanyID, ContactType, ContactValue, IsPreferred);
there is no FirstName/LastName/Email field, so the "Ada Lovelace / ada@example.com"
intent is mapped onto the real fields:
    CompanyID   = 1
    ContactType = 'Email'
    ContactValue= 'ada.lovelace@example.com'
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import win32com.client

import handoff_lib as hl

DB_PATH = str(Path(__file__).resolve().parents[1] / "generated" / "access_e2e_sample.accdb")
STATE_FILE = Path(__file__).resolve().parent / "created_contact.json"

TARGET = {
    "CompanyID": "1",
    "ContactType": "Email",
    "ContactValue": "ada.lovelace@example.com",
}


def _cleanup_prior(value: str) -> None:
    """Delete any pre-existing rows with the target ContactValue (DAO), for a clean slate."""
    engine = win32com.client.Dispatch("DAO.DBEngine.120")
    db = engine.OpenDatabase(DB_PATH)
    try:
        safe = value.replace("'", "''")
        db.Execute(f"DELETE FROM Contacts WHERE ContactValue = '{safe}'", 128)  # dbFailOnError
    finally:
        db.Close()


def main() -> int:
    print("=== TASK A: create contact via UI (PostMessage) ===")
    _cleanup_prior(TARGET["ContactValue"])

    access = hl.open_access(DB_PATH, visible=True)
    watchdog = hl.DialogWatchdog()
    try:
        with watchdog:
            access.DoCmd.OpenForm("ContactEditor")
            time.sleep(0.5)
            # Navigate to a fresh new record.
            access.DoCmd.GoToRecord(hl.AC_FORM, "ContactEditor", hl.AC_NEW_REC)
            time.sleep(0.3)

            # Type each field, then move focus to the NEXT field to commit the prior one.
            hl.type_into_field(access, "CompanyID", TARGET["CompanyID"])
            hl.commit_focus_out(access, "ContactType")

            hl.type_into_field(access, "ContactType", TARGET["ContactType"])
            hl.commit_focus_out(access, "ContactValue")

            hl.type_into_field(access, "ContactValue", TARGET["ContactValue"])
            # Focus-out the last field by moving back to the first control.
            hl.commit_focus_out(access, "CompanyID")

            # Read back live control values (before save) as a sanity check.
            seen = {
                "CompanyID": hl.read_focused_value(access, "CompanyID"),
                "ContactType": hl.read_focused_value(access, "ContactType"),
                "ContactValue": hl.read_focused_value(access, "ContactValue"),
            }
            print(f"Live control values after typing: {seen}")

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

    # --- COM/DAO verification ---
    rows = hl.query_contacts(DB_PATH, TARGET["ContactValue"])
    print(f"DB rows matching ContactValue={TARGET['ContactValue']!r}: {rows}")

    ok = (
        len(rows) == 1
        and rows[0]["CompanyID"] == int(TARGET["CompanyID"])
        and rows[0]["ContactType"] == TARGET["ContactType"]
        and rows[0]["ContactValue"] == TARGET["ContactValue"]
    )

    if ok:
        STATE_FILE.write_text(json.dumps({"contact_id": rows[0]["ContactID"], **TARGET}))
        print(f"PASS: contact created via UI and verified in DB (ContactID={rows[0]['ContactID']}).")
        return 0

    print("FAIL: contact row not found or values did not match.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
