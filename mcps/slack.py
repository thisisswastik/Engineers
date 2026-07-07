# mcps/slack.py
import os
from dotenv import load_dotenv

load_dotenv()

slack_config = {
    "slack": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "env": {
            "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
            "SLACK_TEAM_ID": os.getenv("SLACK_TEAM_ID")
        }
    }
}
