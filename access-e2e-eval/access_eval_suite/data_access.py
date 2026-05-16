from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from . import constants as ac
from .environment import inspect_environment


class DataAccessError(RuntimeError):
    pass


class AccessData:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self._odbc = None
        self._access = None

    def __enter__(self) -> "AccessData":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def open(self) -> None:
        status = inspect_environment()
        if status.has_pyodbc and status.ace_drivers:
            self._open_odbc(status.ace_drivers[0])
            return
        if status.has_pywin32:
            self._open_com()
            return
        raise DataAccessError(
            "No database validation path available. Install pyodbc with an ACE "
            "Access driver or install pywin32 for Access COM/DAO validation."
        )

    def close(self) -> None:
        if self._odbc is not None:
            self._odbc.close()
            self._odbc = None
        if self._access is not None:
            self._access.CloseCurrentDatabase()
            self._access.Quit(ac.AC_QUIT_SAVE_NONE)
            self._access = None

    def execute(self, sql: str) -> None:
        if self._odbc is not None:
            cursor = self._odbc.cursor()
            cursor.execute(sql)
            self._odbc.commit()
            return
        db = self._access.CurrentDb()
        db.Execute(sql, ac.DAO_FAIL_ON_ERROR)

    def scalar(self, sql: str) -> Any:
        rows = self.rows(sql)
        if not rows:
            return None
        first_row = rows[0]
        return next(iter(first_row.values()))

    def rows(self, sql: str) -> list[dict[str, Any]]:
        if self._odbc is not None:
            cursor = self._odbc.cursor()
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
        return self._rows_com(sql)

    def insert_audit_event(
        self,
        event_type: str,
        entity_name: str,
        entity_id: int | None,
        summary: str,
        company_id: int | None = None,
        user_id: int | None = None,
    ) -> None:
        self.execute(
            "INSERT INTO AuditEvents "
            "(UserID, CompanyID, EventType, EntityName, EntityID, EventSummary, EventAt) "
            f"VALUES ({_nullable_int(user_id)}, {_nullable_int(company_id)}, "
            f"'{_escape(event_type)}', '{_escape(entity_name)}', {_nullable_int(entity_id)}, "
            f"'{_escape(summary)}', Now())"
        )

    def _open_odbc(self, driver: str) -> None:
        import pyodbc

        connection_string = (
            f"DRIVER={{{driver}}};"
            f"DBQ={self.database_path};"
            "ExtendedAnsiSQL=1;"
        )
        self._odbc = pyodbc.connect(connection_string, autocommit=False)

    def _open_com(self) -> None:
        import win32com.client

        self._access = win32com.client.Dispatch("Access.Application")
        try:
            self._access.Visible = False
        except Exception:
            pass
        self._access.OpenCurrentDatabase(str(self.database_path))

    def _rows_com(self, sql: str) -> list[dict[str, Any]]:
        db = self._access.CurrentDb()
        recordset = db.OpenRecordset(sql)
        try:
            if recordset.EOF:
                return []
            fields = [recordset.Fields(index).Name for index in range(recordset.Fields.Count)]
            results: list[dict[str, Any]] = []
            while not recordset.EOF:
                results.append(
                    {
                        field_name: recordset.Fields(field_name).Value
                        for field_name in fields
                    }
                )
                recordset.MoveNext()
            return results
        finally:
            recordset.Close()


def count_where(database_path: Path, table: str, where: str) -> int:
    with AccessData(database_path) as data:
        return int(data.scalar(f"SELECT Count(*) AS RecordCount FROM {table} WHERE {where}") or 0)


def assert_single_row(database_path: Path, table: str, where: str) -> dict[str, Any]:
    with AccessData(database_path) as data:
        rows = data.rows(f"SELECT * FROM {table} WHERE {where}")
    if len(rows) != 1:
        raise AssertionError(f"Expected exactly one row in {table} where {where}; found {len(rows)}.")
    return rows[0]


def _escape(value: str) -> str:
    return value.replace("'", "''")


def _nullable_int(value: int | None) -> str:
    return "Null" if value is None else str(value)


def csv(values: Iterable[str]) -> str:
    return ", ".join(f"'{_escape(value)}'" for value in values)
