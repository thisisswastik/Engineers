# agents/devops.py
import os
import json
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

class DevOpsState(TypedDict):
    user_request: str
    architecture: dict
    backend_design: dict
    frontend_design: dict
    devops_config: dict

def devops_node(state: DevOpsState):
    print("\n[DevOps Agent] Generating Docker Compose & Launch Scripts...")

    project_root = "./test_project/gourmetgo-platform"
    
    # Ensure project root exists if created by coder
    if os.path.exists(project_root):
        # 1. Generate docker-compose.yml
        docker_compose_content = """version: '3.8'

services:
  api-gateway:
    build:
      context: ./services/api-gateway
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=development

  auth-service:
    build:
      context: ./services/auth-service
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development

  customer-web-app:
    build:
      context: ./frontend/customer-web-app
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
"""
        docker_compose_path = os.path.join(project_root, "docker-compose.yml")
        with open(docker_compose_path, "w", encoding="utf-8") as f:
            f.write(docker_compose_content)

        # 2. Generate README_RUN.md
        readme_content = """# How to Run GourmetGo Platform

## Prerequisites
- Node.js (v18+)
- Docker & Docker Compose (optional for containerized run)

## Quick Start (Local Development)
Run the automated python launcher from the workspace root:
```bash
python launch_app.py
```

## Running via Docker Compose
```bash
docker-compose up --build
```
"""
        readme_path = os.path.join(project_root, "README_RUN.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

    return {
        "devops_config": {
            "docker_compose_created": True,
            "readme_created": True,
            "status": "DevOps configuration complete"
        }
    }
