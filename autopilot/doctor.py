"""Environment self-test that needs no LLM key: launches the browser and reads a page."""
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from .agent import make_browser

PAGE = """<html><head><title>AutoPilot Self-Test</title></head><body>
<h1>Hello AutoPilot</h1><form><input name=q placeholder=search><button>Go</button></form>
</body></html>"""


class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


async def check() -> bool:
    srv = HTTPServer(("127.0.0.1", 0), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    b = make_browser(True)
    try:
        await b.start()
        await b.navigate_to(f"http://127.0.0.1:{srv.server_port}/")
        state = await b.get_browser_state_summary()
        n = len(state.dom_state.selector_map)
        print(f"title={state.title!r} interactive_elements={n}")
        return n >= 2
    finally:
        await b.kill()
        srv.shutdown()


def main() -> int:
    ok = asyncio.run(check())
    print("browser check:", "OK" if ok else "FAILED")
    return 0 if ok else 1
