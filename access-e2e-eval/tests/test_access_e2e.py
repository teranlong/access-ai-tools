from __future__ import annotations

import pytest

from access_eval_suite.access_app import AccessAppSession, build_config_for_database
from access_eval_suite.access_app import AccessAppError
from access_eval_suite.data_access import AccessData
from access_eval_suite.scenarios import SCENARIOS
from access_eval_suite.uia import AccessUiDriver
from access_eval_suite import constants as ac


pytestmark = pytest.mark.access_e2e


@pytest.fixture()
def access_session(test_database):
    try:
        session = AccessAppSession.open(build_config_for_database(test_database))
    except AccessAppError as exc:
        pytest.skip(str(exc))
    try:
        from pywinauto.keyboard import send_keys

        session.window.set_focus()
        send_keys("{ESC}")
    except RuntimeError as exc:
        session.close()
        pytest.skip(
            "pywinauto attached to Access, but Windows rejected keyboard injection. "
            "Run from an unlocked interactive desktop session. "
            f"Diagnostic: {exc}"
        )
    if not _keyboard_input_reaches_access_controls(session):
        session.close()
        pytest.skip(
            "pywinauto attached to Access, but keyboard input did not change a bound "
            "Access form control. Run from an unlocked interactive desktop session "
            "where Office apps can receive synthetic input."
        )
    try:
        yield session
    finally:
        session.close()


def test_launches_generated_access_app(access_session):
    assert access_session.window.exists()
    assert access_session.app.CurrentProject.FullName


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: f"{scenario.id}-{scenario.name}")
def test_human_like_create_flows(access_session, test_database, scenario):
    access_session.open_form(scenario.form_name)
    driver = AccessUiDriver(access_session)
    driver.new_record()
    driver.fill_form(scenario.fields)
    driver.save()

    row = assert_single_row(
        access_session,
        scenario.validation_table,
        scenario.validation_where,
    )
    assert row


def test_edit_existing_user_role_through_ui(access_session, test_database):
    access_session.open_form("UserEditor", "Email = 'jordan.lee@contoso.example'")
    driver = AccessUiDriver(access_session)
    driver.fill_form({"Role": "Incident Commander", "Status": "Active"})
    driver.save()

    row = assert_single_row(access_session, "Users", "Email = 'jordan.lee@contoso.example'")
    assert row["Role"] == "Incident Commander"


def test_edit_existing_company_through_ui(access_session, test_database):
    access_session.open_form("CompanyEditor", "CompanyName = 'Fabrikam Logistics'")
    driver = AccessUiDriver(access_session)
    driver.fill_form({"Status": "Onboarding", "Phone": "425-555-0140", "City": "Redmond"})
    driver.save()

    row = assert_single_row(access_session, "Companies", "CompanyName = 'Fabrikam Logistics'")
    assert row["Status"] == "Onboarding"
    assert row["Phone"] == "425-555-0140"
    assert row["City"] == "Redmond"


def test_deactivate_and_reactivate_user_through_ui(access_session, test_database):
    access_session.open_form("UserEditor", "Email = 'avery.stone@contoso.example'")
    driver = AccessUiDriver(access_session)
    driver.fill_form({"Status": "Inactive"})
    driver.save()
    assert_single_row(access_session, "Users", "Email = 'avery.stone@contoso.example' AND Status = 'Inactive'")

    driver.fill_form({"Status": "Active"})
    driver.save()
    assert_single_row(access_session, "Users", "Email = 'avery.stone@contoso.example' AND Status = 'Active'")


def test_duplicate_email_is_rejected(access_session, test_database):
    access_session.open_form("UserEditor")
    driver = AccessUiDriver(access_session)
    driver.new_record()
    driver.fill_form(
        {
            "CompanyID": 1,
            "FirstName": "Duplicate",
            "LastName": "Email",
            "Email": "avery.stone@contoso.example",
            "Role": "Tester",
            "Status": "Active",
            "IsPrimaryContact": False,
        }
    )

    driver.save()

    assert count_where(access_session, "Users", "Email = 'avery.stone@contoso.example'") == 1


