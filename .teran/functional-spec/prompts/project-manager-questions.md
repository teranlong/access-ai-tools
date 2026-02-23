<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# you are a senior project manager getting started on an access database migration project (backend access -> sql server) (frontend access - web/react). You are tasked to build a functional spec for the migration project. it should include a functional spec master document for the app overall and a per module fs for each module

an example would be
FS Master
FS Module 1 - Administration
FS Module 2 - Customers and Items
FS Module 3 - Jobs and Rental Agreements
FS Module 4 - Work Order and Calendar

but each app is tailored to the particular company

these companies already have an access db application which fills their needs. You have access to customer and the previous database.

you must write a complete and accurate functional spec. first you may provide a list of questions to

- a customer and daily user of the old application familiar with the business processes and use cases for the company but not the database internals or any technical details
- a technical expert familiar with the technical details of the app, but has never used the app before. they have access to the application to answer your questions.

provide an exhaustive list of questions to ask each person. You may only query them once so include follow up questions in a tree format as necessary

Below are one-shot interview trees for each role. Each bullet is a question; indented bullets are conditional follow‑ups you ask immediately if the previous answer suggests it.

***

## Questions for business user (non‑technical, daily user)

### A. Company, roles, and goals

- What is your role at the company, and how do you use the current Access application in your day‑to‑day work?
    - Which tasks in your typical day absolutely depend on this application?
- What are the main business goals the application helps you achieve (e.g., manage rentals, track jobs, invoice customers, schedule work)?
- Which other roles or departments use the application (e.g., admin, sales, dispatch, technicians, accounting)?
    - For each role, what are the top 3 things they do in the app?
- What are the most critical outcomes the new system must support so you consider the migration a success (e.g., fewer errors, faster entry, better reporting)?[^1_1]


### B. Overall workflows and modules

- In your own words, what are the main “modules” or sections of the current application (e.g., Administration, Customers and Items, Jobs and Rental Agreements, Work Orders and Calendar)?
    - Do you have any additional sections or screens that are unique to your company (e.g., inspections, inventory counts, special pricing, regulatory forms)?
- For each of the main modules, what is the primary business process it supports?
    - Administration – What tasks do you perform here (e.g., user setup, company settings, codes, reference data)?
    - Customers and Items – How do you create, find, update, and manage customers and items?
    - Jobs and Rental Agreements – How do you create and manage jobs or agreements from start to finish?
    - Work Orders and Calendar – How do you schedule work, assign people, and track status?
- Are there any “unofficial” workflows that users have developed over time (e.g., data entry shortcuts, special sequencing of screens, printing to Excel and doing extra work outside the system)?
    - Which of those unofficial workflows are essential and should be supported or improved in the new system?


### C. Detailed end‑to‑end process flows

For each key process, ask the full flow:

- New customer and job/agreement flow:
    - When a brand‑new customer contacts you, walk me through every step you follow using the application from first contact until the job or rental agreement is created.
        - How do you capture their details (name, address, contacts, billing info)?
        - How do you select or set up the items/services for them?
        - How do you generate any agreement, quote, or estimate (including printed or emailed documents)?
        - How do you confirm the job/agreement internally (approvals, checks, or reviews)?
- Scheduling and work execution:
    - Once a job/agreement is created, how do you schedule it on the calendar or create work orders?
        - How do you assign technicians/crews or resources?
        - How do you update status (e.g., scheduled, in progress, completed, cancelled)?
        - How do you capture work performed, parts used, notes, and photos or documents?
- Billing and payments:
    - How do you turn a completed job/agreement into an invoice or billing record?
        - How do you handle partial billing, deposits, or progress invoices if applicable?
        - How do you record payments and handle overpayments, underpayments, or credit memos?
- Customer service and follow‑ups:
    - How do you track customer issues, complaints, or follow‑up tasks in the system (if at all)?
        - Do you schedule follow‑up visits, reminders, or recurring jobs? How?
- Cancellations and changes:
    - When a customer changes or cancels a job/agreement, what steps do you take in the application?
        - How do you adjust schedules, inventory, and billing in those cases?


### D. Screen‑by‑screen behavior (from the user’s perspective)

- When you first open the application, what do you see, and what do you typically do first?
- Please name the 5–10 screens or forms you use the most, and for each:
    - What is the screen called (or how do you refer to it)?
    - What do you use it for?
    - What information do you usually enter, and in what order?
    - What information do you usually look up or review?
    - What actions do you perform (e.g., save, print, email, export, duplicate, close, navigate to another screen)?
    - Are there any fields that are required for you to continue or save?
    - Are there any automatic behaviors you rely on (e.g., auto‑fill fields, calculated totals, automatic date/time stamps)?[^1_2]
