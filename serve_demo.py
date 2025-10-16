#!/usr/bin/env python3
import http.server
import socketserver
import os

# Change to the project directory
os.chdir('/root/tel-projcets/alrah-ai')

PORT = 8090

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Serving at http://91.109.114.158:{PORT}")
    print(f"Access the demo at: http://91.109.114.158:{PORT}/livekit_example.html")
    httpd.serve_forever()
