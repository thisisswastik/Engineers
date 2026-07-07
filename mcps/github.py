# mcps/github.py
import os
from dotenv import load_dotenv

load_dotenv()

github_config = {
    "github": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")
        }
    }
}