- Are there any “hidden” screens, pop‑ups, or dialogs that appear only in certain situations (e.g., warnings, confirmations, lookup dialogs)?[^1_2]
    - When do these appear, and what choices do you usually make?[^1_2]


### E. Data and business rules (user‑visible)

- Which pieces of customer information are mandatory to set up a customer?
- Which pieces of item or product information are mandatory to set up an item?
- Are there any rules about valid combinations of values (e.g., certain items only allowed for certain customer types, certain statuses allowed only if fields are filled)?[^1_2]
- What are the rules you know of around:
    - Pricing and discounts (e.g., customer‑specific pricing, volume discounts, special promotions).[^1_2]
    - Taxes (e.g., tax‑exempt customers, different tax rates by location or item).[^1_2]
    - Deposits, minimum charges, late fees, or penalties.[^1_2]
    - Rental periods (e.g., day/week/month rules, grace periods, partial day handling).[^1_2]
- Are there any approval steps (manager sign‑off, credit check, safety check) you perform inside or outside the system?
    - How do you currently track that an approval has happened?


### F. Reporting and exports

- What reports do you run regularly from the system (daily, weekly, monthly)?
    - For each commonly used report:
        - What is it called?
        - What decisions do you make based on it?
        - How often do you run it?
- Are there any ad‑hoc exports to Excel, CSV, or other formats you rely on?[^1_2]
    - What do you do with that exported data once it’s in Excel or another tool?[^1_2]
- Which reports or exports are critical for:
    - Management or owners.
    - Accounting or finance.
    - Operations (dispatch, technicians, warehouse).


### G. Integrations and external tools (user view)

- Does the current application connect to any other systems from your perspective (e.g., QuickBooks, email, file shares, other apps)?[^1_2]
    - How do you use those connections in your daily work (e.g., push invoices to accounting, send emails with attachments, export/import files)?[^1_2]
- Are there any manual steps where you copy/paste data between this system and others?[^1_2]
    - For each, what data do you move, how often, and why?[^1_2]


### H. Pain points and wish‑list

- What are the most frustrating parts of the current application for you?[^1_1]
    - Where do you lose time or make mistakes most often?[^1_1]
- Are there features that exist but are so awkward that people avoid using them?[^1_1]
- Are there tasks you currently do outside the system (in spreadsheets, email, paper) that you wish the system handled directly?[^1_3]
- If you could change or add only three things in the new web application, what would they be and why?[^1_1]
- Are there any performance issues (slow screens, long report runs) that affect your work significantly?[^1_2]


### I. Access specifics that affect migration (from user view)

- Are there any parts of the application that only one or two “power users” really understand?
    - Who are they, and what special tasks do they perform?
- Are there any seasonal or rare processes (e.g., annual renewals, inventory counts, rate changes) that you must not forget to support even if they happen infrequently?
- Do users ever work simultaneously on the same record or job? How do you handle conflicts today?[^1_2]


### J. Security, roles, and permissions (user view)

- Do different people see different screens or fields when they log in (if there is login)?[^1_2]
    - Which roles exist (e.g., admin, manager, dispatcher, technician, clerk), and what can or cannot they do?[^1_2]
- Are there any sensitive data fields (e.g., pricing, discounts, customer notes) that should only be visible to certain roles?[^1_2]
- Are there any approval or sign‑off actions that only certain roles can perform?[^1_2]


### K. Change management and training

- How do new employees currently learn to use the system (formal training, manuals, shadowing someone)?
- Are there any forms, cheat sheets, or instructions people keep near their desks for using the application?
    - Can you describe those, and what they help with?
- What kind of support would help you adopt the new web application (e.g., in‑app guidance, short videos, step‑by‑step help, printed quick reference)?[^1_1]

***

## Questions for technical expert (Access / technical, non‑user)

### A. High‑level architecture and deployment

- How is the Access application currently deployed: single .accdb/.mdb file, split front‑end/back‑end, multiple front‑ends, shared network drive, or something else?[^1_2]
    - If split, what are the file names and locations of the front‑end(s) and back‑end(s)?[^1_2]
    - Are there multiple versions or copies in circulation (e.g., each user with their own front‑end)?[^1_2]
