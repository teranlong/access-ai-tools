from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import time

from . import constants as ac


@dataclass(frozen=True)
class BuiltDatabase:
    path: Path
    forms: tuple[str, ...]
    tables: tuple[str, ...]


class AccessBuildError(RuntimeError):
    pass


TABLES = ("Companies", "Users", "Contacts", "Cases", "AuditEvents")
FORMS = (
    "CompanyEditor",
    "UserEditor",
    "ContactEditor",
    "CaseEditor",
    "CompanyUserLookup",
    "CompanyList",
    "UserList",
    "TestFormDesignerCheck",
)


def create_sample_database(database_path: Path, overwrite: bool = True) -> BuiltDatabase:
    database_path = database_path.resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        if not overwrite:
            raise AccessBuildError(f"Database already exists: {database_path}")
        database_path.unlink()

    access = _new_access_application()
    try:
        _set_visible_if_supported(access, False)
        access.NewCurrentDatabase(str(database_path))
        db = access.CurrentDb()
        _create_schema(db)
        _seed_data(db)
        _create_forms(access)
        access.CloseCurrentDatabase()
    finally:
        access.Quit(ac.AC_QUIT_SAVE_NONE)
        time.sleep(0.5)

    return BuiltDatabase(path=database_path, forms=FORMS, tables=TABLES)


