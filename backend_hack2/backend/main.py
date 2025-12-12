# ----------------------------------------------------------------------
# main.py – only the parts that changed are shown
# ----------------------------------------------------------------------
import os, asyncio, logging, time
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from pydantic import BaseModel, HttpUrl, EmailStr, validator
from dotenv import load_dotenv
import uvicorn

# ----------------------------------------------------------------------
# Project‑specific imports
# ----------------------------------------------------------------------
from database import ping_db, get_user_collection, db, cache_get, cache_set, cache_delete, create_indexes
from auth_routes import router as auth_router
from kestra_client import trigger_workflow, get_logs_stream
from logging_config import setup_logging
from exceptions import (
    AutopilotBaseException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    ExternalAPIError,
    DatabaseError,
    VideoGenerationError,
    ReportGenerationError,
    ResourceNotFoundError,
    ConfigurationError,
)

# NEW – import the helper we just created
from agents import process_kestra_completion

# ----------------------------------------------------------------------
# Set up structured logging
# ----------------------------------------------------------------------
logger = setup_logging()

load_dotenv()

# ----------------------------------------------------------------------
# Lifespan – same as before (adds a graceful DB close)
# ----------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await ping_db()               # aborts start‑up if Mongo is down
    yield
    await db.client.close()
    logging.info("Mongo client closed")

