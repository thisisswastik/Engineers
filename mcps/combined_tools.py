# mcps/combined_tools.py
import os 
import sys
import shutil
import asyncio 
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from filesystem import filesystem_config
from terminal import terminal_config
from database import database_config

load_dotenv()

async def get_combined_llm_with_tools():
    # Core essential development tools for Coder agent
    combined_configs = {
        **filesystem_config,
        **terminal_config,
        **database_config
    }

    # Normalize 'npx' executable command path on Windows (win32 requires npx.cmd)
    if sys.platform == "win32":
        npx_path = shutil.which("npx") or "npx.cmd"
        for server_name, cfg in combined_configs.items():
            if cfg.get("command") == "npx":
                cfg["command"] = npx_path

    print("\n[MCP Loader] Connecting to core MCP servers (Filesystem, Terminal, Database)...")
    client = MultiServerMCPClient(combined_configs)
    tools = await client.get_tools()
    print(f"[MCP Loader] Successfully loaded {len(tools)} tools!")

    api_key = os.getenv("GEMINI_API_KEY")

    # Fast Model: Gemini 2.5 Flash for planning, specs, & auditing
    flash_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2
    )

    # Reasoning Model: Gemini 2.5 Pro for deep code generation
    pro_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=api_key,
        temperature=0.1
    )

    flash_with_tools = flash_llm.bind_tools(tools)
    pro_with_tools = pro_llm.bind_tools(tools)

    return pro_with_tools, flash_with_tools, tools

async def main():
    pro_llm, flash_llm, tools = await get_combined_llm_with_tools()

if __name__ == "__main__":
    asyncio.run(main())
