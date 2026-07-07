# product manager agent 
'''
This agents job is to mimic the work of a product manager
'''

import os
from typing import TypedDict, List
import json
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()


# state 
class PMstate(TypedDict):
    business_plan: dict
    user_request: str
    product_requirements: dict
    
# initializing model 
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2
)

# Product Manager Node

def pm_node(state: PMstate):
    prompt = f"""
    You are a Product Manager.
    
    
    Client Request:
    {state['user_request']}
    
    CEO Plan:
    {state['business_plan']}
    
    Your job:
    - Elaborate product requirements
    - Define user stories
    - Specify features
    - List technical constraints
    - Produce a PRD (Product Requirements Document)
    
    Return ONLY valid JSON with structure:
    
    {{
    "prd":{{
        "features":[],
        "user_stories":[],
        "constraints":[],
        "success_metrics":[],
        "risks":[]
    }}
}}
"""

    response = llm.invoke(prompt)
    text = response.content.strip()

    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return {
            "product_requirements": json.loads(text),
            "next_agent": "solution_architect"
        }
    except:
        raise Exception(f"PM did not return valid JSON:\n\n{text}")

# Graph 
graph = StateGraph(PMstate)

graph.add_node("product_manager", pm_node)

graph.set_entry_point("product_manager")

graph.add_edge("product_manager", END)

pm_graph = graph.compile()


# main
if __name__ == "__main__":

    state = {
        "user_request": """
Build an AI Resume Analyzer.

The application should:
- Analyze resumes
- Score ATS compatibility
- Suggest improvements
- Recommend jobs
- Generate cover letters
""",

        "business_plan": {
            "project_name": "AI Resume Analyzer",
            "summary": "AI-powered resume analysis platform",
            "goals": [
                "Analyze resumes",
                "Improve ATS score",
                "Generate cover letters"
            ],
            "required_agents": [
                "Product Manager",
                "Architect",
                "Backend Engineer",
                "Frontend Engineer"
            ],
            "priority": "High",
            "estimated_complexity": "High"
        },

        "product_requirements": {}
    }

    result = pm_graph.invoke(state)

    print("\n========== PRODUCT REQUIREMENTS ==========\n")

    print(json.dumps(result["product_requirements"], indent=4))



    


