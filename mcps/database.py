# mcps/database.py
#
# SQLite MCP server configuration.
# The sqlite binary path and DB path are resolved at runtime so the same code
# works on Windows local dev, Linux Docker, and cloud VMs.
#
# Binary resolution priority:
#   1. MCP_SQLITE_BIN env var (explicit override — useful in Docker or CI).
#   2. `mcp-server-sqlite` on PATH (installed by uv/pip into the active venv).
#   3. Falls back to the local .venv path for Windows dev convenience.
#
# DB path resolution priority:
#   1. MCP_DB_PATH env var (explicit override).
#   2. <MCP_WORKSPACE_ROOT>/database.sqlite

import os
import shutil
import sys

# ── Resolve workspace root ────────────────────────────────────────────────────
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_WORKSPACE = os.path.join(_REPO_ROOT, "test_project")
WORKSPACE_ROOT = os.getenv("MCP_WORKSPACE_ROOT", _DEFAULT_WORKSPACE)

# ── Resolve mcp-server-sqlite binary ─────────────────────────────────────────
def _resolve_sqlite_bin() -> str:
    # 1. Explicit env override — always trusted (avoids cross-OS path checks)
    env_bin = os.getenv("MCP_SQLITE_BIN")
    if env_bin:
        return env_bin

    # 2. On PATH (works in Docker / Linux / any venv that has mcp-server-sqlite installed)
    which_bin = shutil.which("mcp-server-sqlite")
    if which_bin:
        return which_bin

    # 3. Windows local dev fallback: look inside the project .venv
    if sys.platform == "win32":
        local_bin = os.path.join(_REPO_ROOT, ".venv", "Scripts", "mcp-server-sqlite.exe")
        if os.path.isfile(local_bin):
            return local_bin

    # 4. Last resort: trust it's on PATH and let the OS raise a clear error
    return "mcp-server-sqlite"


_SQLITE_BIN = _resolve_sqlite_bin()
_DB_PATH = os.getenv("MCP_DB_PATH", os.path.join(WORKSPACE_ROOT, "database.sqlite"))

database_config = {
    "sqlite": {
        "transport": "stdio",
        "command": _SQLITE_BIN,
        "args": ["--db-path", _DB_PATH],
    }
}
