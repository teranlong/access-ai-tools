# Necessary Information for Producing a Functional Specification

All questions and information sources needed to produce a high-quality, developer-ready functional specification for a previously unseen project. Organized from broad to specific within each category.

Every piece of information that appears in a functional specification — version table, capabilities, screen sections, field tables, actions, designer notes, dev notes, callouts, reports, and master design — is traceable to a question in this document.

---

## Category 1: Project Identity & Document Control

This information populates the document header, version table, and title lines.

- Questions
  - What is the formal project name and application name as they should appear in the document title?
  - What platform is this application built on? (Microsoft Access/SQL desktop, Web Application, Mobile)
  - What is the client or organization name?
  - Who is the primary spec author? What initials or short name should appear in the "Edited By" column of the version table?
  - What is the starting version number for this document? (Standard: 1.0)
  - What is today's date for the initial version entry?
  - What is the module number and name for this document? (e.g., Module 1 – Administration)
  - Are there other module spec documents in this project that this document should cross-reference?
  - Are there any sections of this module that are explicitly out of scope for this version?

- Source
  - Customer / project sponsor
  - Statement of Work (SOW)
  - Project kickoff meeting notes

---

## Category 2: High-Level Understanding

This information populates the document title, the module-level Designer Note, and the General Application Features section.

- Questions
  - What is the purpose of this application? What business problem does it solve?
  - What industry or business domain is this application for?
  - What is the scope of this engagement? New build from scratch, migration of an existing system, or enhancement of an existing system?
  - What are the major functional areas (modules) of the application?
    - What is the name and number of each module?
    - What is the primary business entity or task for each module?
  - What are the most important things the application must do correctly? (Top 3–5 business priorities)
  - Are there any capabilities that are explicitly out of scope for this project?
  - What is the application's primary currency? Is more than one currency used?
  - What time zone does the application operate in? Is this configurable?
  - Is there a Master Design document that governs shared UI conventions across all modules?
    - If yes: has it been written? Who maintains it?
    - If no: who is responsible for defining global UI conventions?

- Source
  - Customer / project sponsor
  - SOW
  - Kickoff meeting notes
  - Existing product overview documentation

---

## Category 3: Current State & Legacy System

This information populates the module-level Designer Note and informs which capabilities carry forward, which are dropped, and which gaps the new system closes.

- Questions
  - Does a current system exist? What platform is it on?
    - Microsoft Access database, Excel spreadsheets, paper-based process, third-party software (which?), or no prior system?
  - Walk through the current system from the user's perspective. What does the user do, step by step, in each functional area?
  - What are the biggest frustrations or limitations of the current system?
  - What capabilities in the current system will be carried forward exactly?
  - What capabilities will be changed or redesigned?
  - What capabilities will be dropped entirely?
    - For each dropped capability: why is it being removed? Is there a replacement?
  - What new capabilities are being added that do not exist in the current system?
  - Are there any manual workarounds currently in use? (Things users do in Excel, email, or on paper because the system cannot handle them)
    - For each workaround: should the new system address it?
  - Are there any compliance or regulatory requirements currently met by the old system that must be preserved in the new system?
  - Are there any reports, outputs, or exports from the current system that stakeholders rely on and must be replicated?

- Follow-up questions
  - For any capability being dropped: is there a downstream business process that currently depends on it? How will that process be handled after go-live?
  - For any carried-forward capability: is the current behavior correct, or does the business want it improved?

- Source
  - Customer interview / requirements workshop
  - Current Access database file (.accdb)
  - Screen recording or walkthrough demo of current system
  - Existing user training documentation or user manuals
  - Excel workaround files

---

## Category 4: Users & Access Control

This information populates the Application User Access table, per-screen User Access declarations, and access guard conditions in the Actions section.

