#!/usr/bin/env python3
import http.server
import socketserver
import os

ROOT_DIR = "/Users/frederickamina/Documents/Projects/SYNAPSE/unity-tcg-engine"
REPORT_PATH = os.path.join(ROOT_DIR, "Datasets", "osascript_3d_game_e2e_report.json")
PLAYABLE_REL_URL = "/WebPlayable/cardfront_cradle_of_echoes_playable.html"

class PlaytestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        if self.path in ("/", "/play", "/index.html"):
            self.send_response(302)
            self.send_header("Location", PLAYABLE_REL_URL)
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/__osascript_report__"):
            from urllib.parse import urlparse, parse_qs
            name = parse_qs(urlparse(self.path).query).get("name", [""])[0]
            out_path = REPORT_PATH if not name.isalnum() else os.path.join(ROOT_DIR, "Datasets", f"osascript_{name}_report.json")
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(body)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"saved":true}')
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    # Bind to 0.0.0.0 so both 127.0.0.1 (local harness) and LAN MacBooks/iPads (192.168.86.125) can connect
    with http.server.ThreadingHTTPServer(("0.0.0.0", 8096), PlaytestHandler) as httpd:
        httpd.serve_forever()
