# launch_dashboard.py
import os
import re
import json
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

PORT = 6006
LOG_FILE = os.path.abspath("./logs/telemetry.log")

# Gemini 2.5 Flash Pricing (per 1,000,000 tokens)
INPUT_COST_PER_M = 0.075
OUTPUT_COST_PER_M = 0.30

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Engineering Org — Token & Cost Observability</title>
    <style>
        :root {
            --bg: #0b0f19;
            --card-bg: #151c2c;
            --border: #232d42;
            --accent: #38bdf8;
            --green: #4ade80;
            --yellow: #fbbf24;
            --purple: #c084fc;
            --text: #f8fafc;
            --subtext: #94a3b8;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
        h1 { margin: 0; font-size: 24px; color: var(--accent); display: flex; align-items: center; gap: 10px; }
        .badge { background: #0284c7; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 13px; }
        
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }
        .kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; text-align: left; }
        .kpi-title { font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--subtext); font-weight: 600; }
        .kpi-value { font-size: 28px; font-weight: 700; margin-top: 8px; color: var(--text); }
        .kpi-sub { font-size: 12px; color: var(--subtext); margin-top: 4px; }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
        .card h2 { margin-top: 0; color: var(--text); font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
        
        pre { background: #070a11; padding: 16px; border-radius: 8px; color: #a5f3fc; overflow-x: auto; font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; max-height: 420px; line-height: 1.5; border: 1px solid var(--border); }
        
        .agent-list { display: flex; flex-direction: column; gap: 10px; max-height: 420px; overflow-y: auto; }
        .agent-item { background: #0f172a; padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .agent-name { font-weight: 600; color: var(--yellow); text-transform: uppercase; font-size: 13px; }
        .agent-stats { font-size: 12px; color: var(--subtext); }
        .agent-badge { background: #1e293b; color: var(--accent); padding: 4px 10px; border-radius: 6px; font-weight: bold; border: 1px solid #334155; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AI Engineering Organization — Observability & Token Analytics</h1>
        <span class="badge">Live Monitoring (Port 6006)</span>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Total Tokens</div>
            <div class="kpi-value" id="kpi-tokens">0</div>
            <div class="kpi-sub" id="kpi-tokens-sub">Prompt: 0 | Completion: 0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Estimated LLM Cost</div>
            <div class="kpi-value" style="color: var(--green);" id="kpi-cost">$0.0000</div>
            <div class="kpi-sub">Gemini 2.5 Flash Rates</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Total Spans Captured</div>
            <div class="kpi-value" style="color: var(--purple);" id="kpi-spans">0</div>
            <div class="kpi-sub">OpenTelemetry Instrumentation</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Agent Telemetry Status</div>
            <div class="kpi-value" style="color: var(--accent);" id="kpi-status">ACTIVE</div>
            <div class="kpi-sub">Logs: ./logs/telemetry.log</div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>🤖 Agent Execution Metrics</h2>
            <div class="agent-list" id="agent-breakdown">
                <div class="agent-item">
                    <span class="agent-name">Loading Telemetry Spans...</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📜 Real-Time OTEL Trace Log Stream</h2>
            <pre id="raw-log">Loading logs/telemetry.log...</pre>
        </div>
    </div>

    <script>
        async function updateDashboard() {
            try {
                const res = await fetch('/api/analytics');
                const data = await res.json();

                document.getElementById('kpi-tokens').innerText = data.total_tokens.toLocaleString();
                document.getElementById('kpi-tokens-sub').innerText = `Prompt: ${data.prompt_tokens.toLocaleString()} | Completion: ${data.completion_tokens.toLocaleString()}`;
                document.getElementById('kpi-cost').innerText = `$${data.estimated_cost.toFixed(4)}`;
                document.getElementById('kpi-spans').innerText = data.total_spans.toLocaleString();

                const agentContainer = document.getElementById('agent-breakdown');
                if (data.agents && Object.keys(data.agents).length > 0) {
                    agentContainer.innerHTML = Object.entries(data.agents).map(([agent, count]) => `
                        <div class="agent-item">
                            <span class="agent-name">🤖 ${agent.replace(/_/g, ' ')}</span>
                            <span class="agent-badge">${count} Step Execution${count > 1 ? 's' : ''}</span>
                        </div>
                    `).join('');
                } else {
                    agentContainer.innerHTML = `<div class="agent-item"><span class="agent-name">Waiting for Agent Execution...</span></div>`;
                }

                const logRes = await fetch('/api/telemetry');
                const logText = await logRes.text();
                document.getElementById('raw-log').innerText = logText || "No telemetry spans recorded yet. Run main_v2.py to generate traces.";
            } catch (e) {
                console.error(e);
            }
        }
        setInterval(updateDashboard, 3000);
        updateDashboard();
    </script>
</body>
</html>
"""

def parse_telemetry_metrics():
    """Parses `./logs/telemetry.log` for OpenTelemetry spans, tokens, and agent execution metrics."""
    prompt_tokens = 0
    completion_tokens = 0
    total_spans = 0
    agent_counts = {}

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Count spans by trace_id or JSON span object starts
                total_spans = content.count('"trace_id":')

                # Regex for prompt tokens
                prompt_matches = re.findall(r'"(?:llm\.token_count\.prompt|input_tokens)":\s*(\d+)', content)
                prompt_tokens = sum(int(m) for m in prompt_matches)

                # Regex for completion tokens
                completion_matches = re.findall(r'"(?:llm\.token_count\.completion|output_tokens)":\s*(\d+)', content)
                completion_tokens = sum(int(m) for m in completion_matches)

                # Extract agents executed
                nodes = re.findall(r'"langgraph_node":\s*"([^"]+)"', content)
                for node in nodes:
                    if node != "__start__":
                        agent_counts[node] = agent_counts.get(node, 0) + 1

        except Exception as e:
            print(f"[Telemetry Parser Error] {e}")

    total_tokens = prompt_tokens + completion_tokens
    estimated_cost = (prompt_tokens / 1_000_000 * INPUT_COST_PER_M) + (completion_tokens / 1_000_000 * OUTPUT_COST_PER_M)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost": estimated_cost,
        "total_spans": total_spans,
        "agents": agent_counts
    }

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif self.path == '/api/analytics':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            metrics = parse_telemetry_metrics()
            self.wfile.write(json.dumps(metrics).encode('utf-8'))
        elif self.path == '/api/telemetry':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            content = ""
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()[-12000:]
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(('localhost', PORT), DashboardHandler)
    print(f"\n[Observability Dashboard] Running at http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")
    print(f"[Observability Dashboard] Server started on http://localhost:{PORT}! Keep window open or press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Dashboard server.")
