#!/bin/bash
# Double-click me (macOS). Starts the map server and opens your browser.
cd "$(dirname "$0")"
open "http://127.0.0.1:8090" &
exec python3 serve.py 8090 --lan
