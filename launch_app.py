# launch_app.py
import os
import sys
import subprocess
import time
import webbrowser

PROJECT_ROOT = os.path.abspath("./test_project/gourmetgo-platform")

def log(msg):
    print(f"\n[App Launcher] {msg}")

def check_project_exists():
    if not os.path.exists(PROJECT_ROOT):
        log(f"Error: Project root '{PROJECT_ROOT}' not found! Run main_v2.py first.")
        sys.exit(1)

def run_service_npm_dev(service_dir, port):
    path = os.path.join(PROJECT_ROOT, service_dir)
    if not os.path.exists(path):
        log(f"Directory {path} not found. Skipping...")
        return None
    
    log(f"Installing dependencies in {service_dir}...")
    subprocess.run("npm install", shell=True, cwd=path)

    log(f"Starting {service_dir} on port {port}...")
    process = subprocess.Popen("npm run start:dev", shell=True, cwd=path)
    return process

def main():
    log("="*60)
    log("  GOURMETGO PLATFORM - AUTOMATED APP LAUNCHER  ")
    log("="*60)

    check_project_exists()

    frontend_path = os.path.join(PROJECT_ROOT, "frontend", "customer-web-app")
    auth_service_path = os.path.join(PROJECT_ROOT, "services", "auth-service")

    processes = []

    try:
        # 1. Start Backend Auth Service (if available)
        if os.path.exists(auth_service_path):
            log("Configuring Backend Auth Service...")
            p_backend = run_service_npm_dev("services/auth-service", 3000)
            if p_backend: 
                processes.append(p_backend)

        # 2. Start Customer Web App Frontend (if available)
        if os.path.exists(frontend_path):
            log("Configuring Frontend Customer Web App...")
            p_frontend = run_service_npm_dev("frontend/customer-web-app", 5173)
            if p_frontend: 
                processes.append(p_frontend)

        log("Waiting 5 seconds for servers to initialize...")
        time.sleep(5)

        # 3. Open Browser
        log("Opening Customer Web App in Browser...")
        webbrowser.open("http://localhost:5173")

        log("\n" + "="*60)
        log("App running successfully! Press Ctrl+C to stop all servers.")
        log("="*60)

        # Keep alive until user interrupts
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        log("\nShutting down all running servers...")
        for p in processes:
            p.terminate()
        log("Shutdown complete.")

if __name__ == "__main__":
    main()
