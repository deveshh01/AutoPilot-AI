"""Minimal web UI: submit a task, get the result."""
import asyncio

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from .agent import run_task

load_dotenv()
app = Flask(__name__)

HTML = """<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
<title>AutoPilot AI</title>
<style>body{font:16px system-ui;max-width:720px;margin:2rem auto;padding:0 16px}
textarea{width:100%;height:110px;box-sizing:border-box}button{padding:.6rem 1.2rem;margin-top:8px}
pre{background:#f4f4f4;padding:12px;white-space:pre-wrap;border-radius:6px}</style>
<h1>AutoPilot AI</h1>
<textarea id=t placeholder="e.g. Go to wikipedia.org and tell me the first sentence about Python"></textarea><br>
<button id=b>Run</button><pre id=o>Idle.</pre>
<script>b.onclick=async()=>{b.disabled=true;o.textContent='Running... (can take a minute)';
try{const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({task:t.value})});const j=await r.json();
o.textContent=j.error?'Error: '+j.error:`success: ${j.success}\\nsteps: ${j.steps}\\n\\n${j.result}`}
catch(e){o.textContent='Error: '+e}b.disabled=false}</script>"""


@app.get("/")
def index():
    return HTML


@app.post("/api/run")
def api_run():
    task = (request.get_json(silent=True) or {}).get("task", "").strip()
    if not task:
        return jsonify(error="task is required"), 400
    try:
        r = asyncio.run(run_task(task))
    except RuntimeError as e:
        return jsonify(error=str(e)), 500
    return jsonify(success=r.success, result=r.result, steps=r.steps, urls=r.urls, errors=r.errors)
