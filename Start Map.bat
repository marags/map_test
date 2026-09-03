@echo off
rem Double-click me (Windows, needs Python installed from python.org).
cd /d "%~dp0"
start "" "http://127.0.0.1:8090"
py serve.py 8090 --lan 2>nul || python serve.py 8090 --lan
