#!/usr/bin/env python3
"""Tiny static server WITH HTTP Range support (required by the PMTiles
offline basemap — plain `python3 -m http.server` ignores Range headers).
Usage:  python3 serve.py [port]      (default 8080)"""
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        rng = self.headers.get("Range")
        if not (rng and os.path.isfile(path)):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
        if not m:
            return super().send_head()
        size = os.path.getsize(path)
        start = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2)))
        end = min(int(m.group(2)), size - 1) if m.group(2) and m.group(1) else size - 1
        if start >= size:
            self.send_error(416, "Range Not Satisfiable")
            return None
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._range_left = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, "_range_left", None)
        if left is None:
            return super().copyfile(source, outputfile)
        while left > 0:
            chunk = source.read(min(65536, left))
            if not chunk:
                break
            outputfile.write(chunk)
            left -= len(chunk)
        self._range_left = None

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    host = "0.0.0.0" if "--lan" in sys.argv else "127.0.0.1"
    where = "all interfaces (reachable from other devices)" if host == "0.0.0.0" else "this machine only"
    print(f"Serving on http://{host}:{port} — {where}  (add --lan to allow other devices)")
    ThreadingHTTPServer((host, port), RangeHandler).serve_forever()