def copy_database_template(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    shutil.copy2(source, destination)
    return destination


def _new_access_application():
    try:
        import win32com.client
    except ImportError as exc:
        raise AccessBuildError("pywin32 is required to create an Access database.") from exc

    try:
        return win32com.client.Dispatch("Access.Application")
    except Exception as exc:  # noqa: BLE001 - preserve COM diagnostic for caller.
        raise AccessBuildError(
            "Could not start Microsoft Access through COM. "
            "Verify Access is installed and registered for this Windows user."
        ) from exc


def _set_visible_if_supported(access, visible: bool) -> None:
    try:
        access.Visible = visible
    except Exception:
        return


def _create_schema(db) -> None:
    statements = [
        """
        CREATE TABLE Companies (
            CompanyID AUTOINCREMENT CONSTRAINT pk_Companies PRIMARY KEY,
            CompanyName TEXT(100) NOT NULL,
            Industry TEXT(80),
            Status TEXT(20) NOT NULL,
            Phone TEXT(30),
            Email TEXT(120),
            City TEXT(80),
            State TEXT(30),
            CreatedAt DATETIME
        )
        """,
        """
        CREATE TABLE Users (
            UserID AUTOINCREMENT CONSTRAINT pk_Users PRIMARY KEY,
            CompanyID LONG NOT NULL,
            FirstName TEXT(60) NOT NULL,
            LastName TEXT(60) NOT NULL,
            Email TEXT(120) NOT NULL,
            Role TEXT(60),
            Status TEXT(20) NOT NULL,
            IsPrimaryContact YESNO,
            CreatedAt DATETIME,
            UpdatedAt DATETIME
        )
        """,
        """
        CREATE TABLE Contacts (
            ContactID AUTOINCREMENT CONSTRAINT pk_Contacts PRIMARY KEY,
            CompanyID LONG NOT NULL,
            ContactType TEXT(40) NOT NULL,
            ContactValue TEXT(120) NOT NULL,
            IsPreferred YESNO
        )
        """,
        """
        CREATE TABLE Cases (
            CaseID AUTOINCREMENT CONSTRAINT pk_Cases PRIMARY KEY,
            CompanyID LONG NOT NULL,
            Title TEXT(120) NOT NULL,
            Priority TEXT(20) NOT NULL,
            Status TEXT(20) NOT NULL,
            OpenedAt DATETIME,
            ClosedAt DATETIME
        )
        """,
        """
        CREATE TABLE AuditEvents (
            AuditEventID AUTOINCREMENT CONSTRAINT pk_AuditEvents PRIMARY KEY,
            UserID LONG,
            CompanyID LONG,
            EventType TEXT(40) NOT NULL,
            EntityName TEXT(80) NOT NULL,
            EntityID LONG,
            EventSummary TEXT(255),
            EventAt DATETIME
        )
        """,
        "CREATE UNIQUE INDEX ux_Users_Email ON Users (Email)",
        "CREATE INDEX ix_Users_CompanyID ON Users (CompanyID)",
        "CREATE INDEX ix_Contacts_CompanyID ON Contacts (CompanyID)",
        "CREATE INDEX ix_Cases_CompanyID ON Cases (CompanyID)",
    ]
    for statement in statements:
        db.Execute(statement, ac.DAO_FAIL_ON_ERROR)


def _seed_data(db) -> None:
    statements = [
        """
        INSERT INTO Companies
            (CompanyName, Industry, Status, Phone, Email, City, State, CreatedAt)
        VALUES
            ('Contoso Health', 'Healthcare', 'Active', '206-555-0100',
             'admin@contoso.example', 'Seattle', 'WA', Now())
        """,
        """
        INSERT INTO Companies
            (CompanyName, Industry, Status, Phone, Email, City, State, CreatedAt)
        VALUES
            ('Fabrikam Logistics', 'Transportation', 'Active', '425-555-0125',
             'ops@fabrikam.example', 'Bellevue', 'WA', Now())
        """,
        """
        INSERT INTO Users
            (CompanyID, FirstName, LastName, Email, Role, Status, IsPrimaryContact, CreatedAt, UpdatedAt)
        VALUES
            (1, 'Avery', 'Stone', 'avery.stone@contoso.example',
             'Account Manager', 'Active', True, Now(), Now())
        """,
        """
        INSERT INTO Users
            (CompanyID, FirstName, LastName, Email, Role, Status, IsPrimaryContact, CreatedAt, UpdatedAt)
        VALUES
            (1, 'Jordan', 'Lee', 'jordan.lee@contoso.example',
             'Support Lead', 'Active', False, Now(), Now())
        """,
        """
        INSERT INTO Users
            (CompanyID, FirstName, LastName, Email, Role, Status, IsPrimaryContact, CreatedAt, UpdatedAt)
        VALUES
            (2, 'Morgan', 'Patel', 'morgan.patel@fabrikam.example',
             'Operations Contact', 'Active', True, Now(), Now())
        """,
        """
        INSERT INTO Contacts
            (CompanyID, ContactType, ContactValue, IsPreferred)
        VALUES
            (1, 'Email', 'care-team@contoso.example', True)
        """,
        """
        INSERT INTO Contacts
            (CompanyID, ContactType, ContactValue, IsPreferred)
        VALUES
            (2, 'Phone', '425-555-0199', True)
        """,
        """
        INSERT INTO Cases
            (CompanyID, Title, Priority, Status, OpenedAt, ClosedAt)
        VALUES
            (1, 'Quarterly access review', 'Medium', 'Open', Now(), Null)
        """,
        """
        INSERT INTO AuditEvents
            (UserID, CompanyID, EventType, EntityName, EntityID, EventSummary, EventAt)
        VALUES
            (Null, 1, 'Seed', 'Companies', 1, 'Seeded Contoso Health', Now())
        """,
    ]
    for statement in statements:
        db.Execute(statement, ac.DAO_FAIL_ON_ERROR)


def _create_forms(access) -> None:
    _create_editor_form(
        access,
        form_name="CompanyEditor",
        record_source="Companies",
        controls=[
            ("CompanyName", "Company Name"),
            ("Industry", "Industry"),
            ("Status", "Status"),
            ("Phone", "Phone"),
            ("Email", "Email"),
            ("City", "City"),
            ("State", "State"),
        ],
    )
    _create_editor_form(
        access,
        form_name="UserEditor",
        record_source="Users",
        controls=[
            ("CompanyID", "Company ID"),
            ("FirstName", "First Name"),
            ("LastName", "Last Name"),
            ("Email", "Email"),
            ("Role", "Role"),
            ("Status", "Status"),
            ("IsPrimaryContact", "Primary Contact"),
        ],
    )
    _create_editor_form(
        access,
        form_name="ContactEditor",
        record_source="Contacts",
        controls=[
            ("CompanyID", "Company ID"),
            ("ContactType", "Contact Type"),
            ("ContactValue", "Contact Value"),
            ("IsPreferred", "Preferred"),
        ],
    )
    _create_editor_form(
        access,
        form_name="CaseEditor",
        record_source="Cases",
        controls=[
            ("CompanyID", "Company ID"),
            ("Title", "Title"),
            ("Priority", "Priority"),
            ("Status", "Status"),
            ("ClosedAt", "Closed At"),
        ],
    )
    _create_readonly_list_form(
        access,
        "CompanyList",
        "SELECT CompanyID, CompanyName, Industry, Status, City, State FROM Companies ORDER BY CompanyName",
    )
    _create_readonly_list_form(
        access,
        "UserList",
        "SELECT UserID, CompanyID, FirstName, LastName, Email, Role, Status FROM Users ORDER BY LastName, FirstName",
    )
    _create_readonly_list_form(
        access,
        "CompanyUserLookup",
        """
        SELECT Companies.CompanyName, Users.FirstName, Users.LastName, Users.Email,
               Users.Role, Users.Status
        FROM Companies INNER JOIN Users ON Companies.CompanyID = Users.CompanyID
        ORDER BY Companies.CompanyName, Users.LastName, Users.FirstName
        """,
    )
    _create_editor_form(
        access,
        form_name="TestFormDesignerCheck",
        record_source="Companies",
        controls=[
            ("CompanyName", "Company Name"),
            ("Status", "Status"),
        ],
    )


def _create_editor_form(access, form_name: str, record_source: str, controls: list[tuple[str, str]]) -> None:
    form = access.CreateForm()
    generated_name = form.Name
    form.RecordSource = record_source
    form.Caption = form_name
    form.DefaultView = 0
    form.AllowAdditions = True
    form.AllowEdits = True
    form.AllowDeletions = False
    form.NavigationButtons = True

    top = 500
    for field_name, caption in controls:
        access.CreateControl(form.Name, ac.CONTROL_LABEL, ac.SECTION_DETAIL, "", "", 450, top, 1700, 300).Caption = caption
        control_type = ac.CONTROL_CHECK_BOX if field_name.startswith("Is") else ac.CONTROL_TEXT_BOX
        control = access.CreateControl(
            form.Name,
            control_type,
            ac.SECTION_DETAIL,
            "",
            field_name,
            2300,
            top,
            3000,
            300,
        )
        control.Name = field_name
        top += 450

    # Add Submit button below the last field
    btn_top = top + 200
    btn = access.CreateControl(
        form.Name,
        ac.CONTROL_COMMAND_BUTTON,
        ac.SECTION_DETAIL,
        "",
        "",
        2300,
        btn_top,
        2000,
        400,
    )
    btn.Name = "btnSubmit"
    btn.Caption = "Submit"

    # Wire the button's OnClick event.
    # Try VBA first (most reliable), fall back to expression if VBA project is locked.
    vba_injected = False
    try:
        btn.OnClick = "[Event Procedure]"
        access.DoCmd.Save(ac.AC_FORM, generated_name)
        module = form.Module
        module.InsertText(
            "Private Sub btnSubmit_Click()\r\n"
            "    If Me.Dirty Then Me.Dirty = False\r\n"
            "End Sub\r\n"
        )
        vba_injected = True
    except Exception:
        pass

    if not vba_injected:
        # Fallback: use a macro expression (no VBA trust required)
        btn.OnClick = "=DoCmd.RunCommand(21)"

    access.DoCmd.Save(ac.AC_FORM, generated_name)
    access.DoCmd.Close(ac.AC_FORM, generated_name, ac.AC_SAVE_YES)
    access.DoCmd.Rename(form_name, ac.AC_FORM, generated_name)


def _create_readonly_list_form(access, form_name: str, record_source: str) -> None:
    form = access.CreateForm()
    generated_name = form.Name
    form.RecordSource = record_source
    form.Caption = form_name
    form.DefaultView = 2
    form.AllowAdditions = False
    form.AllowEdits = False
    form.AllowDeletions = False
    form.NavigationButtons = True
    access.DoCmd.Save(ac.AC_FORM, generated_name)
    access.DoCmd.Close(ac.AC_FORM, generated_name, ac.AC_SAVE_YES)
    access.DoCmd.Rename(form_name, ac.AC_FORM, generated_name)
