# launch_app.py
import os
import sys
import subprocess
import time
import webbrowser

PROJECT_ROOT = os.path.abspath("./test_project/gourmetgo-platform")

def log(msg):
    print(f"\n[App Launcher] {msg}")

def discover_web_app():
    """Dynamically searches test_project/gourmetgo-platform for frontend/web apps."""
    if not os.path.exists(PROJECT_ROOT):
        return None, None

    search_dirs = [
        os.path.join(PROJECT_ROOT, "apps"),
        os.path.join(PROJECT_ROOT, "frontend"),
        PROJECT_ROOT
    ]

    for parent in search_dirs:
        if os.path.exists(parent):
            for entry in os.listdir(parent):
                full_path = os.path.join(parent, entry)
                if os.path.isdir(full_path):
                    # Check for package.json or index.html
                    if os.path.exists(os.path.join(full_path, "package.json")) or os.path.exists(os.path.join(full_path, "index.html")):
                        return entry, full_path

    return None, None

def main():
    log("="*60)
    log("  GOURMETGO PLATFORM - AUTOMATED APP LAUNCHER  ")
    log("="*60)

    app_name, app_path = discover_web_app()

    if not app_path:
        log("⚠️ NOTICE: Generated web application source files not found yet!")
        log("Please run 'uv run main_v2.py' and press 'y' at the Human-in-the-Loop prompt")
        log("to allow the Coder agent to generate the project files.\n")
        sys.exit(0)

    log(f"Found Web Application: '{app_name}' at {app_path}")
    log("Installing dependencies...")
    subprocess.run("npm install", shell=True, cwd=app_path)

    log("Starting web app server on http://localhost:5173...")
    process = subprocess.Popen("npm run dev", shell=True, cwd=app_path)

    log("Waiting 3 seconds for server startup...")
    time.sleep(3)

    log("Opening Customer Web App in Browser...")
    webbrowser.open("http://localhost:5173")

    log("\n" + "="*60)
    log("App running successfully on http://localhost:5173!")
    log("Press Ctrl+C to stop the server.")
    log("="*60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\nShutting down web app server...")
        process.terminate()
        log("Shutdown complete.")

if __name__ == "__main__":
    main()
