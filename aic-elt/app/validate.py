from __future__ import annotations

import sys
from contextlib import closing

from app.main import connect_source, connect_warehouse
from app.validation import collect_validation_report, format_validation_report


def main() -> None:
    with closing(connect_source()) as source, closing(connect_warehouse()) as warehouse:
        report = collect_validation_report(source, warehouse)

    print(format_validation_report(report))
    if not report.passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