- Questions
  - Who are the user personas that use this application?
    - For each persona: what is their job title or function?
    - For each persona: what is their primary task in this application?
    - Approximately how many users are in each persona group?
  - How are users authenticated?
    - Windows Active Directory (login = Windows username)?
    - Username and password managed within the application?
    - Single Sign-On (SSO)? Which identity provider?
  - What is the permission model for this application?
    - Is it a simple two-level model (admin / non-admin)?
    - Is it a named capability model where individual capabilities are assigned to users? (e.g., Customers_MaintainFull, Customers_ReadOnly)
    - Who assigns capabilities to users? A system administrator within the app? IT?
  - What are the names of all capabilities defined for this module?
    - For each capability: what does it allow the user to see, create, edit, and delete?
    - For each capability: are there any actions or fields it does NOT grant access to?
    - Are any two capabilities mutually exclusive (a user cannot have both)?
  - Are there data-scoping rules?
    - Can some users see all records while others see only a subset? (e.g., only records assigned to their division, only their subscriber's records)
    - What is the scoping dimension? (by division, by location, by assigned user, by subscriber, by date range)
    - What capability grants access to all records regardless of scope?
  - Are there screens or features that are visible to all authenticated users regardless of capability?
  - Does the application have external users, such as API consumers, partner systems, or portal users?
    - If yes: how are they authenticated? What can they access?

- Follow-up questions
  - For each action on each screen (New, Edit, Delete): which capability is required to perform it?
  - For each screen: which capability grants read-only access?
  - If a user has no relevant capability for a module: is the module hidden from their menu entirely, or are they shown a read-only view?

- Source
  - Customer / IT department
  - Current system user list and role assignments
  - HR org chart (for understanding job functions)
  - Authentication system documentation (Active Directory, identity provider)

---

## Category 5: Module & Navigation Structure

This information populates screen headings, the navigation flow between screens, and the Master Design home page section.

- Questions
  - What is the application's main menu structure?
    - What menu items appear on the main menu?
    - For each menu item: what screen or module does it open?
    - Are any menu items visible only to users with a specific capability?
    - Are menu items organized into groups or sub-menus?
  - What is the home or landing page after login?
    - What does it display? (Main menu, dashboard, recent activity, branding image only)
    - Is any content on the home page personalized? (e.g., "Welcome, [User Name]", user-specific statistics)
  - For this module: what are all of the screens?
    - What is each screen's name?
    - What form type is each screen? (SLF, ELF, DF, R)
    - From which screen does the user navigate to each other screen?
    - Are there any screens reachable from multiple entry points?
  - Are there any modal dialogs, pop-up panels, or inline sub-forms?
    - If yes: when do they appear? What do they contain? Do they block the underlying page?
  - How does the user return to the main menu from any screen?
  - Is there a browser Back button behavior to specify? (Should Back work normally, or should navigation be handled by the application's own buttons only?)

- Source
  - Customer / business analyst
  - Figma screen flow document
  - Current system walkthrough demo
  - SOW scope list

---

## Category 6: Database & Data Model

This information populates Dev Notes (table and column mappings), field type specifications in element tables, and calculated field formulas.

- Questions
  - What are all of the tables in the current or planned database?
    - For each table: what is its purpose? What business entity or concept does it represent?
    - For each table: what naming prefix convention is used?
      - `tbl` — primary data tables?
      - `tlkp` — lookup / reference tables?
      - `txrf` — junction / cross-reference tables (many-to-many)?
      - `tsys` / `SysConfig` — system configuration tables?
  - What are the primary keys for each table?
    - What is the primary key field name and data type for each table? (auto-increment integer, GUID, natural key?)
  - What are all of the foreign key relationships between tables?
    - For each relationship: which field in which table references which primary key in which table?
    - For each relationship: one-to-many or many-to-many?
    - For each relationship: is the foreign key required (NOT NULL) or optional (nullable)?
  - For each table: what are all of the fields?
    - Field name, data type (VARCHAR, INT, DECIMAL, BIT, DATE, DATETIME), maximum length for text fields
    - Is the field nullable or NOT NULL?
    - Does the field have a default value?
    - Is it system-generated? (identity/auto-increment, auto-set on insert or update, calculated)
  - Which fields are calculated and not stored? What is the formula for each?
  - Which fields are audited?
    - Is there a LastUpdated timestamp field on each data table?
    - Is there a LastUpdatedBy user field?
  - Which tables are shared across multiple modules?
  - Are there any fields whose values depend on another field's value? (Conditional data rules)
  - Are there any effective-date fields?
    - For each: how is the correct historical value selected for a given date? (Most recent record before date, exact match, etc.)

- Follow-up questions
  - For any calculated field: what inputs does the formula use? What is the exact calculation? How should rounding be handled?
  - For any lookup table: is the full list of values known now, or will the client manage them going forward?
  - For any many-to-many relationship: what additional data is stored on the junction record beyond the two foreign keys?

- Source
  - Access DB schema file (.accdb, .bacpac)
  - Database schema export (SQL script, ERD diagram)
  - Developer interview
  - Existing query and report definitions in the Access DB

---

## Category 7: Screen Details — Searchable List Forms (SLF)

This information populates the SLF screen sections of the functional spec: search criteria table, elements table, actions, and grid actions.

- Questions
  - What entity does this list screen display?
  - What columns appear in the grid?
    - For each column: what is the label? What field does it display?
    - For each column: is it sortable by the user?
    - For each column: what is the display format? (m/d/yyyy for dates, $0.00 for currency, etc.)
    - For each column: is it read-only in the grid?
  - What search / filter criteria appear above the grid?
    - For each criterion: what is the label and field type? (Text, Dropdown, Date range, Checkbox)
    - For each criterion: what is the default value on page load?
    - For each dropdown criterion: what are the options? What is the selection source?
  - Does the grid auto-populate when the page loads, or does the user click Search first?
  - What is the default sort order on page load?
  - What page-level actions are available? (New, Export, Print, etc.)
    - For each action: what does it do?
    - For each action: is it restricted by capability?
  - What grid row actions are available? (Details icon, Edit icon, Delete icon, custom icons)
    - For each: what does it do?
    - For each: is it restricted by capability?
  - For the Delete action: what is the exact confirmation message text shown to the user?
  - Are any columns or actions conditionally visible? Under what condition?
  - Is pagination required? What is the default page size?

- Source
  - Customer / business analyst
  - Figma sketches
  - Current system demo or screenshots

---

## Category 8: Screen Details — Detail Forms (DF)

This information populates the DF screen sections: elements table, actions, designer notes, and dev notes.

- Questions
  - What entity does this form display and edit?
  - What fields appear on this form?
    - For each field: what is the label as displayed to the user?
    - For each field: what is the data type? (Text, Number, Currency, Date, Dropdown, Checkbox/Bit, Long text/RTF)
    - For each field: what is the maximum length? (for text fields)
    - For each field: is it required? (Cannot save without a value)
    - For each field: is it editable by the user, or read-only?
    - For each field: is it conditional? (Required or editable only when another field has a certain value)
    - For each field: what is a representative sample value?
    - For each field: what is the display format? (m/d/yyyy, $0.00 with comma, 00.00%, etc.)
    - For each field: what is the default value when creating a new record?
  - What dropdown / lookup fields exist?
    - For each dropdown: what table and column does it pull values from?
    - For each dropdown: how are inactive records handled? (Hidden from list, shown with a special indicator)
    - For each dropdown: is the list sorted? How?
  - What validation rules apply?
    - Uniqueness: are any fields required to be unique across all records of this type?
    - Range: are any numeric or date fields constrained to a minimum or maximum value?
    - Format: are any text fields constrained to a specific pattern? (Phone number, email, etc.)
    - Dependency: are any fields only valid when another field has a certain value?
    - For each validation rule: what is the exact error message shown to the user when it fails?
  - What calculated fields appear on the form?
    - For each: what is the formula? What input fields does it use?
    - For each: is the calculated value stored in the database or computed on the fly?
  - What conditional field behavior exists?
    - For each conditional field: what condition triggers the change in behavior?
    - What changes: the field becomes required, becomes visible, becomes editable, becomes read-only?
  - Is the form organized into sections or collapsible panels?
    - For each section: what is its name? Can it be collapsed?
    - For each section: what fields are in it?
  - Does this form display a timestamp for when the record was last updated? By whom?
  - Can records be deleted from this form? Under what conditions?
    - If there are referential integrity constraints (cannot delete if child records exist): what is the error message?

- Follow-up questions
  - For each conditional field: what is the exact database condition (which table, which field, which value)?
  - For any field whose default value is computed (not a static value): what is the computation?

- Source
  - Customer / business analyst
  - Figma sketches
  - Current system demo
  - Access DB table and field definitions

---

## Category 9: Screen Details — Editable Lookup Tables (ELF)

This information populates ELF screen sections for admin-managed reference data.

- Questions
  - What lookup or reference values does this table manage?
  - What fields does each row have?
    - For each field: label, type, required, sample value, format
  - Can rows be deleted?
    - If a lookup value is referenced by another record: is deletion blocked? What message is shown?
    - If rows are not deletable: is there an Active/Inactive flag instead?
  - Is there a limit to how many rows this table can have?
  - What is the default sort order for the grid?
  - Who can manage this table? (All admin-capable users, or only a specific capability?)
  - Does the application need to store the history of when values changed? (e.g., effective-date records vs. replacing the current value)

- Source
  - Customer / administrator
  - Current Access DB lookup tables

---

## Category 10: Screen Details — Reports (R)

This information populates the R screen sections: report filter criteria, report elements by section, and designer notes.

- Questions
  - What is the report's name and business purpose?
  - Who runs this report? Which user role? How often (daily, monthly, on demand)?
  - What filter criteria does the user control before running the report?
    - For each filter: label, field type, default value, and whether it is required
  - How is the report data grouped?
    - What is the primary grouping? Secondary grouping?
    - Is there a subtotal row after each group?
  - What is the sort order within each group?
  - What fields appear in the report detail rows?
    - For each field: label, format, alignment (left/right/center)
  - What calculated or summary values appear?
    - For each: label, formula, scope (group total, report total, page total)
  - What sections does the report have?
    - Report Header (appears once at the very top): what elements appear?
    - Group Header (appears at the start of each group): what elements appear?
    - Detail Row (one per record): what fields appear?
    - Group Footer (appears at the end of each group): what totals or summaries appear?
    - Report Footer (appears once at the very bottom): what totals or statements appear?
    - Page Footer (appears at the bottom of every page): what appears? (Page number format, date printed, legal statement)
  - Is there a legal or compliance statement in the footer? What is the exact text, or is it configurable?
  - What output formats are available? (Preview on screen, PDF export, print, Excel export)
  - Is the report title static, or does it include dynamic values from the filter selections?
  - Can this report be printed with a page break between groups?

- Source
  - Customer / report consumers
  - Samples of current reports (PDFs, screenshots, Access report definitions)
  - Legal or compliance team (for footer language)

---

## Category 11: Business Rules & Calculations

This information populates Designer Notes (business context) and Dev Notes (formulas), and drives the Callouts table for reusable logic.

- Questions
  - What are the key business rules that govern behavior across this module?
    - List every rule that the system must enforce automatically (not just display as a guideline).
  - For each rule: does it apply to all records, or only under certain conditions?
  - For each rule: is it role-dependent? (Does the rule behave differently for admin vs. non-admin users?)
  - For each calculated field anywhere in the application:
    - What is the exact formula?
    - What input fields or values does the formula use?
    - Are any inputs pulled from another table or module?
    - Is the value calculated at display time, at save time, or on demand?
    - How should rounding be handled? (Round half up, truncate, round to N decimal places)
  - Are there any time-sensitive rules?
    - Rules based on "the previous month's value," "last year's value," "the value as of [date]," or "the most recent record before [date]"?
    - For each: how is the correct historical value determined?
  - Are there fiscal year or accounting period rules?
    - Does the fiscal year differ from the calendar year?
    - Do records close or lock at period end?
  - Are there any calculations or rules that apply to more than one screen or entity?
    - These should be defined as Callouts (reusable logic blocks referenced by name).
  - Are there any regulatory, legal, or compliance constraints that translate directly into calculation or validation rules?
    - What is the rule? What is its source (regulation name, policy document)?

- Follow-up questions
  - For any formula that uses a rate, percentage, or multiplier: where does that value come from? Is it configurable? Can it change over time?
  - For any formula with conditional branches: what is the exact condition for each branch?

- Source
  - Customer / domain expert / subject matter expert
  - Current Access DB query and calculated field definitions
  - Business rules or policy documentation
  - Regulatory / compliance documentation

---

## Category 12: Workflow & Status Transitions

This information populates Designer Notes, conditional action behaviors, and any state transition documentation.

- Questions
  - Do any record types in this module have a status field?
    - What are all possible status values?
    - For each status value: what does it mean in business terms?
    - What is the initial status when a record is created?
    - What status transitions are allowed? (From each status, which statuses can it move to?)
    - What user action or system event triggers each transition?
    - Is a transition restricted by user capability? (Only a supervisor can approve, etc.)
    - Is a confirmation dialog required before a transition? What is the message text?
    - Does a transition trigger any other actions? (Email notification sent, related records updated, record becomes locked)
  - Are any records read-only after reaching a certain status?
    - Which fields, if any, remain editable even after the record is locked?
  - Are there approval workflows?
    - A record is submitted by one user type and must be reviewed or approved by another user type?
    - What happens if the reviewer rejects? Is there a rejection reason captured?
  - Are there any scheduled or automatic status changes?
    - A record's status changes automatically based on a date, elapsed time, or external trigger?
    - How frequently does this check run?

- Source
  - Customer / business analyst
  - Process documentation or flowcharts
  - Current system demo

---

## Category 13: Configuration & Admin-Managed Values

This information populates any Configuration module screen sections and informs lookup table ELF sections across all modules.

- Questions
  - What application-wide settings need to be configurable by an administrator?
    - For each setting: what is its label? What are the valid values? What is the default?
    - For each setting: how often does it change in practice?
    - For each setting: which user capability allows changing it?
  - What lookup / reference tables are managed through the application's UI?
    - For each lookup table: what values does it contain? (List the initial seed values if known)
    - For each lookup table: who manages it? (All admin users, only a super-admin)
    - For each lookup table: can values be deleted, or only deactivated?
  - Are there any time-series configuration values?
    - Values that are maintained over time with effective dates? (e.g., a percentage that changes annually, a rate maintained monthly)
    - For each: what fields does each record have? (Value, Effective Date, Last Updated)
    - For each: can there be overlapping effective date ranges, or must they be sequential?
  - Are there any per-user preferences that the user controls themselves? (Display settings, notification preferences, default filter values)
  - Are there any system-generated codes or IDs that need a configuration prefix or format? (e.g., Job numbers formatted as "J-2025-0001")

- Source
  - Customer / system administrator
  - Current Access DB system tables and configuration screens
  - Business policy documentation

---

## Category 14: Notifications & Email

This information populates action descriptions that trigger notifications and any email template ELF sections.

- Questions
  - What email notifications does the application send?
    - For each notification: what event triggers it?
    - For each notification: who are the recipients?
      - A specific named role?
      - The user who owns or created the triggering record?
      - A configurable list managed by an administrator?
      - All users with a specific capability?
    - Is the recipient list configurable by an administrator?
    - For each notification: what is the subject line?
    - For each notification: what is the email body content?
      - Static text portions: what do they say?
      - Dynamic values: which fields from the triggering record are included?
    - Is the email body stored as a configurable template (editable by admin) or hardcoded?
  - Does the application send in-app notifications, alerts, or badges?
    - For each: what triggers it? What does it say? What action clears it?
  - Does the application generate any scheduled or automated reports or digests sent by email?
    - For each: what does it contain? What is the schedule? Who receives it?

- Source
  - Customer
  - Current system email examples or templates
  - Email template configuration tables in the existing database

---

## Category 15: API & External Integrations

This information populates API spec sections (Arguments table, Output table) and any integration-related action descriptions.

- Questions
  - Does the application expose an API that external systems can call?
    - What is the purpose of the API?
    - What authentication method is used for API access? (API key, Bearer token, Windows auth)
    - What capability governs API access?
    - For each API call:
      - What is the call name?
      - What does it do?
      - For each argument: name, data type, required or optional, validation rule, sample value
      - For each output: name, data type, description, sample value
      - What is returned when the call succeeds?
      - What is returned when arguments are invalid or the operation fails?
  - Does the application consume any external APIs or data feeds?
    - For each: what data is retrieved? From which system? How frequently?
    - What happens if the external service is unavailable?
  - Does the application support file import?
    - What file format? (CSV, Excel, fixed-width text)
    - What is the expected column layout?
    - What validation is applied to imported rows?
    - What happens to rows that fail validation? (Skipped with a log entry, entire import rejected)
    - Is an error log displayed to the user after import?
  - Does the application support file export?
    - What format? (CSV, Excel, PDF)
    - Which fields are included in the export?
    - Does the export respect the current search filter, or does it always export all records?

- Source
  - Customer / IT department
  - API consumer documentation
  - Integration partner specifications
  - File format specifications or sample import files

---

## Category 16: UI / UX & Design (Master Design Content)

This information populates the Master Design document and is referenced by all module specs. If no Master Design document exists yet, these questions define its content.

- Questions — Branding & Layout
  - Is a Figma file available?
    - If yes: what is the Figma URL? Does it cover all modules or a subset?
    - If no: are there screen sketches, mockups, or screenshots of a reference application?
  - What is the application's primary color? Accent color? Background color?
  - Is there a logo? What format, size, and placement?
  - What is the application title as it appears in the browser tab and the page header?
    - Is this title configurable by an administrator, or is it hardcoded?
  - What is the navigation structure?
    - Persistent left sidebar, top navigation bar, or main-menu landing page?
    - Does the menu remain visible on all pages, or only on the home page?

- Questions — Grid Behavior
  - What icon is used for the Details (view record) grid action?
  - What icon is used for the Edit grid action?
  - What icon is used for Delete?
  - What icon is used for Add (adding a sub-record from within a grid row)?
  - Do grid rows alternate colors? What are the two row colors?
  - What is the standard grid row height?
  - How are sortable column headers visually indicated?
  - When the user scrolls down in a long grid, do column headers repeat or stick?
  - What pagination controls appear? (Page size selector, page number, First/Prev/Next/Last buttons)
  - What is the default page size?

- Questions — Date, Time & Input Conventions
  - Is there a calendar date picker popup on date fields? What triggers it?
  - What is the "reasonable date" validation range? (e.g., must be within 100 years of today)
  - What is the standard date display format? (m/d/yyyy)
  - What is the standard datetime display format? (m/d/yyyy h:mm AM/PM, or 24-hour?)
  - What is the standard email validation rule?
  - Are there any phone number format requirements?

- Questions — Search / Filter Behavior
  - Does the search grid auto-populate results on page load, or does the user click Search first?
  - When the user clicks Reset, what do the search criteria reset to? (Blanks, system defaults, last-used values)

- Questions — Detail Form Conventions
  - Can only one section of a detail form be in Edit mode at a time?
  - Do form sections have collapsible headers?
  - What is the section header color or style?
  - Does any detail form display a Clock Icon?
    - If yes: what does hovering over the Clock Icon show? (Created date/user, last modified date/user, or both)

- Questions — Inactive Records in Dropdowns
  - How are inactive or deactivated records displayed in dropdown lists?
    - Hidden from the list entirely?
    - Shown with a visual indicator, such as an asterisk (*) or strikethrough?
    - Shown in a different color or grouped at the bottom?

- Questions — Rich Text / HTML Features
  - Are any fields in the application rich text / formatted text (not plain text)?
    - If yes: what formatting is allowed? (Bold, italic, bullet lists, numbered lists, hyperlinks, font size, color)
    - What is the maximum character length for rich text fields?

- Questions — Mobile & Accessibility
  - Is the application used on mobile devices or tablets?
    - If yes: are there screen-size-specific layout requirements?
  - Are there accessibility requirements?
    - WCAG conformance target? (e.g., WCAG 2.1 Level AA)
    - Is keyboard navigation required for all interactive elements?
    - Minimum color contrast ratio?
    - Screen reader support required?

- Questions — Help System
  - Does the application have an in-application help system?
    - If yes: is help text editable by an administrator within the application?
    - If yes: is there a Help icon visible on every screen?
    - What does clicking the Help icon do? (Opens a drawer, opens a popup, navigates to a help page)

- Source
  - Customer / project sponsor
  - Figma file and design tokens
  - Branding guide or style guide
  - Existing Master Design document (if one exists for a prior project)
  - IT / accessibility compliance team

---

## Category 17: Supplementary — "Nice to Know Before Writing"

These questions are not always available at spec time but significantly improve spec quality when answered before the first draft.

- Questions
  - Are there any screens in the new application that correspond 1:1 to a screen in the current system? If yes: walk through both side by side so differences can be documented.
  - Are there any terms or field names that mean different things to different user groups in this organization? (Terminology conflicts to be aware of)
  - Are there any data quality issues in the current system's data that will affect the new system's design? (Duplicate records, inconsistent formats, missing required values)
  - Are there any known edge cases or exceptional records that the spec must handle explicitly?
  - Are there any features that the client has specifically said they do NOT want, even if they would seem natural? (Things to explicitly exclude)
  - Are there any planned future phases that the current spec should be designed to accommodate without implementing yet?
  - Are there any third-party or vendor constraints? (A reporting tool that requires specific output formats, a payment gateway with a fixed API contract, a government database with a required interchange format)

- Source
  - Customer
  - Prior project retrospectives
  - Data analyst reviewing the existing database

---

## Quick Reference: Question-to-Spec-Section Mapping

| Information Category | Where It Appears in the Spec |
| --- | --- |
| Project Identity | Document title lines, version table Edited By, document file name |
| High-Level Understanding | Module-level Designer Note, document title |
| Current State | Module-level Designer Note (business context) |
| Users & Access Control | Application User Access table, per-screen User Access declarations, action access guards |
| Module & Navigation | Screen heading list, Action "Done" / "Close" navigation targets, Master Design home page |
| Database & Data Model | Dev Notes column mappings (// mapped to...), field types in element tables, calculated field formulas |
| List Screen (SLF) | SLF screen section: Search Criteria table, Elements table, Actions, Grid Actions |
| Detail Form (DF) | DF screen section: Elements table, Actions, Designer Notes |
| Editable Lookup (ELF) | ELF screen section: Elements table, Actions |
| Reports (R) | R screen section: Report Filter Criteria, Report Elements by section |
| Business Rules & Calculations | Designer Notes (business context), Dev Notes (formulas), Callouts table |
| Workflow & Status | Conditional actions in Actions section, Designer Notes, state-specific behavior in element table |
| Configuration & Admin Values | Configuration module screen sections, lookup table ELF sections |
| Notifications & Email | Action descriptions (triggering events), email template ELF sections |
| API & Integrations | API spec screen sections: Arguments table, Output table |
| UI / UX & Design | Master Design document (all sections), Sketches section (Figma URL) |