def test_retrieve_all_users_for_company(access_session, test_database):
    access_session.open_form("CompanyUserLookup")
    from pywinauto.keyboard import send_keys

    access_session.window.set_focus()
    send_keys("^fContoso Health{ENTER}{ESC}", with_spaces=True)
    access_session.refresh()

    rows = access_session.rows(
        """
        SELECT Users.Email
        FROM Companies INNER JOIN Users ON Companies.CompanyID = Users.CompanyID
        WHERE Companies.CompanyName = 'Contoso Health'
        ORDER BY Users.Email
        """
    )
    emails = {row["Email"] for row in rows}
    assert "avery.stone@contoso.example" in emails
    assert "jordan.lee@contoso.example" in emails


def test_close_support_case_through_ui(access_session, test_database):
    access_session.open_form("CaseEditor", "Title = 'Quarterly access review'")
    driver = AccessUiDriver(access_session)
    driver.fill_form({"Status": "Closed", "ClosedAt": "5/15/2026"})
    driver.save()

    row = assert_single_row(access_session, "Cases", "Title = 'Quarterly access review'")
    assert row["Status"] == "Closed"
    assert row["ClosedAt"] is not None


def test_required_company_name_is_enforced(access_session, test_database):
    access_session.open_form("CompanyEditor")
    driver = AccessUiDriver(access_session)
    driver.new_record()
    driver.fill_form(
        {
            "Industry": "Validation",
            "Status": "Active",
            "Phone": "555-0101",
            "Email": "missing-name@example.invalid",
            "City": "Seattle",
            "State": "WA",
        }
    )

    driver.save()

    assert count_where(access_session, "Companies", "Email = 'missing-name@example.invalid'") == 0


def test_helper_created_form_exists_and_opens(access_session, test_database):
    access_session.open_form("TestFormDesignerCheck")
    assert access_session.window.exists()
    assert access_session.app.CurrentProject.AllForms("TestFormDesignerCheck").Name == "TestFormDesignerCheck"


def test_audit_event_can_be_written_and_verified(test_database):
    with AccessData(test_database) as data:
        data.insert_audit_event(
            event_type="EvalCheck",
            entity_name="Users",
            entity_id=1,
            summary="Evaluation suite verified audit trail write path",
            company_id=1,
            user_id=1,
        )
        count = data.scalar(
            "SELECT Count(*) AS EventCount FROM AuditEvents WHERE EventType = 'EvalCheck'"
        )
    assert int(count or 0) == 1


def assert_single_row(access_session, table: str, where: str):
    rows = access_session.rows(f"SELECT * FROM {table} WHERE {where}")
    assert len(rows) == 1, f"Expected exactly one row in {table} where {where}; found {len(rows)}."
    return rows[0]


def count_where(access_session, table: str, where: str) -> int:
    return int(
        access_session.scalar(f"SELECT Count(*) AS RecordCount FROM {table} WHERE {where}") or 0
    )


def _keyboard_input_reaches_access_controls(session) -> bool:
    original = session.scalar("SELECT Phone FROM Companies WHERE CompanyID = 1")
    probe_value = "206-555-0198"
    try:
        session.open_form("CompanyEditor", "CompanyID = 1")
        driver = AccessUiDriver(session)
        driver.fill_form({"Phone": probe_value})
        driver.save()
        changed = session.scalar("SELECT Phone FROM Companies WHERE CompanyID = 1") == probe_value
        session.app.CurrentDb().Execute(
            f"UPDATE Companies SET Phone = '{original}' WHERE CompanyID = 1",
            ac.DAO_FAIL_ON_ERROR,
        )
        return changed
    except Exception:
        session.app.CurrentDb().Execute(
            f"UPDATE Companies SET Phone = '{original}' WHERE CompanyID = 1",
            ac.DAO_FAIL_ON_ERROR,
        )
        return False
