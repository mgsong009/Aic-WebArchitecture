from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psycopg
import pymysql


SOURCE_RAW_TABLES = [
    ("users", "raw_users"),
    ("classes", "raw_classes"),
    ("assignments", "raw_assignments"),
    ("submissions", "raw_submissions"),
    ("metrics", "raw_metrics"),
]

WAREHOUSE_TABLES = [
    "raw_users",
    "raw_classes",
    "raw_assignments",
    "raw_submissions",
    "raw_metrics",
    "stg_submission_metrics",
    "mart_student_assignment_metrics",
    "mart_assignment_summary",
    "mart_class_summary",
]


@dataclass(frozen=True)
class ValidationIssue:
    check_name: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    source_counts: dict[str, int]
    warehouse_counts: dict[str, int]
    failures: list[ValidationIssue]

    @property
    def passed(self) -> bool:
        return not self.failures


def _mysql_count(connection: pymysql.connections.Connection, table_name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) AS row_count FROM {table_name}")
        row = cursor.fetchone()
    return int(row["row_count"])


def _pg_scalar(connection: psycopg.Connection, sql: str) -> Any:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
    return next(iter(row.values()))


def _pg_count(connection: psycopg.Connection, table_name: str) -> int:
    return int(_pg_scalar(connection, f"SELECT COUNT(*) AS row_count FROM {table_name}"))


def _pg_issue_count(connection: psycopg.Connection, sql: str) -> int:
    return int(_pg_scalar(connection, sql))


def collect_validation_report(
    source: pymysql.connections.Connection,
    warehouse: psycopg.Connection,
) -> ValidationReport:
    source_counts = {
        source_table: _mysql_count(source, source_table)
        for source_table, _ in SOURCE_RAW_TABLES
    }
    warehouse_counts = {
        table_name: _pg_count(warehouse, table_name)
        for table_name in WAREHOUSE_TABLES
    }

    failures: list[ValidationIssue] = []

    for source_table, raw_table in SOURCE_RAW_TABLES:
        source_count = source_counts[source_table]
        raw_count = warehouse_counts[raw_table]
        if source_count != raw_count:
            failures.append(
                ValidationIssue(
                    check_name=f"{source_table}->{raw_table}",
                    message=f"source={source_count}, warehouse={raw_count}",
                )
            )

    stg_count = warehouse_counts["stg_submission_metrics"]
    raw_submission_count = warehouse_counts["raw_submissions"]
    if stg_count != raw_submission_count:
        failures.append(
            ValidationIssue(
                check_name="staging submissions",
                message=f"raw_submissions={raw_submission_count}, stg_submission_metrics={stg_count}",
            )
        )

    mart_student_count = warehouse_counts["mart_student_assignment_metrics"]
    if mart_student_count != raw_submission_count:
        failures.append(
            ValidationIssue(
                check_name="student assignment mart",
                message=f"raw_submissions={raw_submission_count}, mart_student_assignment_metrics={mart_student_count}",
            )
        )

    assignment_mismatches = _pg_issue_count(
        warehouse,
        """
        SELECT COUNT(*)
        FROM mart_assignment_summary mart
        JOIN (
            SELECT source_assignment_id, COUNT(*) AS raw_count
            FROM raw_submissions
            GROUP BY source_assignment_id
        ) raw USING (source_assignment_id)
        WHERE mart.submission_count <> raw.raw_count
        """,
    )
    if assignment_mismatches:
        failures.append(
            ValidationIssue(
                check_name="assignment mart counts",
                message=f"{assignment_mismatches} assignment summary row(s) differ from raw submissions",
            )
        )

    class_mismatches = _pg_issue_count(
        warehouse,
        """
        SELECT COUNT(*)
        FROM mart_class_summary mart
        JOIN (
            SELECT a.source_class_id, COUNT(*) AS raw_count
            FROM raw_submissions s
            JOIN raw_assignments a USING (source_assignment_id)
            GROUP BY a.source_class_id
        ) raw USING (source_class_id)
        WHERE mart.submission_count <> raw.raw_count
        """,
    )
    if class_mismatches:
        failures.append(
            ValidationIssue(
                check_name="class mart counts",
                message=f"{class_mismatches} class summary row(s) differ from raw submissions",
            )
        )

    return ValidationReport(
        source_counts=source_counts,
        warehouse_counts=warehouse_counts,
        failures=failures,
    )


def format_validation_report(
    report: ValidationReport,
    raw_loaded_counts: dict[str, int] | None = None,
    title: str = "Warehouse validation summary",
) -> str:
    lines = [title]

    if raw_loaded_counts is not None:
        lines.append("")
        lines.append("Extract/upsert rows:")
        for table_name, row_count in raw_loaded_counts.items():
            lines.append(f"  {table_name}: {row_count}")

    lines.append("")
    lines.append("Source row counts:")
    for table_name, row_count in report.source_counts.items():
        lines.append(f"  {table_name}: {row_count}")

    lines.append("")
    lines.append("Warehouse row counts:")
    for table_name, row_count in report.warehouse_counts.items():
        lines.append(f"  {table_name}: {row_count}")

    lines.append("")
    if report.passed:
        lines.append("Validation: PASS")
    else:
        lines.append("Validation: FAIL")
        for failure in report.failures:
            lines.append(f"  - {failure.check_name}: {failure.message}")

    return "\n".join(lines)
