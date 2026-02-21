"""
accdb_schema.py — Export the schema of an Access database (.accdb / .mdb) as Markdown.

Uses pyodbc with the Microsoft Access ODBC driver. Opens the DB read-only.
On failure, writes a clear explanation of the 32/64-bit mismatch issue and
manual export instructions.
"""

from __future__ import annotations

from pathlib import Path

from .base import ConversionResult, make_output_path


_DRIVER_NAME = "Microsoft Access Driver (*.mdb, *.accdb)"

_MANUAL_STEPS = """\
## Manual Export Instructions

The automated schema export failed (see error above). Use one of these methods:

### Option A — Access "Documenter" (built into MS Access)
1. Open the database in Microsoft Access.
2. Go to **Database Tools → Database Documenter**.
3. Select all tables → click **OK**.
4. Save the output as a PDF or print-to-text.

### Option B — Export table list via Access VBA
```vba
Dim db As DAO.Database
Dim tbl As DAO.TableDef
Set db = CurrentDb()
For Each tbl In db.TableDefs
    If Left(tbl.Name, 4) <> "MSys" Then Debug.Print tbl.Name
Next
```

### Option C — Export schema via SSMS (if linked to SQL Server)
Use SQL Server Management Studio to script all tables.

### 32/64-bit Note
pyodbc requires the **same bitness** as the installed Access ODBC driver.
- If Python is 64-bit, install "Microsoft Access Database Engine 2016 Redistributable (x64)".
- If Python is 32-bit, install the x86 version.
- Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920
"""


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Connect to an Access database and extract the schema as Markdown."""
    try:
        import pyodbc
    except ImportError as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=f"Missing dependency: {exc}. Run: pip install pyodbc",
        )

    out_path = make_output_path(source, output_root, project_root, ".md")
    sections: list[str] = [f"# Access Database Schema: {source.name}\n"]

    conn_str = (
        f"DRIVER={{{_DRIVER_NAME}}};"
        f"DBQ={source};"
        f"ReadOnly=1;"
    )

    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()

        # Get all user tables (skip MSys* system tables)
        tables = [
            row.table_name
            for row in cursor.tables(tableType="TABLE")
            if not row.table_name.startswith("MSys")
        ]
        tables.sort()

        sections.append(f"**Tables found:** {len(tables)}\n")

        for table_name in tables:
            col_rows = cursor.columns(table=table_name)
            columns: list[str] = []
            for col in col_rows:
                nullable = "NULL" if col.nullable else "NOT NULL"
                col_type = col.type_name
                size_info = f"({col.column_size})" if col.column_size else ""
                columns.append(
                    f"| `{col.column_name}` | `{col_type}{size_info}` | {nullable} |"
                )

            header = f"## Table: `{table_name}`\n\n"
            if columns:
                table_md = (
                    "| Column | Type | Nullable |\n"
                    "|--------|------|----------|\n"
                    + "\n".join(columns)
                )
            else:
                table_md = "_No columns found._"

            sections.append(header + table_md + "\n")

        cursor.close()
        conn.close()

    except Exception as exc:
        error_str = str(exc)
        # Provide helpful context for common driver-related errors
        extra = ""
        driver_issues = (
            "Data source name not found" in error_str
            or "IM002" in error_str
            or isinstance(exc, (UnicodeDecodeError, UnicodeError))
            or "codec can't decode" in error_str
        )
        if driver_issues:
            extra = (
                "\n\n**Likely cause:** The Microsoft Access ODBC driver is not installed "
                "or there is a 32/64-bit mismatch between Python and the driver. "
                "A UnicodeDecodeError from pyodbc typically means the driver returned "
                "a garbled error message — this almost always indicates the driver is missing.\n"
            )

        error_section = (
            f"## Conversion Error\n\n"
            f"**Error:** `{error_str}`{extra}\n\n"
            f"{_MANUAL_STEPS}"
        )
        sections.append(error_section)
        out_path.write_text("\n\n".join(sections), encoding="utf-8")

        return ConversionResult(
            success=False,
            output_files=[out_path],
            action="error",
            error=error_str,
        )

    out_path.write_text("\n\n---\n\n".join(sections), encoding="utf-8")

    return ConversionResult(
        success=True,
        output_files=[out_path],
        action="converted",
    )
