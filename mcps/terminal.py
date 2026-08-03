# mcps/terminal.py
#
# Shell / Terminal MCP server configuration.
# MCP_SHELL_DEFAULT_WORKDIR is set to the workspace root so the Coder agent's
# shell commands run inside the generated project directory.
#
# Works on:
#   - Windows local dev  (c:/Users/swastik/Desktop/engineers/test_project)
#   - Linux Docker       (/app/test_project)
#   - Any cloud VM       (set MCP_WORKSPACE_ROOT in env)

import os

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_WORKSPACE = os.path.join(_REPO_ROOT, "test_project")
WORKSPACE_ROOT = os.getenv("MCP_WORKSPACE_ROOT", _DEFAULT_WORKSPACE)

terminal_config = {
    "terminal": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@mako10k/mcp-shell-server"],
        "env": {
            "MCP_SHELL_DEFAULT_WORKDIR": WORKSPACE_ROOT,
        },
    }
}
