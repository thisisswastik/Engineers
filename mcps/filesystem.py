# mcps/filesystem.py
#
# Filesystem MCP server configuration.
# Uses an environment-aware base path so this works on:
#   - Windows local dev (c:/Users/swastik/Desktop/engineers/test_project)
#   - Linux Docker container                        (/app/test_project)
#   - Any cloud VM                                  (set MCP_WORKSPACE_ROOT in env)

import os

# Resolve the workspace root at runtime:
#   1. Honour MCP_WORKSPACE_ROOT env var if set (Docker / CI / cloud).
#   2. Fall back to <repo_root>/test_project (works for local dev on any machine).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_WORKSPACE = os.path.join(_REPO_ROOT, "test_project")
WORKSPACE_ROOT = os.getenv("MCP_WORKSPACE_ROOT", _DEFAULT_WORKSPACE)

filesystem_config = {
    "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", WORKSPACE_ROOT],
    }
}
