from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import employees_router, projects_router, seats_router, dashboard_router, ai_router
import os

app = FastAPI(
    title="Ethara Seat Allocation & Project Mapping API",
    description="Backend API for managing seat allocations, project mappings, and utilization dashboards.",
    version="1.0.0"
)

# CORS — comma-separated origins in env var ALLOWED_ORIGINS
# e.g. "https://ethara.vercel.app,http://localhost:5173"
# Defaults to wildcard (*) if env var is not set (safe for dev/staging).
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if _raw_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=_raw_origins != "*",  # credentials require explicit origins, not wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(employees_router)
app.include_router(projects_router)
app.include_router(seats_router)
app.include_router(dashboard_router)
app.include_router(ai_router)

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

# Serve bundled frontend (only present in local docker-compose via Dockerfile.local)
# On Render, static/ doesn't exist and this block is skipped — frontend is on Vercel.
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="assets")

    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        return FileResponse(os.path.join(static_path, "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "Ethara Seat Allocation API is running."}
