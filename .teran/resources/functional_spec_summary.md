# Functional Specification Summaries (v1.3.0)

## Heartland Bank - Stock Tracking Application
**Master Spec:** (Not specified as a standalone document; covered by Module FS docs)

- **Module 1: Configuration**
  - Application User Access management (Admin vs. Read-Only).
  - Share Values configuration and Shareholder legalese footer management.
  - Withhold Percentage settings.

- **Module 2: Shareholders and Transactions** (Includes Module 3)
  - Shareholder list management and search functionality.
  - Shareholder general information and detailed views.
  - Transaction entry logic (Transfers, New Issues).
  - Forced Vesting features for employee stock.
  - Restricted Stock Transfer validation logic.

- **Module 4: Dividends**
  - Creation and management of Dividend Events.
  - Calculation of dividends based on share balance snapshots.
  - Dividend Adjustments for late-breaking transactions.
  - Event locking mechanism to finalize payments.
  - Generation of Dividend Payment Reports and ACH prep.

- **Module 5: Stock Award Plans**
  - Management of employee stock grants (Restricted Stock).
  - Vesting Schedule definitions (e.g., 6-year schedules).
  - Automated calculation of Vested % and Vested shares.
  - Integration with dividend calculations.

- **Module 6: Reports**
  - Shareholders by Owner Group (share counts and percentages).
  - Transaction Report with date range and type filters.
  - Statement of Ownership (comprehensive shareholder equity view).
  - Dividend Payment Reports.
  - Tax-related reporting: Employee W2 (Non-Cash Earnings) and Shareholder 1099 data.

---

## Statewide - Fence Management System
**Master Spec:** Statewide Master Design

- **Module 1: Administration**
  - Role-based access control (Capabilities).
  - Administration menu for system lookups.
  - Configuration of Routes and Stops for scheduling.
  - Geographic lookups (City, State, Location).

- **Module 2: Customers and Items**
  - Customer profile management (Contacts, Credit holds/flags).
  - Item catalog management (Categories, Measurement units).
  - Inventory calculation logic based on Work Order status.
  - Item-level transaction history.

- **Module 3: Jobs and Rental Agreements**
  - Job lifecycle management (New, Closed, History).
  - Rental Agreement (RA) management (Re-rents, Items on Site).
  - Integration between Jobs and RAs for inventory tracking.
  - Job-level reporting and contact management.

- **Module 4: Work Orders and Calendar**
  - Work Order lifecycle (Scheduling, Line Items, Review/Finalization).
  - Interactive Calendar for dispatching (Office vs. Field views).
  - Mobile/Field support: Signatures, on-site photos, and field notes.
  - Automated PDF generation for field reports and customer receipts.

---

## KnightG - Exclusion (Sanctions) Web Application
**Master Spec:** KG Exclusion Master Design

- **Module 1: Administration**
  - Subscriber (Customer) management and license tracking.
  - User account management and role assignment.
  - Login security and self-service password reset.
  - Sanctions Programs and ISO Country lookups.

- **Module 2: Lists and Processing**
  - Automated list uploads (OFAC SDN, Consolidated lists).
  - Banned Party data cleaning and parsing (name normalization).
  - Internal List management (White Lists and Black Lists).
  - Import error handling and warning logs.

- **Module 3: Search**
  - Search interface for identifying banned parties.
  - Possible match identification and status tracking.
  - Batch clearing functionality for high-volume results.
  - Detailed Search Report generation.

- **Module 4: Jobs and Referrals**
  - Referral workflow (Assigning matches to investigators).
  - Investigation remarks and closure codes.
  - Automated Job parsing for batch searches.
  - Integration with White List to prevent repeat hits.

---

## Youngdahl - Field Application (Geotechnical)
**Master Spec:** Youngdahl Master Design

- **Module 1: Administration**
  - Project Specifications management (Project-specific vs. Standard).
  - AHJ (Authority Having Jurisdiction) and Contract Type configuration.
  - Settings for ODBC data links to legacy GEMS system.
  - Global user access model (additive roles).

- **Module 2: Dispatch, Visits and Tasks**
  - Field visit scheduling and dispatching.
  - Task management for field technicians (Daily Field Reports - DFRs).
  - Attachment and photo management for site visits.
  - DFR status tracking (Draft, In Review, Approved, Distributed).

- **Module 3: Soils**
  - Technical field tests: ASTM Soils and AC (Asphalt Concrete).
  - Curve and Location selection for compaction testing.
  - Automated calculation of Relative Compaction based on project rules.
  - Complex DFR Report generation combining multiple test types.
  - Data export to Excel for technical analysis.

- **Module 4: Labs**
  - Lab-based curve management (Material types, Rock corrections).
  - Integration between lab data and field test requirements.
  - Revision control for technical specifications.

- **Module 6: Dashboard and Notifications**
  - Personalized Dashboard for field techs (Visits & Tasks, Agenda).
  - Supervisor Dashboard for monitoring staff activity.
  - Automated notifications and status alerts.
