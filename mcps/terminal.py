# mcps/terminal.py
terminal_config = {
    "terminal": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@mako10k/mcp-shell-server"],
        "env": {
            "MCP_SHELL_DEFAULT_WORKDIR": "c:/Users/swastik/Desktop/engineers/test_project"
        }
    }
}
