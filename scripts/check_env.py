import os
import re
import sys
from pathlib import Path


PLACEHOLDER_HINTS = ("change_", "placeholder", "example", "default", "your_")
REQUIRED_KEYS = ("MYSQL_ROOT_PASSWORD", "MYSQL_PASSWORD", "JWT_SECRET")


def load_env_file(path: Path) -> dict:
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def has_mixed_complexity(value: str) -> bool:
    checks = [
        re.search(r"[a-z]", value),
        re.search(r"[A-Z]", value),
        re.search(r"\d", value),
        re.search(r"[^A-Za-z0-9]", value),
    ]
    return sum(bool(c) for c in checks) >= 3


def validate(values: dict) -> list[str]:
    errors = []
    for key in REQUIRED_KEYS:
        value = values.get(key)
        if not value:
            errors.append(f"{key} is missing.")
            continue

        lowered = value.lower()
        if any(hint in lowered for hint in PLACEHOLDER_HINTS):
            errors.append(f"{key} still contains placeholder/default text.")

        min_len = 32 if key == "JWT_SECRET" else 12
        if len(value) < min_len:
            errors.append(f"{key} must be at least {min_len} characters.")

        if not has_mixed_complexity(value):
            errors.append(f"{key} must include mixed character types (letters/numbers/symbols).")

    return errors


def main() -> int:
    env_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".env")
    if not env_path.exists():
        print(f"[env-check] File not found: {env_path}")
        return 1

    values = load_env_file(env_path)
    errors = validate(values)
    if errors:
        print("[env-check] FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"[env-check] OK: {env_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
