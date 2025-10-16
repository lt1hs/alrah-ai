#!/usr/bin/env python3
import http.server
import ssl
import os

# Change to project directory
os.chdir('/root/tel-projcets/alrah-ai')

PORT = 8443

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

# Create server
httpd = http.server.HTTPServer(('0.0.0.0', PORT), CORSHTTPRequestHandler)

# Create SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')

# Wrap socket with SSL
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"HTTPS server running at https://91.109.114.158:{PORT}")
print("Note: You'll need to accept the self-signed certificate warning")

httpd.serve_forever()
