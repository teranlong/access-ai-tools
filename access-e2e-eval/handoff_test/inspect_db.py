"""TASK 0: Inspect the generated sample DB via COM/DAO.

Confirms the .accdb exists, lists user tables, the Contacts table fields,
and the ContactEditor form control names. Uses only COM/DAO (allowed).
"""
from __future__ import annotations

from pathlib import Path

import win32com.client

DB_PATH = (Path(__file__).resolve().parents[1] / "generated" / "access_e2e_sample.accdb")


def main() -> None:
    print(f"DB path: {DB_PATH}")
    print(f"DB exists: {DB_PATH.exists()}")
    if not DB_PATH.exists():
        raise SystemExit("Database not found; run scripts/build_sample_db.py first.")

    access = win32com.client.Dispatch("Access.Application")
    try:
        access.Visible = False
        access.OpenCurrentDatabase(str(DB_PATH))
        db = access.CurrentDb()

        # User tables (skip system tables that start with MSys)
        tables = [t.Name for t in db.TableDefs if not t.Name.startswith("MSys")]
        print(f"\nUser tables: {tables}")

        # Contacts fields
        contacts = db.TableDefs("Contacts")
        print("\nContacts fields (name : type_code : required):")
        for f in contacts.Fields:
            print(f"  {f.Name} : {f.Type} : required={f.Required}")

        # ContactEditor control names -- open the form to read controls
        access.DoCmd.OpenForm("ContactEditor")
        frm = access.Forms("ContactEditor")
        print("\nContactEditor controls (name : controltype):")
        for c in frm.Controls:
            try:
                print(f"  {c.Name} : {c.ControlType}")
            except Exception as exc:  # noqa: BLE001
                print(f"  <error reading control: {exc}>")
        access.DoCmd.Close(2, "ContactEditor", 2)  # acForm=2, acSaveNo=2
    finally:
        try:
            access.CloseCurrentDatabase()
        except Exception:  # noqa: BLE001
            pass
        access.Quit(2)  # acQuitSaveNone


if __name__ == "__main__":
    main()
