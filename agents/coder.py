from typing import TypedDict, List
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

class CoderState(TypedDict):
    user_request: str
    architecture: str
    database_design: str
    backend_design: str
    frontend_design: str
    coder_logs: List[str]

async def coder_node(state: CoderState, llm, tools):
    # initializing the ReAct agent with access to the LLM and filesystem/terminal tools
    agent =  create_react_agent(llm,tools)

    # forumulating the instruction propmpt 
    prompt = f"""
You are a Senior Software Developer Agent.
Your task is to implement the code files according to the architecture, database design, and backend/frontend design plans.
SYSTEM ARCHITECTURE PLAN:
{state['architecture']}
DATABASE DESIGN:
{state.get('database_design', '')}
BACKEND DESIGN:
{state['backend_design']}
FRONTEND DESIGN:
{state['frontend_design']}
INSTRUCTIONS:
1. Use your filesystem tools (`write_file`, `create_directory`) to create the project files.
2. Put all files inside your workspace root.
3. Write clean, complete code files (do not use placeholders like // TODO: implement later).
4. Run `pytest` or compiler checks via the terminal tools to verify the code works.
When you are completely finished writing and verifying the files, output a summary of files created and stop.
"""
    # 3. Invoke the ReAct agent. It will run in a loop calling tools automatically.
    print("\n[Coder Node] Starting file generation...")
    result = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
    
    # Return the final completion messages/logs
    final_response = result["messages"][-1].content
    return {"coder_logs": [final_response]}