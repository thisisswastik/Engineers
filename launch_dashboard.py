# launch_dashboard.py
import os
import json
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

PORT = 6006
LOG_FILE = os.path.abspath("./logs/telemetry.log")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Agentic Observability Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid #334155; }
        h1 { margin: 0; color: #38bdf8; font-size: 24px; }
        .badge { background: #0284c7; color: white; padding: 4px 12px; borderRadius: 12px; font-weight: bold; font-size: 12px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; }
        .card h2 { margin-top: 0; color: #f1f5f9; font-size: 18px; border-bottom: 1px solid #334155; padding-bottom: 10px; }
        pre { background: #090d16; padding: 15px; border-radius: 6px; color: #a5f3fc; overflow-x: auto; font-size: 13px; max-height: 400px; }
        .span-item { padding: 10px; border-bottom: 1px solid #334155; }
        .span-item:last-child { border-bottom: none; }
        .agent-name { color: #fbbf24; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AI Engineering Organization — Live Telemetry Dashboard</h1>
        <span class="badge">Status: Active (Port 6006)</span>
    </div>

    <div class="grid">
        <div class="card">
            <h2>📊 Real-Time Execution Traces</h2>
            <div id="spans">Loading telemetry traces...</div>
        </div>

        <div class="card">
            <h2>📜 Telemetry Log File Stream</h2>
            <pre id="raw-log">Reading logs/telemetry.log...</pre>
        </div>
    </div>

    <script>
        async function fetchTelemetry() {
            try {
                const res = await fetch('/api/telemetry');
                const data = await res.text();
                document.getElementById('raw-log').innerText = data || "No telemetry spans recorded yet. Run main_v2.py to generate execution traces.";
            } catch (e) {
                console.error(e);
            }
        }
        setInterval(fetchTelemetry, 3000);
        fetchTelemetry();
    </script>
</body>
</html>
"""

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif self.path == '/api/telemetry':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            content = ""
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()[-10000:]  # Last 10k chars
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP access logging

def run_server():
    server = HTTPServer(('localhost', PORT), DashboardHandler)
    print(f"\n[Observability Dashboard] Running continuously at http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")
    print(f"[Observability Dashboard] Server started! Keep this window open or press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Observability Dashboard server.")
