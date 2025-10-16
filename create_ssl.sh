#!/bin/bash

# Create self-signed SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=91.109.114.158"

echo "SSL certificate created!"
echo "Files: cert.pem and key.pem"
