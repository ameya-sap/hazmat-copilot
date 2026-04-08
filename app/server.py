from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
from urllib.parse import urlparse, parse_qs

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        from app.ingest import ingest_files

        parsed_path = urlparse(self.path)
        if parsed_path.path == "/ingest":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Starting ingestion...\n")
            
            try:
                params = parse_qs(parsed_path.query)
                batch_size = int(params.get("batch_size", [os.environ.get("BATCH_SIZE", "10")])[0])
                self.wfile.write(f"Processing batch of {batch_size} files.\n".encode())
                ingest_files(batch_size=batch_size)
                self.wfile.write(b"Ingestion completed successfully.\n")
            except Exception as e:
                self.wfile.write(f"Ingestion failed: {e}\n".encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        # Health check
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run():
    port = int(os.environ.get("PORT", "8080"))
    server_address = ('', port)
    httpd = HTTPServer(server_address, Handler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
