import os
import httpx
from fastapi import HTTPException

# Kestra OSS URL (internal Docker hostname)
KESTRA_URL = os.getenv("KESTRA_URL", "http://kestra:8080")

# Kestra OSS does NOT use authentication → always empty
HEADERS = {}

async def trigger_workflow(
    repo_url: str, 
    branch: str, 
    user_email: str, 
    github_token: str, 
    coderabbit_token: str = ""
):
    """Trigger a Kestra workflow in OSS mode (no auth)."""

    url = f"{KESTRA_URL}/api/v1/executions/trigger/hackathon/devops-autopilot"

    payload = {
        "repoUrl": repo_url,
        "branch": branch,
        "userEmail": user_email,
        "githubToken": github_token,
        "coderabbitToken": coderabbit_token,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=HEADERS)

            # If flow not found
            if response.status_code == 404:
                raise HTTPException(404, "Kestra flow 'devops-autopilot' not found.")

            response.raise_for_status()
            return response.json()

        except httpx.ConnectError:
            raise HTTPException(503, f"Cannot reach Kestra at {KESTRA_URL}")

        except httpx.HTTPStatusError as e:
            raise HTTPException(e.response.status_code, f"Kestra error: {e.response.text}")

async def get_logs_stream(execution_id: str):
    """Stream logs from Kestra OSS."""
    url = f"{KESTRA_URL}/api/v1/executions/{execution_id}/logs"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()

            for log in response.json():
                yield f"data: {log.get('message', '')}\n\n"

        except Exception as e:
            yield f"data: Log stream error: {str(e)}\n\n"
