# Project Modularization: Coleville LogYard 2.0 Rebuild

Applying the Project Modularization Guidelines to the **Coleville Forest Products LogYard 2.0 System**.

## Project Name: Coleville LogYard 2.0
**Master Spec:** Statement of Work: Colville Forrest Products LLC LogYard System 2.0

---

## Proposed Module Structure

### Module 1: Administration & Configuration (**The Foundation**)
Aligns with the **"Foundation Rule"**. Handles all the static lookups and system-wide settings required for timber valuation and security.
*   **Capabilities:**
    *   **User Management:** Roles, capabilities, and active/inactive status.
    *   **Timber Lookups:** Species, species categories, logging methods, and valuation types.
    *   **Rate Lookups:** Ownership types, sort yard rates, and global variables.
    *   **Security:** Login, password reset, and access control.

### Module 2: Entities - Companies & People (**The "What we track"**)
Aligns with the **"Entity Ownership Rule"**. Manages the parties involved in the log yard lifecycle.
*   **Capabilities:**
    *   **Companies:** Logging companies (and their methods) and Milling companies (and their yards).
    *   **Personnel:** Truckers and scalers (importing and manual enrichment).
    *   **Contacts:** Management of primary contacts for all companies.

### Module 3: Load Entry & Valuation (**The Core Transaction**)
Aligns with the **"Lifecycle/Workflow Rule"**. This is the high-intensity area where data enters the system and is validated.
*   **Capabilities:**
    *   **Load Staging (Quarantine):** Importing BIA files, validity checking, and error feedback.
    *   **Load Management:** Valuation of weighted, scaled, and sampled loads.
    *   **Ticket Adjustment:** Adjusting rates on tickets before or after payment.
    *   **Detail Reports:** Generating/Printing detailed load tickets.

### Module 4: Logging Units & Contracts (**Technical Workflows**)
Aligns with the **"Entity Ownership Rule"** (Technical domain). Handles the physical and legal structure of the timber sales.
*   **Capabilities:**
    *   **Logging Units:** Managing sales, sections, and blocks.
    *   **Road Costs:** Tracking road charges and build-out costs for profitability analysis.
    *   **Hauling/Road Rates:** Unit-to-yard rate management.
    *   **Stumpage:** Stumpage contracts, cost calculation, and summary reporting.

### Module 5: Logging Payments & Hold Accounts (**Financial Lifecycle**)
Aligns with the **"Lifecycle/Workflow Rule"**. Manages the complex payout cycle and financial "holdbacks."
*   **Capabilities:**
    *   **Payment Cycles:** Creating payment sets for current periods + adjustment payments for retroactive rate changes.
    *   **Holdback Management:** Accrued holdbacks, penalties, transfers between loggers, and account summaries.
    *   **Logger Payouts:** Printing/PDF generation of payment summaries and species-specific details.

### Module 6: Mills & Revenue Reconciliation (**Output & Reconciliation**)
Aligns with the **"Lifecycle Rule"** and **"Output Rule"**. Finalizes the revenue side of the business.
*   **Capabilities:**
    *   **Mill Accounts:** Anticipated revenue vs. actual payment received.
    *   **Revenue Rate Sheets:** Mass update of revenue rates (quarterly/daily).
    *   **Reconciliation:** Recording actual mill payments and account register balancing.
    *   **Revenue Reporting:** Revenue summaries and account balance reports.

### Module 7: Insights & Dashboards (**The "What it means"**)
Aligns with the **"Output Rule"**. Provides the cross-functional analysis requested in the SOW.
*   **Capabilities:**
    *   **Executive Dashboard:** Power BI integration for production and profitability trends.
    *   **Ad-hoc Analysis:** Refreshable Excel datasets for pivots (Loads and Load Details).
    *   **Monthly P&L:** Cross-module financial performance reporting.

---

## Modularization Intuition Applied

1.  **Foundation:** Module 1 (Security + Species/Rate lookups).
2.  **Entities:** Module 2 (Loggers, Mills, Truckers).
3.  **Transactions:** Module 3 (The actual Load imports and tickets).
4.  **Workflow/Contracts:** Modules 4-5 (The logic of *how* we pay based on contracts and roads).
5.  **Output/Reconciliation:** Module 6 (Closing the loop with Mill payments).
6.  **Insights:** Module 7 (The Dashboard).
