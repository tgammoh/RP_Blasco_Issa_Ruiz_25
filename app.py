import os
import sys
import time
import socket
import shutil
import threading
import subprocess
import http.server
import socketserver
from pathlib import Path

WORKSPACE_DIR = Path(__file__).parent.resolve()

def find_free_port(start_port=8000):
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start_port

def start_server(port, ready_event):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(WORKSPACE_DIR), **kwargs)

        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("127.0.0.1", port), QuietHandler) as httpd:
            ready_event.set()
            httpd.serve_forever()
    except Exception:
        ready_event.set()

def find_edge_path():
    # Common Windows locations for Microsoft Edge
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
        shutil.which("msedge"),
        shutil.which("chrome")
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None

def main():
    port = find_free_port(8000)
    ready_event = threading.Event()

    # Start local server
    server_thread = threading.Thread(target=start_server, args=(port, ready_event), daemon=True)
    server_thread.start()

    # Ensure server is fully bound before launching app
    ready_event.wait(timeout=3.0)

    target_url = f"http://localhost:{port}/index.html"
    app_exe = find_edge_path()
    profile_dir = os.path.expandvars(r"%LocalAppData%\ECHO7_Profile")
    os.makedirs(profile_dir, exist_ok=True)

    if app_exe:
        # Launch in isolated standalone Windows App Mode
        cmd = [
            app_exe,
            f"--app={target_url}",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=980,870",
            "--window-position=120,60"
        ]
        start_time = time.time()
        proc = subprocess.Popen(cmd)
        proc.wait()

        # If process returned immediately (< 2s) due to delegation, keep server alive
        if time.time() - start_time < 2:
            while True:
                time.sleep(1)
    else:
        # Fallback to default browser
        import webbrowser
        webbrowser.open(target_url)
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