- Which version(s) of Access and Office are used, and on what Windows versions?[^1_2]
- Are there any external components or libraries used (e.g., ActiveX controls, COM components, custom DLLs, third‑party add‑ins)?[^1_2]
    - For each, what is it used for and where is it referenced?[^1_2]


### B. Database structure (tables, relationships, constraints)

- How many back‑end database files are there, and what is the approximate number of tables in each?[^1_2]
- Are all tables stored in Access, or are there linked tables to other data sources (e.g., existing SQL Server, Excel, other Access files)?[^1_2]
    - For each linked table source, what is the data source type and connection information?[^1_2]
- How are relationships defined in Access (relationship view)?[^1_2]
    - Are referential integrity, cascade update, and cascade delete options used, and where?[^1_2]
    - Are there known logical relationships that are not enforced in the Access relationship diagram?[^1_2]
- Are there lookup tables or code tables used for drop‑downs and validation lists?[^1_2]
    - Which tables serve as lookups, and how widely are they referenced?[^1_2]
- Are there any known denormalizations or “workaround” structures (e.g., fields storing multiple values in a single text field, comma‑separated IDs, EAV tables)?[^1_2]


### C. Data volume, quality, and performance

- What is the approximate size of each back‑end database file (MB/GB)?[^1_2]
- What are approximate row counts for the largest tables (e.g., customers, items, jobs, work orders, history)?[^1_2]
- Are there any performance issues today (slow queries, frequent compacts, lockups)?[^1_2]
    - Which tables/queries/screens are most affected?[^1_2]
- Are there any known data quality issues (e.g., inconsistent codes, missing foreign keys, duplicate customers/items)?[^1_2]
    - Are there any existing scripts or processes for cleanup or maintenance?[^1_2]


### D. Business logic implementation (queries, macros, VBA)

- Where is the majority of business logic implemented: queries, macros, data macros, VBA modules, form/report code, or a mix?[^1_2]
    - Approximately how many saved queries exist, and how many are actually used by forms/reports?[^1_2]
- Are there parameter queries or action queries (append, update, delete, make‑table) triggered from the UI?[^1_2]
    - Which of these are critical to daily or periodic operations?[^1_2]
- Are there macros attached to forms/reports or standalone macros?[^1_2]
    - What are the main macro‑driven workflows (e.g., auto‑opening forms, printing reports, data imports/exports)?[^1_2]
- Is there VBA code in standard modules, class modules, or behind forms and reports?[^1_2]
    - Roughly how many distinct modules or significant procedures implement business rules?[^1_2]
    - Are there any central “utility” modules that many forms rely on (e.g., validation, logging, formatting)?[^1_2]
- Are there any data macros or table‑level events being used (in .accdb)?[^1_2]
    - If yes, what kind of logic do they implement (validation, defaulting, cascades)?[^1_2]


### E. UI structure (forms, reports, navigation)

- How many forms and reports are in the application (rough estimate)?[^1_2]
    - Are any of them clearly obsolete or unused?[^1_2]
- How is navigation organized today (switchboard, custom main menu form, ribbon customization, navigation forms)?[^1_2]
    - What is the startup object and any autoexec macro behavior?[^1_2]
- For key forms:
    - Which forms are used for data entry and maintenance of master data (customers, items, codes)?[^1_2]
    - Which forms handle transactional data (jobs, rental agreements, work orders, scheduling)?[^1_2]
    - Which forms are more like dashboards or search/browse screens?[^1_2]
- Are there subforms, tab controls, or complex nested form structures?[^1_2]
    - Which forms are most complex in terms of subforms and conditional logic?[^1_2]
- Are there custom menus or ribbon customizations we need to be aware of?[^1_2]


### F. Validations, defaults, and calculations (technical view)

- Which fields have validation rules defined at the table level or field level?[^1_2]
    - Are there fields with input masks that reflect business rules (e.g., phone, account codes)?[^1_2]
- Which fields have default values defined?[^1_2]
    - Are any defaults based on expressions, functions, or user context (e.g., current date, current user)?[^1_2]
- Where are key calculations defined (totals, taxes, discounts, balances, rental charges)?
    - In queries (calculated columns).[^1_2]
    - In forms (calculated controls, VBA).[^1_2]
    - In reports (calculated controls, VBA).[^1_2]
- Are there any triggers for cascading logic that we need to preserve (e.g., when status changes, update date fields or related records)?[^1_2]


