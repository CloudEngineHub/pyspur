from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from ..nodes.registry import NodeRegistry

NodeRegistry.discover_nodes()

from ..integrations.google.auth import router as google_auth_router
from .dataset_management import router as dataset_management_router
from .evals_management import router as evals_management_router
from .file_management import router as file_management_router
from .key_management import router as key_management_router
from .node_management import router as node_management_router
from .openai_compatible_api import router as openai_compatible_api_router
from .output_file_management import router as output_file_management_router
from .rag_management import router as rag_management_router
from .run_management import router as run_management_router
from .template_management import router as template_management_router
from .workflow_management import router as workflow_management_router
from .workflow_run import router as workflow_run_router

load_dotenv()


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a sub-application for API routes
api_app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    title="PySpur API",
    version="1.0.0",
)
api_app.include_router(node_management_router, prefix="/node")
api_app.include_router(workflow_management_router, prefix="/wf")
api_app.include_router(workflow_run_router, prefix="/wf")
api_app.include_router(dataset_management_router, prefix="/ds")
api_app.include_router(run_management_router, prefix="/run")
api_app.include_router(output_file_management_router, prefix="/of")
api_app.include_router(key_management_router, prefix="/env-mgmt")
api_app.include_router(template_management_router, prefix="/templates")
api_app.include_router(openai_compatible_api_router, prefix="/api")
api_app.include_router(evals_management_router, prefix="/evals")
api_app.include_router(google_auth_router, prefix="/google")
api_app.include_router(rag_management_router, prefix="/rag")
api_app.include_router(file_management_router, prefix="/files")

# Mount the API routes under /api
app.mount("/api", api_app, name="api")

# Mount static files to serve frontend
static_dir = Path(__file__).parent.parent.joinpath("static")

# Optionally, mount directories for assets that you want served directly:
if Path.joinpath(static_dir, "images").exists():
    app.mount("/images", StaticFiles(directory=str(static_dir.joinpath("images"))), name="images")
if Path.joinpath(static_dir, "_next").exists():
    app.mount("/_next", StaticFiles(directory=str(static_dir.joinpath("_next"))), name="_next")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    print("Serving frontend for path:", full_path)
    # If the request is empty, serve index.html
    if full_path == "":
        return FileResponse(static_dir.joinpath("index.html"))

    # remove trailing slash
    if full_path[-1] == "/":
        full_path = full_path[:-1]

    # Build a candidate file path from the request.
    candidate = static_dir.joinpath(full_path)

    # If candidate is a directory, try its index.html.
    print("Checking if candidate is a directory:", candidate)
    if candidate.is_dir():
        candidate_index = candidate.joinpath("index.html")
        if candidate_index.exists():
            print("Serving index.html from directory:", candidate)
            return FileResponse(candidate_index)

    # If no direct file, try appending ".html" (for files like dashboard.html)
    candidate_html = static_dir.joinpath(full_path + ".html")
    print("Checking if candidate HTML file exists:", candidate_html)
    if candidate_html.exists():
        print("Serving candidate HTML file:", candidate_html)
        return FileResponse(candidate_html)

    # If a file exists at that candidate, serve it.
    print("Checking if candidate file exists:", candidate)
    if candidate.exists():
        print("Serving candidate file:", candidate)
        return FileResponse(candidate)

    # Check if the parent directory contains a file named "[id].html"
    parts = full_path.split("/")
    print("Checking if parent directory contains dynamic file:", parts)
    if len(parts) >= 2:
        parent = static_dir.joinpath(*parts[:-1])
        dynamic_file = parent.joinpath("[id].html")
        print("Checking if dynamic file exists:", dynamic_file)
        if dynamic_file.exists():
            return FileResponse(dynamic_file)

    # Fallback: serve the main index.html for client‑side routing.
    print("Falling back to serving index.html")
    return FileResponse(static_dir.joinpath("index.html"))
