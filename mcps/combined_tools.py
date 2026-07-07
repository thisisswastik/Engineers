import os 
import sys
import asyncio 
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI

# Add the directory containing this script to the search path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 1. Import adjacent config dictionaries directly (without "mcps.")
# pyrefly: ignore [missing-import]
from browser import browser_config
# pyrefly: ignore [missing-import]
from figma import figma_config
# pyrefly: ignore [missing-import]
from slack import slack_config
# pyrefly: ignore [missing-import]
from docker import docker_config
# pyrefly: ignore [missing-import]
from filesystem import filesystem_config
# pyrefly: ignore [missing-import]
from github import github_config
# pyrefly: ignore [missing-import]
from terminal import terminal_config
# pyrefly: ignore [missing-import]
from database import database_config

load_dotenv()

async def get_combined_llm_with_tools():
    # 2. Merge all configurations into a single dictionary
    combined_configs = {
        **browser_config,
        **figma_config,
        **slack_config,
        **docker_config,
        **filesystem_config,
        **github_config,
        **terminal_config,
        **database_config
    }

    # 3. Pass the single merged dictionary to the client
    client = MultiServerMCPClient(combined_configs)
    
    print("Connecting to all MCP servers...")
    tools = await client.get_tools()
    print(f"Successfully loaded {len(tools)} tools in total across all servers!")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    # Bind tools 
    llm_with_tools = llm.bind_tools(tools)
    print("Successfully bound tools to LLM!")

    return llm_with_tools, tools

async def main():
    llm_with_tools, tools = await get_combined_llm_with_tools()

if __name__ == "__main__":
    asyncio.run(main())
