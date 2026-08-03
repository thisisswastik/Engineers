# api/api_v1.py
"""
Deployment-Grade REST & WebSockets API for the Autonomous Multi-Agent AI Software Engineering Platform.

Fixes applied vs previous version:
- build_pipeline() now receives a persistent AsyncSqliteSaver checkpointer (fixes startup crash).
- Uses FastAPI lifespan() context manager instead of deprecated @app.on_event("startup").
- CORS: allow_credentials removed when allow_origins=["*"] to satisfy CORS spec.
- start_pipeline() returns immediately with thread_id; planning executes as a background task.
- Added GET /api/v1/pipeline/{thread_id}/status polling endpoint.
- backend_coder_node is now also called alongside frontend_coder_node (see main_v2.py).
"""

import os
import sys
import uuid
import json
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

# Add workspace root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from main_v2 import build_pipeline, PipelineState
from observabillity import setup_observability

load_dotenv()

DB_PATH = os.path.abspath("./logs/checkpoints.sqlite")

# Global graph handle (set during lifespan startup)
compiled_graph = None

# Per-thread status tracking for polling endpoint
thread_status: Dict[str, Dict[str, Any]] = {}

# Active WebSocket connections keyed by thread_id
active_websockets: Dict[str, List[WebSocket]] = {}


# ==============================================================================
# Lifespan Context Manager (replaces deprecated @app.on_event)
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once on startup and once on shutdown."""
    global compiled_graph

    os.makedirs("./logs", exist_ok=True)

    print("\n[API Startup] Initializing OpenTelemetry Tracing...")
    setup_observability()

    print("[API Startup] Opening persistent SQLite checkpointer...")
    # We open the checkpointer here and keep it alive for the process lifetime.
    # The AsyncSqliteSaver context manager will close it cleanly on shutdown.
    async with AsyncSqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        print("[API Startup] Compiling LangGraph Multi-Agent Pipeline...")
        compiled_graph = await build_pipeline(checkpointer)
        print("[API Startup] Platform API is fully compiled and ready to serve requests!\n")
        yield  # ← server runs while we are inside this yield

    # Cleanup on shutdown
    compiled_graph = None
    print("\n[API Shutdown] Checkpointer closed. Server stopped cleanly.")


# ==============================================================================
# FastAPI Application
# ==============================================================================
app = FastAPI(
    title="Autonomous AI Software Engineering Platform API",
    version="1.0.0",
    description="Enterprise API powering multi-agent software development workflows, HITL checkpoints, and real-time streaming.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — wildcard origin is fine for dev/demo. Do NOT combine with allow_credentials=True.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to specific domains in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Pydantic Schemas
# ==============================================================================
class StartPipelineRequest(BaseModel):
    user_request: str = Field(
        ...,
        example="Build a food delivery application with customer web app, restaurant dashboard, and driver app.",
        description="Natural language project specification for the AI Engineering Organization.",
    )

class ApprovePipelineRequest(BaseModel):
    thread_id: str = Field(..., example="session-a1b2c3d4", description="Unique session thread ID.")
    approved: bool = Field(..., example=True, description="Human approval decision to resume code generation.")


# ==============================================================================
# Helper: broadcast a message to all WebSocket clients watching a thread
# ==============================================================================
async def _broadcast(thread_id: str, payload: dict):
    if thread_id not in active_websockets:
        return
    dead = []
    msg = json.dumps(payload)
    for ws in active_websockets[thread_id]:
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        active_websockets[thread_id].remove(ws)


# ==============================================================================
# Health & Telemetry Endpoints
# ==============================================================================
@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Kubernetes / Cloud Container Healthcheck. Returns 503 until graph is compiled."""
    if compiled_graph is None:
        raise HTTPException(status_code=503, detail="Pipeline graph is still initialising.")
    return {"status": "healthy", "service": "engineers-platform-api", "version": "1.0.0"}


@app.get("/api/v1/telemetry", tags=["Observability"])
async def get_telemetry_logs():
    """Returns the last 15 KB of OpenTelemetry execution traces."""
    log_path = os.path.abspath("./logs/telemetry.log")
    if not os.path.exists(log_path):
        return PlainTextResponse("No telemetry records available yet.")
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()[-15000:]
    return PlainTextResponse(content)


# ==============================================================================
# Pipeline Endpoints
# ==============================================================================
@app.post(
    "/api/v1/pipeline/start",
    response_model=Dict[str, Any],
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Pipeline"],
)
async def start_pipeline(req: StartPipelineRequest, background_tasks: BackgroundTasks):
    """
    Kicks off the Planning Phase asynchronously (CEO → PM → Architect → parallel → QA).
    Returns immediately with a thread_id. Poll GET /api/v1/pipeline/{thread_id}/status
    to know when planning is done and the HITL checkpoint has been reached.
    """
    thread_id = f"session-{uuid.uuid4().hex[:8]}"
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 50,
    }

    initial_state: PipelineState = {
        "user_request": req.user_request,
        "business_plan": {},
        "agents_required": [],
        "product_requirements": {},
        "architecture": {},
        "backend_design": {},
        "database_design": {},
        "frontend_design": {},
        "qa_plan": {},
        "coder_logs": [],
        "security_report": {},
        "devops_config": {},
        "review_feedback": {},
        "documentation_docs": {},
        "revision_count": 0,
        "feedback_history": [],
        "approved_by_human": False,
    }

    # Mark thread as running
    thread_status[thread_id] = {"phase": "planning", "status": "running", "nodes_completed": []}

    async def run_planning_phase():
        try:
            async for event in compiled_graph.astream(initial_state, config, stream_mode="updates"):
                for node_name, _ in event.items():
                    thread_status[thread_id]["nodes_completed"].append(node_name)
                    await _broadcast(thread_id, {"event": "node_finished", "node": node_name.upper()})

            # Planning complete — now paused at HITL breakpoint before 'coder'
            state_snapshot = await compiled_graph.aget_state(config)
            thread_status[thread_id]["status"] = "awaiting_approval"
            thread_status[thread_id]["planning_deliverables"] = {
                "product_requirements": state_snapshot.values.get("product_requirements", {}),
                "architecture":         state_snapshot.values.get("architecture", {}),
                "database_design":      state_snapshot.values.get("database_design", {}),
                "backend_design":       state_snapshot.values.get("backend_design", {}),
                "frontend_design":      state_snapshot.values.get("frontend_design", {}),
                "qa_plan":              state_snapshot.values.get("qa_plan", {}),
            }
            await _broadcast(thread_id, {"event": "planning_complete", "thread_id": thread_id})
        except Exception as e:
            thread_status[thread_id]["status"] = "error"
            thread_status[thread_id]["error"] = str(e)
            await _broadcast(thread_id, {"event": "error", "message": str(e)})

    background_tasks.add_task(run_planning_phase)

    return {
        "status": "PLANNING_STARTED",
        "thread_id": thread_id,
        "message": "Planning phase launched. Connect to /ws/pipeline/{thread_id} for live updates or poll /api/v1/pipeline/{thread_id}/status.",
    }


