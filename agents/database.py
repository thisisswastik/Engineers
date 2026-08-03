"""
database.py

Database Engineer Agent

Responsibilities
----------------
1. Design database schema in detail (tables, columns, types, keys, constraints).
2. Plan database indexing strategy for performance optimization.
3. Design database seeding (initial data).
4. Outline database migration plan/steps.
"""

import os
import json
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


# ==========================================================
# STATE
# ==========================================================

class DatabaseState(TypedDict):
    user_request: str
    business_plan: dict
    product_requirements: dict
    architecture: dict
    backend_design: dict
    database_design: dict


# ==========================================================
# MODEL
# ==========================================================

def _get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
    )


# ==========================================================
# DATABASE NODE
# ==========================================================

def database_node(state: DatabaseState):
    llm = _get_llm()

    prompt = f"""
You are a Principal Database Engineer.

You are given:

USER REQUEST
------------
{state["user_request"]}

CEO BUSINESS PLAN
-----------------
{json.dumps(state.get("business_plan", {}), indent=2)}

PRODUCT REQUIREMENTS
--------------------
{json.dumps(state.get("product_requirements", {}), indent=2)}

ARCHITECTURE
------------
{json.dumps(state.get("architecture", {}), indent=2)}

BACKEND DESIGN
--------------
{json.dumps(state.get("backend_design", {}), indent=2)}

Your job is NOT to write the application code, but to design a detailed Database Design Document.

Your responsibilities:

1. Specify database type and engine details.
2. Design the precise database schemas: define tables, fields/columns (with correct types, constraints like primary keys, foreign keys, not null, default values), and relationships.
3. Define indexing strategy: determine which columns should have indexes (B-Tree, Hash, etc.) to optimize query speed, especially on frequently searched or joined fields.
4. Design a data migration strategy (e.g. schema changes/versions, tools to use).
5. Specify seed data requirements (e.g. mock users, status lists, default values) for bootstrapping the system.

Return ONLY valid JSON.

Return EXACTLY this schema:

{{
    "database_design": {{
        "database_type": "e.g. PostgreSQL, SQLite, MySQL etc.",
        "tables": [
            {{
                "table_name": "users",
                "description": "Stores user registration and login credentials",
                "columns": [
                    {{
                        "name": "id",
                        "type": "UUID / INTEGER",
                        "constraints": ["PRIMARY KEY", "NOT NULL"],
                        "default_value": "uuid_generate_v4() / autoincrement",
                        "description": "Unique identifier for the user"
                    }}
                ],
                "foreign_keys": [
                    {{
                        "column": "role_id",
                        "references_table": "roles",
                        "references_column": "id",
                        "on_delete": "CASCADE"
                    }}
                ]
            }}
        ],
        "indexes": [
            {{
                "name": "idx_users_email",
                "table": "users",
                "columns": ["email"],
                "unique": true,
                "index_type": "BTREE"
            }}
        ],
        "migration_plan": {{
            "tool": "Alembic / Knex / Flyway etc.",
            "steps": [
                "Initialize migration repository",
                "Create initial tables schema migration",
                "Run initial migration scripts to create tables"
            ]
        }},
        "seed_data": [
            {{
                "table": "roles",
                "records": [
                    {{"id": 1, "name": "admin"}},
                    {{"id": 2, "name": "user"}}
                ]
            }}
        ]
    }}
}}

DO NOT add markdown.
DO NOT add explanation.
DO NOT wrap in ```json.
"""

    response = llm.invoke(prompt)
    text = response.content.strip()

    # Remove markdown code formatting if LLM still returns it
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    try:
        design = json.loads(text)
    except Exception as e:
        raise Exception(f"Database Agent returned invalid JSON. Error: {e} Text: {text}")

    return design


if __name__ == "__main__":
    graph = StateGraph(DatabaseState)
    graph.add_node("database_engineer", database_node)
    graph.set_entry_point("database_engineer")
    graph.add_edge("database_engineer", END)
    database_graph = graph.compile()
