import http.server
import os
import socket
import socketserver
import threading
import time
import webbrowser
from pathlib import Path

# Ensure we always serve from the exact folder where this script is located
BASE_DIR = Path(__file__).resolve().parent

def find_free_port(start_port=8000):
    """Find a guaranteed available port starting from start_port."""
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start_port

def run_server(port, ready_event):
    os.chdir(BASE_DIR)

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(BASE_DIR), **kwargs)

        def log_message(self, format, *args):
            pass  # Keep console output clean

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(('127.0.0.1', port), QuietHandler) as httpd:
            print(f"Serving files from: {BASE_DIR}")
            ready_event.set()
            httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")
        ready_event.set()

def main():
    port = find_free_port(8000)
    ready_event = threading.Event()

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, args=(port, ready_event), daemon=True)
    server_thread.start()

    # Wait until server is bound before launching browser
    ready_event.wait(timeout=3.0)

    url = f"http://localhost:{port}/index.html"
    print(f"Opening {url} in your default browser...")
    opened = webbrowser.open(url)
    if not opened:
        # Fallback for Windows shell launch
        os.system(f'start "" "{url}"')

    print("\n" + "=" * 55)
    print("  E.C.H.O.-7 Voice Terminal is ONLINE!")
    print(f"  URL: {url}")
    print("  Voice recognition requires http://localhost")
    print("  Keep this window open. Press Ctrl+C to shut down.")
    print("=" * 55 + "\n")

    try:
        while server_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nShutting down E.C.H.O.-7 server. Goodbye!")

if __name__ == "__main__":
    main()
