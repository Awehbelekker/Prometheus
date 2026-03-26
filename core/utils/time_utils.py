from datetime import datetime, UTC

__all__ = ["utc_now", "utc_iso"]

def utc_now() -> datetime:
    """Return a timezone-aware UTC datetime (Python 3.11+ style)."""
    return datetime.now(UTC)

def utc_iso() -> str:
    """Return ISO8601 string in UTC with trailing 'Z' (e.g. 2025-08-11T12:34:56.123456Z)."""
    return utc_now().isoformat().replace("+00:00", "Z")
