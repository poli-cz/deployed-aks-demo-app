from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
import os
import time
import random
import socket

app = FastAPI()

START_TS = time.time()
REQ_COUNT = 0

MOODS = [
    "🦦 chill",
    "🐒 chaos monkey",
    "🦄 magical",
    "🐙 multi-armed (controller)",
    "🧠 reconciled",
    "🔥 on fire (but self-healing)",
]

JOKES = [
    "Why did the Kubernetes pod go to therapy? Too many restarts.",
    "Helm: 'It worked on my cluster.'",
    "GitOps: I don't always deploy, but when I do… it's from Git.",
    "Flux walks into a bar and reconciles the entire menu.",
]


def k8s_context():
    # Best shown if you add these env vars via Downward API in the Deployment
    return {
        "pod": os.getenv("POD_NAME") or socket.gethostname(),
        "namespace": os.getenv("POD_NAMESPACE", "unknown"),
        "node": os.getenv("NODE_NAME", "unknown"),
        "service_account": os.getenv("SERVICE_ACCOUNT", "unknown"),
    }


def app_context():
    return {
        "env": os.getenv("APP_ENV", "unknown"),
        "version": os.getenv("APP_VERSION", "dev"),
        "commit": os.getenv("GIT_SHA", "unknown"),
    }


@app.middleware("http")
async def counter_middleware(request: Request, call_next):
    global REQ_COUNT
    REQ_COUNT += 1
    return await call_next(request)


@app.get("/api", response_class=JSONResponse)
def api_root():
    return {
        "message": "Hello from AKS demo app 👋",
        **app_context(),
        **k8s_context(),
        "uptime_s": round(time.time() - START_TS, 1),
        "requests": REQ_COUNT,
        "mood": random.choice(MOODS),
    }


@app.get("/", response_class=HTMLResponse)
def root():
    uptime = round(time.time() - START_TS, 1)
    mood = random.choice(MOODS)
    ctx = {**app_context(), **k8s_context()}

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <title>AKS Demo App</title>
        <style>
          body {{ font-family: ui-sans-serif, system-ui, -apple-system; margin: 2rem; }}
          .card {{ max-width: 900px; padding: 1.25rem 1.5rem; border: 1px solid #ddd; border-radius: 16px; }}
          .row {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
          .pill {{ padding: .35rem .7rem; border-radius: 999px; background: #f2f2f2; display: inline-block; }}
          code {{ background: #f6f6f6; padding: .15rem .35rem; border-radius: 8px; }}
          a {{ text-decoration: none; }}
          .muted {{ color: #666; }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>🚀 AKS Demo App</h1>
          <p class="muted">GitOps-friendly, reconciliation-ready.</p>

          <div class="row">
            <span class="pill">Mood: <b>{mood}</b></span>
            <span class="pill">Uptime: <b>{uptime}s</b></span>
            <span class="pill">Requests: <b>{REQ_COUNT}</b></span>
          </div>

          <h3>Context</h3>
          <ul>
            <li>Env: <code>{ctx["env"]}</code></li>
            <li>Version: <code>{ctx["version"]}</code></li>
            <li>Commit: <code>{ctx["commit"]}</code></li>
            <li>Namespace: <code>{ctx["namespace"]}</code></li>
            <li>Pod: <code>{ctx["pod"]}</code></li>
            <li>Node: <code>{ctx["node"]}</code></li>
          </ul>

          <h3>Try</h3>
          <ul>
            <li><a href="/api">/api</a> (JSON)</li>
            <li><a href="/joke">/joke</a> (random joke)</li>
            <li><a href="/healthz">/healthz</a> and <a href="/readyz">/readyz</a></li>
            <li><a href="/burn?ms=250">/burn?ms=250</a> (tiny CPU burn for demos)</li>
          </ul>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(html)


@app.get("/joke", response_class=PlainTextResponse)
def joke():
    return random.choice(JOKES)


@app.get("/burn", response_class=JSONResponse)
def burn(ms: int = Query(200, ge=10, le=5000)):
    """
    Small demo endpoint: burns CPU for N milliseconds.
    Useful to demonstrate HPA / metrics / observability.
    """
    end = time.time() + (ms / 1000.0)
    x = 0
    while time.time() < end:
        x = (x * 13 + 7) % 1_000_003
    return {"burned_ms": ms, "result": x}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


@app.get("/info")
def info():
    return {"status": "This endpoint is the new endpoint"}
