from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UiScenario:
    id: str
    name: str
    form_name: str
    purpose: str
    fields: dict[str, Any]
    validation_table: str
    validation_where: str


SCENARIOS: tuple[UiScenario, ...] = (
    UiScenario(
        id="S02",
        name="Add company",
        form_name="CompanyEditor",
        purpose="Human tester creates a new company through the Access company form.",
        fields={
            "CompanyName": "Northwind Research",
            "Industry": "Biotech",
            "Status": "Active",
            "Phone": "503-555-0144",
            "Email": "hello@northwind.example",
            "City": "Portland",
            "State": "OR",
        },
        validation_table="Companies",
        validation_where="CompanyName = 'Northwind Research'",
    ),
    UiScenario(
        id="S04",
        name="Add user",
        form_name="UserEditor",
        purpose="Human tester adds a new user and assigns the user to a company.",
        fields={
            "CompanyID": 1,
            "FirstName": "Riley",
            "LastName": "Chen",
            "Email": "riley.chen@contoso.example",
            "Role": "Security Reviewer",
            "Status": "Active",
            "IsPrimaryContact": False,
        },
        validation_table="Users",
        validation_where="Email = 'riley.chen@contoso.example'",
    ),
    UiScenario(
        id="S10",
        name="Add contact method",
        form_name="ContactEditor",
        purpose="Human tester adds a preferred contact method to a company.",
        fields={
            "CompanyID": 1,
            "ContactType": "Escalation Email",
            "ContactValue": "escalations@contoso.example",
            "IsPreferred": True,
        },
        validation_table="Contacts",
        validation_where="ContactValue = 'escalations@contoso.example'",
    ),
    UiScenario(
        id="S11",
        name="Create support case",
        form_name="CaseEditor",
        purpose="Human tester opens a company case from the Access UI.",
        fields={
            "CompanyID": 1,
            "Title": "Validate quarterly user access",
            "Priority": "High",
            "Status": "Open",
        },
        validation_table="Cases",
        validation_where="Title = 'Validate quarterly user access'",
    ),
)


EVALUATION_CATALOG = (
    ("S01", "Launch Access app", "Open generated .accdb and verify startup form appears."),
    ("S02", "Add company", "Fill CompanyEditor and save."),
    ("S03", "Edit company", "Change company status/phone/city."),
    ("S04", "Add user", "Fill UserEditor and save."),
    ("S05", "Edit user", "Change role/email/status."),
    ("S06", "Remove/deactivate user", "Deactivate user from UI while preserving history."),
    ("S07", "Reactivate user", "Reactivate inactive user."),
    ("S08", "Prevent duplicate email", "Attempt duplicate user email and verify validation."),
    ("S09", "Retrieve company records", "Filter/search company lookup form."),
    ("S10", "Add contact method", "Add preferred company contact."),
    ("S11", "Create support case", "Add case for company."),
    ("S12", "Close support case", "Mark case closed."),
    ("S13", "Required-field validation", "Attempt save with missing required fields."),
    ("S14", "Search/filter users", "Filter users by company/status."),
    ("S15", "Create simple form", "Generate/save a simple Access form helper."),
    ("S16", "Smoke-test created form", "Open generated form and read/edit bound data."),
    ("S17", "Audit trail check", "Verify operations write audit events."),
    ("S18", "Regression cleanup", "Close Access and ensure no lock file remains."),
)
