# Type stubs for common.db_dsn module
from typing import Optional

def resolve_dsn(*, strict: bool = True, role: str = "default", app: str | None = None) -> str: ...
