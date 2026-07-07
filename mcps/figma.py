# mcps/figma.py
import os
from dotenv import load_dotenv

load_dotenv()

figma_config = {
    "figma": {
        "transport": "stdio",
        "command": "npx",
        "args": [
            "-y", 
            "figma-developer-mcp", 
            "--stdio",
            f"--figma-api-key={os.getenv('FIGMA_CLIENT_SECRET')}"
        ]
    }
}
