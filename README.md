# Engineers — Autonomous Multi-Agent AI Software Engineering Platform

> Convert a single natural language prompt into a production-ready, full-stack application using an orchestrated team of 11 specialized AI agents.

[![CI — Syntax & Import Check](https://github.com/thisisswastik/Engineers/actions/workflows/ci.yml/badge.svg)](https://github.com/thisisswastik/Engineers/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-1.2+-orange)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Pro_%26_Flash-4285F4?logo=google)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## What It Does

You type:
```
Build me a food delivery platform with customer app, restaurant dashboard, and driver tracking.
```

The platform runs a full software engineering organization — CEO to DevOps — and delivers:

- ✅ Product Requirements Document (PRD)
- ✅ System Architecture & Tech Stack
- ✅ Database Schema & SQL Migrations
- ✅ Backend REST API Contracts
- ✅ Frontend Component Specifications
- ✅ QA Test Strategy
- ✅ Generated React + Node.js codebase
- ✅ `docker-compose.yml` for the generated app
- ✅ Security audit report
- ✅ Developer documentation

---

## Agent Architecture

```
                    ┌─────────────────────────────────────┐
  Natural Language  │  Phase 1: Planning  (Gemini Flash)  │
     Prompt ──────► │                                     │
                    │  CEO → Product Manager → Architect  │
                    │                  │                  │
                    │    ┌─────────────┼─────────────┐    │
                    │    ▼             ▼             ▼    │
                    │  Backend    Database       Frontend  │  ← Parallel fan-out
                    │    └─────────────┼─────────────┘    │
                    │                  ▼                  │
                    │            QA Engineer              │
                    └─────────────────┬───────────────────┘
                                      │
                              ⏸ HUMAN-IN-THE-LOOP
                          Review specs → Approve / Reject
                                      │
                    ┌─────────────────▼───────────────────┐
                    │  Phase 2: Execution  (Gemini Pro)   │
                    │                                     │
                    │  Coder Agent ◄──────────────────┐   │
                    │  (ReAct + MCP Tools)            │   │
                    │        │                        │   │
                    │        ▼                        │   │
                    │  DevOps → Security → Reviewer   │   │
                    │                  │              │   │
                    │         Critical Issues? ───────┘   │  ← Self-correction loop
                    │         (max 2 revisions)           │     (up to 2x)
                    │                  │                  │
                    │          Documentation Agent        │
                    └─────────────────────────────────────┘
                                       │
                              Generated Application
```

---

## Agent Roster

| Agent | File | Model | Output |
|:---|:---|:---|:---|
| CEO | [`agents/ceo.py`](agents/ceo.py) | Flash | Business plan, roadmap, team scope |
| Product Manager | [`agents/product_manager.py`](agents/product_manager.py) | Flash | PRD, user stories, constraints |
| Architect | [`agents/architect.py`](agents/architect.py) | Flash | Tech stack, microservices, DB schema, APIs |
| Backend Engineer | [`agents/backend.py`](agents/backend.py) | Flash | REST routes, controllers, auth design |
| Database Engineer | [`agents/database.py`](agents/database.py) | Flash | ER schema, migrations, indexes |
| Frontend Engineer | [`agents/frontend.py`](agents/frontend.py) | Flash | Component tree, routing, state design |
| QA Engineer | [`agents/qa.py`](agents/qa.py) | Flash | Test cases, coverage strategy, CI commands |
| **Coder** | [`agents/coder.py`](agents/coder.py) | **Pro** | Full-stack code via ReAct + MCP tools |
| DevOps | [`agents/devops.py`](agents/devops.py) | — | `docker-compose.yml`, setup scripts |
| Security Engineer | [`agents/security.py`](agents/security.py) | Flash | OWASP audit, threat model, RBAC review |
| Code Reviewer | [`agents/reviewer.py`](agents/reviewer.py) | Flash | Quality scores, criticisms, revision triggers |
| Documentation | [`agents/documentation.py`](agents/documentation.py) | Flash | Setup guides, API docs, deployment steps |

---

## Key Engineering Features

### Multi-Model Tier Routing
- `gemini-2.5-flash` — all planning, auditing, and specification agents (fast, cost-efficient)
- `gemini-2.5-pro` — Coder agent only (deep reasoning for code generation)

### Parallel Fan-Out / Fan-In
Backend, Database, and Frontend engineers run **concurrently** after the Architect finishes. LangGraph joins their outputs at QA, cutting total planning time by ~3x.

### Human-in-the-Loop (HITL) with Persistent Checkpointing
The graph pauses before code generation with `interrupt_before=["coder"]`. State is persisted to `logs/checkpoints.sqlite` via `AsyncSqliteSaver`. You can review specs, close the terminal, and resume the pipeline days later — state is never lost.

### Automated Self-Correction Loop
The Code Reviewer evaluates severity of issues. If `"high"` or `"critical"` criticisms are found and `revision_count < 2`, the graph routes back to the Coder automatically with structured feedback.

### MCP Tool Integration
The Coder agent has sandboxed access to three MCP servers:
- **Filesystem** — file creation, directory management
- **Shell/Terminal** — command execution, package installs, test runs  
- **SQLite** — direct database schema creation and querying

Paths are **environment-aware** — works on Windows, Linux, and inside Docker containers with zero code changes.

### OpenTelemetry Observability
Every LLM call, tool invocation, and agent step is traced via OpenInference instrumentation and logged silently to `logs/telemetry.log`. A persistent dashboard at `http://localhost:6006` visualizes traces.

### REST API + WebSockets
A deployment-grade FastAPI server (`api/api_v1.py`) exposes the entire pipeline as a web service with non-blocking endpoints and real-time WebSocket streaming of agent progress.

---

## Project Structure

```
engineers/
├── agents/                   # 12 specialized AI agent implementations
│   ├── ceo.py
│   ├── product_manager.py
│   ├── architect.py
│   ├── backend.py
│   ├── database.py
│   ├── frontend.py
│   ├── qa.py
│   ├── coder.py              # ReAct agent with MCP tool binding
│   ├── devops.py
│   ├── security.py
│   ├── reviewer.py
│   └── documentation.py
├── api/
│   └── api_v1.py             # FastAPI REST + WebSocket server
├── mcps/                     # MCP server configurations (env-aware paths)
│   ├── combined_tools.py     # Multi-model LLM + tool loader
│   ├── filesystem.py
│   ├── terminal.py
│   └── database.py
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI pipeline
├── logs/                     # Runtime: telemetry traces & SQLite checkpoints
│   └── .gitkeep
├── test_project/             # Runtime: generated application code lands here
│   └── .gitkeep
├── main_v2.py                # CLI entrypoint — runs full pipeline interactively
├── observabillity.py         # OpenTelemetry + OpenInference setup
├── launch_dashboard.py       # Telemetry dashboard server (port 6006)
├── launch_app.py             # Auto-discovers & launches generated web apps
├── Dockerfile                # Multi-stage production container
├── docker-compose.yml        # Full-stack container orchestration
├── pyproject.toml            # Dependency manifest (uv-managed)
└── .env.example              # Environment variable template
```

---

## Quick Start

### Prerequisites
- Python `3.11.*`
- Node.js `>=18` (for MCP npx servers)
- [Gemini API Key](https://aistudio.google.com/app/apikey)

### 1. Clone & Install

```bash
git clone https://github.com/thisisswastik/Engineers.git
cd Engineers

# Install uv (fast Python package manager)
pip install uv

# Install all dependencies
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run the Pipeline (CLI)

```bash
uv run main_v2.py
```

The pipeline will:
1. Run all planning agents (CEO → PM → Architect → parallel → QA)
2. **Pause** and display full specifications for your review
3. Prompt: `Do you approve the planning specs to start coding? (y/n)`
4. On `y` — Coder, DevOps, Security, Reviewer, and Documentation agents run
5. Generated application files appear in `test_project/`

### 4. Run via API (for frontends / integrations)

```bash
uv run python api/api_v1.py
```

API runs on `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

```bash
# 1. Start a pipeline session
curl -X POST http://localhost:8000/api/v1/pipeline/start \
  -H "Content-Type: application/json" \
  -d '{"user_request": "Build a task management app"}'

# Response: { "thread_id": "session-a1b2c3d4", "status": "PLANNING_STARTED" }

# 2. Poll for status
curl http://localhost:8000/api/v1/pipeline/session-a1b2c3d4/status

# 3. Approve when status is "awaiting_approval"
curl -X POST http://localhost:8000/api/v1/pipeline/approve \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "session-a1b2c3d4", "approved": true}'
```

### 5. Launch Generated App

```bash
python launch_app.py
# Opens generated web app at http://localhost:5173
```

### 6. View Telemetry Dashboard

```bash
python launch_dashboard.py
# Opens trace viewer at http://localhost:6006
```

---

## Docker Deployment

```bash
# Set your API key in shell
export GEMINI_API_KEY=your_key_here

# Build and run
docker-compose up --build
```

| Port | Service |
|:---|:---|
| `8000` | FastAPI REST API + WebSockets |
| `6006` | Observability Dashboard |
| `5173` | Generated Frontend App |

The `docker-compose.yml` handles all environment variable injection and mounts `./test_project` and `./logs` as persistent volumes.

---

## API Reference

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/healthz` | Container health check |
| `POST` | `/api/v1/pipeline/start` | Start planning phase, returns `thread_id` |
| `GET` | `/api/v1/pipeline/{id}/status` | Poll current phase & deliverables |
| `GET` | `/api/v1/pipeline/{id}/state` | Full raw LangGraph state snapshot |
| `POST` | `/api/v1/pipeline/approve` | Submit HITL approval decision |
| `GET` | `/api/v1/telemetry` | Last 15KB of OpenTelemetry traces |
| `WS` | `/ws/pipeline/{id}` | Real-time agent progress stream |

Full interactive documentation: `http://localhost:8000/docs`

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| Agent Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM Provider | Google Gemini 2.5 Pro & Flash |
| Tool Integration | [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) |
| State Persistence | SQLite via `AsyncSqliteSaver` |
| API Server | FastAPI + Uvicorn |
| Observability | OpenTelemetry + OpenInference |
| Container | Docker (multi-stage build) |
| Package Manager | [uv](https://github.com/astral-sh/uv) |
| CI/CD | GitHub Actions |

---

## Resume Bullet Points

> Orchestrated an 11-agent LangGraph state machine utilizing parallel fan-out execution phases and multi-tier model routing (Gemini 2.5 Flash & Pro) to convert natural language specs into production-ready full-stack applications.

> Implemented enterprise safety controls including a 2-revision self-correcting code review loop, Human-in-the-Loop state persistence (`AsyncSqliteSaver`) prior to code execution, and sandboxed MCP tool access for filesystem, terminal, and database operations.

> Exposed the agent pipeline as a deployment-grade FastAPI service with non-blocking REST endpoints, real-time WebSocket streaming, persistent SQLite session checkpointing, and a containerized Docker deployment with environment-aware cross-platform MCP path resolution.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