app = FastAPI(
    title="Autopilot.dev Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],               # 👉 replace with your front‑end domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# Pydantic models with enhanced validation
# ----------------------------------------------------------------------
class TriggerRequest(BaseModel):
    repo_url: HttpUrl
    branch: str = "main"
    user_email: EmailStr

    class Config:
        str_strip_whitespace = True
        str_min_length = 1

    @validator('branch')
    def validate_branch(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Branch name cannot be empty')
        if len(v) > 255:
            raise ValueError('Branch name too long')
        # Basic validation for branch name characters
        import re
        if not re.match(r'^[a-zA-Z0-9._/-]+$', v):
            raise ValueError('Invalid branch name characters')
        return v.strip()

    @validator('repo_url')
    def validate_repo_url(cls, v):
        # Ensure it's a GitHub URL
        if 'github.com' not in str(v):
            raise ValueError('Only GitHub repositories are supported')
        return v

# ----------------------------------------------------------------------
# Root / health – with detailed docstrings
# ----------------------------------------------------------------------
@app.get(
    "/",
    summary="Root endpoint",
    description="Returns a welcome message for the Autopilot.dev backend API.",
    tags=["General"]
)
async def root():
    """
    Get basic information about the API.

    Returns:
        dict: A welcome message with API information.
    """
    return {"message": "Autopilot.dev Backend (MongoDB + GitHub Auth) 🚀"}

@app.get(
    "/health",
    summary="Health check",
    description="Check if the service is running and database is accessible.",
    tags=["General"]
)
async def health():
    """
    Perform a health check of the service.

    Returns:
        dict: Health status of the service including database connectivity.
    """
    try:
        # Check database connectivity
        await ping_db()
        db_status = "healthy"
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get(
    "/metrics",
    summary="Performance metrics",
    description="Get application performance metrics and statistics.",
    tags=["Monitoring"]
)
async def metrics():
    """
    Get performance metrics for monitoring.

    Returns:
        dict: Performance metrics including request counts, response times, etc.
    """
    try:
        # Get basic metrics from database
        runs_count = await db["runs"].count_documents({})
        users_count = await db["users"].count_documents({})
        artefacts_count = await db["artefacts"].count_documents({})

        # Get recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_runs = await db["runs"].count_documents({"timestamp": {"$gte": yesterday}})

        return {
            "total_runs": runs_count,
            "total_users": users_count,
            "total_artefacts": artefacts_count,
            "recent_runs_24h": recent_runs,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Metrics collection failed: {exc}")
        raise DatabaseError(f"Failed to collect metrics: {str(exc)}")

# ----------------------------------------------------------------------
# /api/trigger – enhanced with custom exceptions and logging
# ----------------------------------------------------------------------
@app.post(
    "/api/trigger",
    summary="Trigger DevOps automation workflow",
    description="Starts the DevOps automation workflow for a GitHub repository, including code analysis, report generation, and video creation.",
    tags=["Workflow"],
    response_model=dict,
    responses={
        200: {
            "description": "Workflow triggered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "execution_id": "abc123",
                        "message": "Autopilot launched – video will be ready after workflow finishes",
                        "status_url": "/api/status/abc123"
                    }
                }
            }
        },
        401: {"description": "Authentication failed"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def trigger_autopilot(
    req: TriggerRequest,
    background: BackgroundTasks,
    request: Request
):
    # Enhanced JWT validation
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid authorization header")

    token = auth_header.split(" ")[1]
    try:
        # Decode and validate JWT token
        import jwt
        from datetime import datetime, timedelta

        JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise AuthenticationError("Token has expired")

        user_email = payload.get("sub")
        if not user_email:
            raise AuthenticationError("Invalid token payload")

        # Verify user exists in database
        users_col = get_user_collection()
        user_doc = await users_col.find_one({"email": user_email})
        if not user_doc:
            raise AuthenticationError("User not found")

        logger.info(f"Authenticated user: {user_email}")

    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
    except Exception as exc:
        logger.error(f"JWT validation failed: {exc}")
        raise AuthenticationError("Authentication failed")
    logger.info(f"Triggering autopilot for repo: {req.repo_url}, user: {req.user_email}")

    try:
        # ------ validation & Kestra start ------
        repo_str = str(req.repo_url)
        users_col = get_user_collection()
        user_doc = await users_col.find_one({"email": req.user_email})
        if not user_doc:
            logger.warning(f"User not found: {req.user_email}")
            raise ResourceNotFoundError(f"User not found: {req.user_email}")

        github_token = user_doc.get("github_token")
        if not github_token:
            logger.warning(f"GitHub token missing for user: {req.user_email}")
            raise AuthenticationError("GitHub token missing – please re-authenticate")

        system_coderabbit_token = os.getenv("CODERABBIT_TOKEN")
        if not system_coderabbit_token:
            logger.error("CODERABBIT_TOKEN environment variable not set")
            raise ConfigurationError("System configuration error")

        try:
            execution = await trigger_workflow(
                repo_url=repo_str,
                branch=req.branch,
                user_email=req.user_email,
                github_token=github_token,
                coderabbit_token=system_coderabbit_token,
            )
            execution_id = execution["id"]
            logger.info(f"Kestra workflow triggered successfully: {execution_id}")
        except Exception as exc:
            logger.error(f"Kestra trigger failed: {exc}")
            raise ExternalAPIError(f"Failed to trigger workflow: {str(exc)}")

        # ------- store the run document ---------------------------------
        try:
            run_doc = {
                "id": execution_id,
                "repo": repo_str,
                "status": "RUNNING",
                "timestamp": execution["state"]["startDate"],
                "user_email": req.user_email,
            }
            await db["runs"].insert_one(run_doc)
            logger.info(f"Run document stored for execution: {execution_id}")
        except Exception as exc:
            logger.error(f"Failed to store run document: {exc}")
            raise DatabaseError(f"Failed to store execution record: {str(exc)}")

        # ------- respond immediately ------------------------------------
        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Autopilot launched – video will be ready after workflow finishes",
            "status_url": f"/api/status/{execution_id}",
        }

    except AutopilotBaseException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error in trigger_autopilot: {exc}")
        raise HTTPException(500, "Internal server error")

# ----------------------------------------------------------------------
# /api/status – log streaming with documentation
# ----------------------------------------------------------------------
@app.get(
    "/api/status/{execution_id}",
    summary="Stream workflow execution logs",
    description="Streams real-time logs for a specific workflow execution using Server-Sent Events.",
    tags=["Workflow"],
    responses={
        200: {
            "description": "Log stream established",
            "content": {
                "text/event-stream": {
                    "example": "data: Workflow started\n\ndata: Processing repository\n\n"
                }
            }
        },
        404: {"description": "Execution not found"},
        500: {"description": "Log streaming failed"}
    }
)
async def stream_status(execution_id: str):
    try:
        return StreamingResponse(
            get_logs_stream(execution_id),
            media_type="text/event-stream",
        )
    except Exception as exc:
        raise HTTPException(500, f"Log stream failed: {exc}")

# ----------------------------------------------------------------------
# /api/runs – recent runs with enhanced error handling
# ----------------------------------------------------------------------
@app.get(
    "/api/runs",
    summary="Get recent workflow executions",
    description="Retrieves the most recent workflow executions, sorted by timestamp.",
    tags=["Workflow"],
    responses={
        200: {
            "description": "List of recent runs",
            "content": {
                "application/json": {
                    "example": {
                        "runs": [
                            {
                                "id": "exec123",
                                "repo": "https://github.com/user/repo",
                                "status": "COMPLETED",
                                "timestamp": "2024-01-01T00:00:00Z",
                                "user_email": "user@example.com"
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "Database error"}
    }
)
async def get_runs():
    logger.info("Fetching recent runs")

    try:
        cur = db["runs"].find().sort("timestamp", -1).limit(50)
        runs = await cur.to_list(50)
        for r in runs:
            r["_id"] = str(r["_id"])
        logger.info(f"Retrieved {len(runs)} runs")
        return {"runs": runs}
    except Exception as exc:
        logger.error(f"Failed to fetch runs: {exc}")
        raise DatabaseError(f"Failed to retrieve execution history: {str(exc)}")

# ----------------------------------------------------------------------
# /webhook/kestra – now also fires the video‑generation background task
# ----------------------------------------------------------------------
@app.post("/webhook/kestra")
async def kestra_webhook(request: Request):
    """
    Kestra calls this when a workflow finishes.
    1️⃣ Mark the run as COMPLETED.
    2️⃣ Fire‑and‑forget `process_kestra_completion` (which creates the video).
    """
    try:
        payload = await request.json()
        exec_id = payload.get("id") or payload.get("executionId")
        if not exec_id:
            raise ValueError("Missing executionId in webhook payload")

        # 1️⃣ update run status (upsert=True to handle manual Kestra runs)
        await db["runs"].update_one(
            {"id": exec_id},
            {
                "$set": {
                    "status": "COMPLETED", 
                    "finished_at": datetime.utcnow(),
                    # Ensure these fields exist if creating a new doc
                    "repo": payload.get("repo"),
                    "user_email": payload.get("user_email")
                }
            },
            upsert=True
        )

        # -----------------------------------------------------------------
        # 2️⃣ launch the *creative* background job
        # -----------------------------------------------------------------
        run_doc = await db["runs"].find_one({"id": exec_id})
        if not run_doc:
            raise RuntimeError("Run document not found after completion")
        
        repo_url = run_doc.get("repo")
        user_email = run_doc.get("user_email")
        
        if not repo_url or not user_email:
             logging.warning("Skipping video generation: repo or user_email missing in run doc")
             return {"status": "processed", "video": "skipped"}

        async def _run_post_kestra():
            try:
                result = await process_kestra_completion(
                    repo_url=repo_url,
                    execution_id=exec_id,
                    user_email=user_email,
                    db=db,
                )
                # Store the result back onto the run document
                await db["runs"].update_one(
                    {"id": exec_id},
                    {"$set": {
                        "status": "VIDEO_READY",
                        "completion_message": result["message"],
                        "artefact_id": result["artefact_id"],
                    }},
                )
            except Exception as exc:
                logging.exception("Post‑Kestra video generation failed: %s", exc)
                await db["runs"].update_one(
                    {"id": exec_id},
                    {"$set": {"status": "VIDEO_FAILED"}}
                )

        # fire‑and‑forget – the webhook returns *immediately*
        asyncio.create_task(_run_post_kestra())

        return {"status": "processed"}
    except Exception as exc:
        logging.exception("Kestra webhook handling error: %s", exc)
        raise HTTPException(500, f"Webhook processing failed: {exc}")

# ----------------------------------------------------------------------
# NEW – endpoint that streams the *raw video bytes* to the front‑end
# ----------------------------------------------------------------------
@app.get(
    "/api/video/{execution_id}",
    summary="Get generated video",
    description="Retrieves the AI-generated video for a completed workflow execution.",
    tags=["Media"],
    responses={
        200: {
            "description": "Video file stream",
            "content": {
                "video/mp4": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
        404: {"description": "Video not found"},
        500: {"description": "Video retrieval failed"}
    }
)
async def get_video(execution_id: str):
    """
    Returns the video generated for a given Kestra execution.
    The video is streamed as `video/mp4` (or whatever codec the provider produced).
    """
    # Find the artefact that belongs to this execution
    artefact = await db["artefacts"].find_one({"session": execution_id})
    if not artefact:
        raise HTTPException(404, "Video artefact not found")

    video_bytes = artefact.get("video_bytes")
    if not video_bytes:
        raise HTTPException(500, "Video data is missing in artefact")

    # Stream the bytes – FastAPI will set the correct `Content‑Length`
    return StreamingResponse(
        iter([video_bytes]),      # a single‑iteration generator
        media_type="video/mp4",
        headers={"Content-Disposition": f'inline; filename="{execution_id}.mp4"'},
    )

# ----------------------------------------------------------------------
# Vercel webhook with documentation
# ----------------------------------------------------------------------
@app.post(
    "/webhook/vercel",
    summary="Vercel deployment webhook",
    description="Handles webhook notifications from Vercel deployments.",
    tags=["Webhooks"],
    responses={
        200: {"description": "Webhook processed successfully"},
        500: {"description": "Webhook processing failed"}
    }
)
async def vercel_webhook(request: Request):
    try:
        payload = await request.json()
        return {"status": "deployed", "payload": payload}
    except Exception as exc:
        raise HTTPException(500, f"Vercel webhook failed: {exc}")

# ----------------------------------------------------------------------
# NEW – Together AI endpoints
# ----------------------------------------------------------------------
@app.post("/api/together-ai/generate")
async def generate_together_report(request: Request):
    """Generate a Together AI report for a repository."""
    try:
        payload = await request.json()
        repo_url = payload.get("repo_url")
        execution_id = payload.get("execution_id")
        user_email = payload.get("user_email")

        if not repo_url or not execution_id:
            raise HTTPException(400, "Missing repo_url or execution_id")

        # Get CodeRabbit insights first
        from agents import get_coderabbit_insights, generate_together_report
        coderabbit_key = os.getenv("CODERABBIT_API_KEY")
        if not coderabbit_key:
            raise HTTPException(500, "CODERABBIT_API_KEY missing")

        insights = get_coderabbit_insights(repo_url, coderabbit_key)
        
        # Generate Together AI report
        together_key = os.getenv("TOGETHER_API_KEY")
        if not together_key:
            raise HTTPException(500, "TOGETHER_API_KEY missing")

        report = generate_together_report(insights, together_key)

        # Store report in database
        report_doc = {
            "execution_id": execution_id,
            "repo_url": repo_url,
            "report": report,
            "created_at": datetime.utcnow(),
        }
        await db["together_reports"].insert_one(report_doc)

        return {
            "report": report,
            "execution_id": execution_id,
            "repo_url": repo_url,
            "created_at": report_doc["created_at"].isoformat(),
        }
    except Exception as exc:
        logging.exception("Together AI report generation failed: %s", exc)
        raise HTTPException(500, f"Failed to generate report: {exc}")

@app.get(
    "/api/together-ai/report/{execution_id}",
    summary="Get Together AI report",
    description="Retrieves a previously generated Together AI report by execution ID.",
    tags=["Reports"],
    responses={
        200: {
            "description": "Report retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "execution_id": "exec123",
                        "repo_url": "https://github.com/user/repo",
                        "report": "Executive summary...",
                        "created_at": "2024-01-01T00:00:00.000Z"
                    }
                }
            }
        },
        404: {"description": "Report not found"},
        500: {"description": "Report retrieval failed"}
    }
)
async def get_together_report(execution_id: str):
    """Get a Together AI report by execution ID."""
    try:
        report_doc = await db["together_reports"].find_one({"execution_id": execution_id})
        if not report_doc:
            raise HTTPException(404, "Report not found")
        
        report_doc["_id"] = str(report_doc["_id"])
        report_doc["created_at"] = report_doc["created_at"].isoformat()
        return report_doc
    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("Failed to fetch Together AI report: %s", exc)
        raise HTTPException(500, f"Failed to fetch report: {exc}")

# ----------------------------------------------------------------------
# NEW – Cline AI agent endpoints
# ----------------------------------------------------------------------
@app.post("/api/cline/trigger")
async def trigger_cline_agent(request: Request):
    """Trigger Cline AI agent to fix code."""
    try:
        payload = await request.json()
        repo_url = payload.get("repo_url")
        branch = payload.get("branch", "main")
        bug_report = payload.get("bug_report", "")
        github_token = payload.get("github_token")

        if not repo_url:
            raise HTTPException(400, "Missing repo_url")

        # Store execution in database
        execution_id = f"cline_{int(time.time())}"
        cline_doc = {
            "execution_id": execution_id,
            "repo_url": repo_url,
            "branch": branch,
            "bug_report": bug_report,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        await db["cline_executions"].insert_one(cline_doc)

        # Trigger Cline agent in background
        async def _run_cline():
            try:
                import subprocess
                import os
                
                env = os.environ.copy()
                env["REPO_URL"] = repo_url
                env["GITHUB_TOKEN"] = github_token or ""
                env["BUG_REPORT"] = bug_report
                
                # Run Cline agent (assuming it's in the ai-engine directory)
                result = subprocess.run(
                    ["python", "ai-engine/agent.py"],
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd="/app"  # Adjust path as needed
                )
                
                status = "completed" if result.returncode == 0 else "failed"
                await db["cline_executions"].update_one(
                    {"execution_id": execution_id},
                    {
                        "$set": {
                            "status": status,
                            "output": result.stdout,
                            "error": result.stderr if result.returncode != 0 else None,
                            "completed_at": datetime.utcnow(),
                        }
                    }
                )
            except Exception as exc:
                logging.exception("Cline execution failed: %s", exc)
                await db["cline_executions"].update_one(
                    {"execution_id": execution_id},
                    {
                        "$set": {
                            "status": "failed",
                            "error": str(exc),
                            "completed_at": datetime.utcnow(),
                        }
                    }
                )

        asyncio.create_task(_run_cline())

        return {
            "execution_id": execution_id,
            "repo_url": repo_url,
            "branch": branch,
            "status": "running",
        }
    except Exception as exc:
        logging.exception("Cline trigger failed: %s", exc)
        raise HTTPException(500, f"Failed to trigger Cline: {exc}")

@app.get("/api/cline/status/{execution_id}")
async def get_cline_status(execution_id: str):
    """Get Cline agent execution status."""
    try:
        cline_doc = await db["cline_executions"].find_one({"execution_id": execution_id})
        if not cline_doc:
            raise HTTPException(404, "Cline execution not found")
        
        cline_doc["_id"] = str(cline_doc["_id"])
        if "created_at" in cline_doc:
            cline_doc["created_at"] = cline_doc["created_at"].isoformat()
        if "completed_at" in cline_doc:
            cline_doc["completed_at"] = cline_doc["completed_at"].isoformat()
        
        return {
            "execution_id": cline_doc["execution_id"],
            "repo_url": cline_doc["repo_url"],
            "branch": cline_doc.get("branch", "main"),
            "status": cline_doc["status"],
            "output": cline_doc.get("output"),
            "error": cline_doc.get("error"),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("Failed to fetch Cline status: %s", exc)
        raise HTTPException(500, f"Failed to fetch Cline status: {exc}")

# ----------------------------------------------------------------------
# Run the server
# ----------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
