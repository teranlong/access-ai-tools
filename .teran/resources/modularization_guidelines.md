# Project Modularization Guidelines & Observations

Based on an analysis of successful Access/Web migration projects (Heartland Bank, Statewide, KnightG, Youngdahl), the following patterns and rules define how complex projects are split into manageable functional modules.

## Key Patterns Observed

1.  **Foundational Setup (Module 1):** Every project begins with an "Administration" or "Configuration" module. This handles the "plumbing"—user access, global lookup tables, and system-wide settings that every other module relies on.
2.  **Noun-Based Partitioning:** Modules often center around primary business entities (Shareholders, Customers, Items). When entities are tightly coupled in the user's mental model, they are grouped together (e.g., "Customers and Items").
3.  **Lifecycle-Based Partitioning:** High-intensity workflows with clear states (Draft -> Review -> Approved) are isolated. This prevents the core entity modules from being overwhelmed by complex "transactional" logic.
4.  **Context/Persona Splitting:** Projects are often split by *where* and *who*. Youngdahl separates "Field" tasks from "Lab" tasks, aligning the software structure with the physical world of the technicians.
5.  **Reporting as an Output Layer:** Reporting is typically treated as a final aggregation layer, either bundled at the end or integrated as a "read-only" view of the data captured in earlier modules.

---

## Guidelines for Splitting a Project into Modules

### 1. The "Foundation" Rule (Module 1)
**Group all "Read-Mostly" and Setup data here.** 
If a feature is required for the system to function but isn't part of the daily transactional workflow, it belongs in Administration.
*   **Includes:** User Roles, Permissions, Global Config, Static Lookups (States, Unit Types, Sanctions Programs).

### 2. The "Entity Ownership" Rule
**Cluster modules around primary nouns.**
A module should "own" the lifecycle of a core business object. If two nouns are inseparable in the user's mind, keep them together. 
*   **Rule of Thumb:** If you can't describe the module without using both nouns, they belong together.
*   **Example:** "Customers and Items" (Statewide).

### 3. The "Lifecycle/Workflow" Rule
**Isolate state-heavy processes.**
If a process involves multi-step workflows, complex calculations, or a "Finalization/Locking" step, it deserves its own module.
*   **Why:** This keeps the core entity logic "clean" and focuses the complex business rules into a dedicated space.
*   **Example:** "Dividends" (Heartland) is separate from "Shareholders" because it has a specific time-bound calculation and locking cycle.

### 4. The "Persona/Environment" Rule
**Split by who uses it and where.**
If one set of features is used by field technicians on tablets and another by office staff on desktops, split them. This simplifies the UI/UX footprint for specific hardware.
*   **Example:** "Dispatch & Tasks" (Field) vs. "Administration" (Office).

### 5. The "Output" Rule
**Separate Input from Aggregation.**
Group complex reporting, dashboards, and third-party exports into a final module or a dedicated reporting section. This ensures data entry remains focused on integrity, while reporting focuses on performance and presentation.

---

## The Standard "Module Intuition" Sequence
*   **Module 1:** Setup & Security (**The "How it works"**)
*   **Module 2-3:** Core Entities (**The "What we track"**)
*   **Module 4-5:** Complex Workflows (**The "What we do with it"**)
*   **Module 6:** Reporting & Dashboards (**The "What it means"**)
