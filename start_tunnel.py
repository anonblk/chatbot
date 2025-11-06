#!/usr/bin/env python3
from pyngrok import ngrok
import time

# Start ngrok tunnel
public_url = ngrok.connect(8501)
print(f"\n🌐 PUBLIC URL: {public_url}")
print(f"\n📱 Open this URL on your iPhone: {public_url}")
print("\nPress Ctrl+C to stop the tunnel...")

try:
    # Keep the tunnel alive
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down tunnel...")
    ngrok.kill()
