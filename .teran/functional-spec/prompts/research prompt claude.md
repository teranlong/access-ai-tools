You are a research agent. Your job is to read all 20 functional specification files listed below and produce a
detailed structural analysis. Do NOT write any files — just return analysis text.

Files to Read

Base: C:\Users\Teran\LocalProjects\access-ai-tools\agent-data\ai-compatible\v1.0.0\

Heartland Bank (Heartland Bank/Functional Specifications/)
1. Heartland FS Module 1 - Configuration.docx.md
2. Heartland FS Module 2 - Shareholders and Transactions.docx.md
3. Heartland FS Module 4 - Dividends.docx.md
4. Heartland FS Module 5 - Stock Awards.docx.md
5. Heartland FS Module 6 - Reports.docx.md

KnightG (KnightG/Functional Specifications/)
6. KG Exclusion FS - API.docx.md
7. KG Exclusion FS Module 1 - Administration.docx.md
8. KG Exclusion FS Module 2 - Lists and Processing.docx.md
9. KG Exclusion FS Module 3 - Search.docx.md
10. KG Exclusion FS Module 4 - Jobs and Referrals.docx.md
11. KG Exclusion Master Design.docx.md
12. Knight Guardian API.docx.md

Statewide (Statewide/Functional Specifications/)
13. Statewide FS Module 1 - Administration.docx.md
14. Statewide FS Module 2 - Customers and Items.docx.md
15. Statewide FS Module 3 - Jobs and Rental Agreements.docx.md
16. Statewide Master Design.docx.md

Youngdahl (Youngdahl/Functional Specifications/)
17. Youngdahl FS Module 1 - Administration.docx.md
18. Youngdahl FS Module 4 - Labs.docx.md
19. Youngdahl FS Module 6 - Dashboard and Notifications.docx.md
20. Youngdahl Master Design.docx.md

Reading Instructions

- Read each file using the Read tool. If a file exceeds the token limit, read it in chunks (offset/limit) — use
limit=500 lines per chunk. Read enough to get the full structure.
- Large files: use offset=0 limit=500, then offset=500 limit=500, etc. until you have seen all the structural
content.
- Focus on: document structure (headings hierarchy), recurring section types, field-table conventions,
action-button patterns, designer note conventions, version history format, and any cross-module patterns.

What to Return

Return a detailed structural analysis with the following sections:

1. File Inventory

List each file, its project, approximate size (small/medium/large), and whether it's a module spec or a master
design doc.

2. Document Structure Patterns

- What heading levels are used (H1, H2, H3, H4, etc.)
- Standard opening sections (version table, intro paragraph, etc.)
- Standard closing sections
- How sections are named (consistent patterns across projects)

3. Section Types Found

List every distinct section type you found across all docs (e.g., "Actions", "Elements", "Designer Notes",
"Business Rules"). For each, describe how it appears and how consistently it appears.

4. Field/Element Table Pattern

Describe the column schema used for field definition tables (column names, what X/R/E/C mean, formatting notes
columns, etc.)

5. Action Button Pattern

How are actions/buttons documented? What format? What information is captured per button?

6. Designer Notes / Dev Notes Pattern

How are these used? Are they consistently placed? What kind of content goes in each?

7. Master Design vs Module Spec Differences

What structural differences exist between a "Master Design" document and a module-level functional spec?

8. API Documentation Pattern (KnightG only)

Describe how the API spec documents differ structurally from the module specs.

9. Cross-Project Variation

What structural conventions are consistent across ALL four projects? What varies? Note any evolution (e.g., newer
projects use a pattern that older ones don't).

10. Version Control Convention

How is version history captured? What fields are used?

11. Notable Omissions

What information is commonly ABSENT from these specs that you'd expect in a complete functional spec (e.g., no
error message text, no workflow diagrams inline, no data type constraints spelled out)?

12. Writing Style Observations

Describe the prose style, level of formality, abbreviation conventions, and any recurring phrasing patterns.

Be thorough. This analysis will be used to build templates, guidelines, and a scoring rubric for producing this
type of document in the future. If a file is too large to read fully, read at minimum the first 500 lines and
last 100 lines to capture opening and closing patterns, plus any mid-document section headers you can find via
grep.