@app.get("/api/v1/pipeline/{thread_id}/status", tags=["Pipeline"])
async def get_pipeline_status(thread_id: str):
    """
    Polls current pipeline status for a thread.
    Returns phase, status, nodes completed so far, and planning deliverables once available.
    """
    if thread_id not in thread_status:
        raise HTTPException(status_code=404, detail=f"No pipeline found for thread_id '{thread_id}'")
    return {"thread_id": thread_id, **thread_status[thread_id]}


@app.get("/api/v1/pipeline/{thread_id}/state", tags=["Pipeline"])
async def get_pipeline_state(thread_id: str):
    """Fetches the full raw LangGraph state snapshot for a thread (for debugging)."""
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = await compiled_graph.aget_state(config)
    if not state_snapshot.values:
        raise HTTPException(status_code=404, detail=f"No state found for thread_id '{thread_id}'")
    return {
        "thread_id": thread_id,
        "next_nodes": state_snapshot.next,
        "state_values": state_snapshot.values,
    }


@app.post("/api/v1/pipeline/approve", tags=["Pipeline"])
async def approve_pipeline(req: ApprovePipelineRequest, background_tasks: BackgroundTasks):
    """
    Sends human approval (approved=True/False) to resume or abort an HITL-paused thread.
    If approved, Phase 2 (Coder → DevOps → Security → Reviewer → Documentation) starts in the background.
    """
    if thread_id_status := thread_status.get(req.thread_id):
        if thread_id_status.get("status") != "awaiting_approval":
            raise HTTPException(
                status_code=400,
                detail=f"Thread '{req.thread_id}' is not paused at HITL (current status: {thread_id_status.get('status')}).",
            )
    else:
        raise HTTPException(status_code=404, detail=f"No pipeline found for thread_id '{req.thread_id}'")

    if not req.approved:
        thread_status[req.thread_id]["status"] = "aborted"
        return {
            "status": "ABORTED_BY_HUMAN",
            "thread_id": req.thread_id,
            "message": "Human rejected planning specifications. Pipeline terminated.",
        }

    config = {
        "configurable": {"thread_id": req.thread_id},
        "recursion_limit": 50,
    }
    thread_status[req.thread_id]["status"] = "generating_code"
    thread_status[req.thread_id]["phase"] = "coding"

    async def run_coding_phase():
        try:
            async for event in compiled_graph.astream(None, config, stream_mode="updates"):
                for node_name, _ in event.items():
                    thread_status[req.thread_id]["nodes_completed"].append(node_name)
                    await _broadcast(req.thread_id, {"event": "node_finished", "node": node_name.upper()})

            thread_status[req.thread_id]["status"] = "complete"
            await _broadcast(req.thread_id, {"event": "pipeline_complete", "thread_id": req.thread_id})
        except Exception as e:
            thread_status[req.thread_id]["status"] = "error"
            thread_status[req.thread_id]["error"] = str(e)
            await _broadcast(req.thread_id, {"event": "error", "message": str(e)})

    background_tasks.add_task(run_coding_phase)

    return {
        "status": "RESUMED_CODE_GENERATION",
        "thread_id": req.thread_id,
        "message": "Approved. Coder, DevOps, Security, and Reviewer agents launched. Poll /status or watch /ws for progress.",
    }


# ==============================================================================
# Real-Time WebSocket Streaming
# ==============================================================================
@app.websocket("/ws/pipeline/{thread_id}")
async def websocket_pipeline_stream(websocket: WebSocket, thread_id: str):
    """
    Bidirectional WebSocket. Streams node completion events and errors in real time.
    The client can connect before or after calling /start — it will receive all future events.
    """
    await websocket.accept()
    active_websockets.setdefault(thread_id, []).append(websocket)

    try:
        await websocket.send_text(json.dumps({
            "event": "connected",
            "thread_id": thread_id,
            "message": "Real-time streaming channel established.",
        }))
        # Keep the connection open; server pushes events, client can send pings
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({"event": "pong", "echo": data}))
    except WebSocketDisconnect:
        if thread_id in active_websockets:
            try:
                active_websockets[thread_id].remove(websocket)
            except ValueError:
                pass
            if not active_websockets[thread_id]:
                del active_websockets[thread_id]


# ==============================================================================
# CLI entrypoint
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.api_v1:app", host="0.0.0.0", port=8000, reload=False)