### G. Imports, exports, and integrations (technical)

- Are there any automated or semi‑automated data import processes (e.g., from CSV, Excel, text files, other databases)?[^1_2]
    - How are these implemented (macros, VBA, saved import specifications)?[^1_2]
- Are there any exports to external systems (e.g., accounting software, regulatory systems, partners)?[^1_2]
    - How are exports triggered and in what formats?[^1_2]
- Does the application send emails (via Outlook automation or other methods)?[^1_2]
    - What exactly is sent (reports as attachments, simple notifications, templated emails)?[^1_2]
- Are there any ODBC or OLE DB connections already defined (e.g., linked tables to SQL Server)?[^1_2]
    - If yes, how are connection strings and credentials managed?[^1_2]


### H. Security, users, and permissions (technical)

- Does the Access application use any built‑in user‑level security (for older .mdb) or a custom login system?[^1_2]
    - If yes, how are users and roles stored (tables, workgroup file, Windows integration)?[^1_2]
- Are there any row‑level or field‑level security mechanisms implemented in Access (even if informal, via UI logic)?[^1_2]
- How many concurrent users typically connect to the back‑end, and how is file locking configured?[^1_2]
    - Are there known issues with record locking or conflicts?[^1_2]


### I. Environment, backup, and maintenance

- Where are the back‑end database files stored (file server, local machine, cloud share)?[^1_2]
    - Are there multiple environments (production, test, training) or just one?[^1_2]
- How are backups performed for the Access back‑end files?[^1_2]
    - How often are backups taken, and what is the retention?[^1_2]
- Are there any regular maintenance tasks (compacting/repairing the database, archiving old data, deleting temp data)?[^1_2]
    - How are these tasks run (manual, scheduled scripts, in‑app buttons)?[^1_2]


### J. Known limitations, technical debt, and edge cases

- Are there any known technical limitations or issues in the current application (file size limits, frequent corruption, unsupported features)?[^1_2]
- Are there any “dangerous” or sensitive operations in the app (e.g., mass delete/update functions, schema changes from the UI)?[^1_2]
    - How are these currently protected (passwords, hidden forms, restricted access)?[^1_2]
- Are there any edge‑case processes implemented for specific customers, contracts, or regulatory requirements (e.g., one‑off fields, hard‑coded IDs)?[^1_2]
    - Where are those implemented (specific forms, queries, code modules)?[^1_2]


### K. Migration‑specific considerations to SQL Server and web/React

- Have you ever linked this Access back‑end to SQL Server or attempted a prior migration (e.g., using SQL Server Migration Assistant for Access)?[^1_2]
    - If yes, what issues or incompatibilities were encountered (data types, reserved words, queries that didn’t convert)?[^1_2]
- Do you know of any Access‑specific features (e.g., multi‑value fields, attachment fields, complex data types) used in this database?[^1_2]
    - In which tables/fields are these used?[^1_2]
- Are there any very complex queries (e.g., nested subqueries, domain aggregate functions, crosstab queries) that are critical to the application?[^1_2]
    - Where are they used (forms, reports, exports)?[^1_2]
- Are there any time‑based or scheduled processes (e.g., daily rollups, end‑of‑day routines) implemented in Access or via external scripts?[^1_2]
    - How are these triggered (user action, Windows Task Scheduler, macros)?[^1_2]


### L. Artifacts and documentation

- Is there any existing technical documentation, ER diagrams, or developer notes for this Access application?
    - If yes, where are they stored and how up to date are they?
- Are there any naming conventions for tables, queries, forms, and reports that we should be aware of (e.g., prefixes for module ownership, temp vs permanent)?[^1_2]
- Are there any test data sets, sample databases, or demo copies that differ from production?[^1_2]
    - If yes, what are the differences and how trustworthy are they for understanding real behavior?[^1_2]

***

You can treat these two trees as your one‑shot interview guides: ask everything in order, drilling into follow‑ups immediately so the functional spec master document and each module‑level spec can be complete and accurate.
<span style="display:none">[^1_4]</span>

<div align="center">⁂</div>

[^1_1]: interests.programming.functional_specs

[^1_2]: https://www.perplexity.ai/search/7a1d641e-0b99-4c8f-8e69-77515677a628

[^1_3]: https://www.perplexity.ai/search/75eada0f-9081-4683-973e-fcf9b264e1f0

[^1_4]: https://www.perplexity.ai/search/4143ca09-52cf-4dd5-b654-d7a7b65ad765

