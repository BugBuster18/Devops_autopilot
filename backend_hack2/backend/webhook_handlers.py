import os
import httpx

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

async def handle_kestra_webhook(data: dict):
    """Handles callbacks from Kestra (workflow complete)."""
    outputs = data.get("outputs", {})
    status = outputs.get("status", "Unknown")
    repo = outputs.get("repo", "Unknown Repo")
    
    message = f"🚀 Autopilot Complete for {repo}\nStatus: {status}\nBugs Fixed: {outputs.get('bugs_found', 'N/A')}"
    
    # 1. Send Slack Notification
    if SLACK_WEBHOOK:
        async with httpx.AsyncClient() as client:
            await client.post(SLACK_WEBHOOK, json={"text": message})
            
    # 2. Trigger Video Generation (Stub)
    video_url = await generate_video_summary(repo, status)
    
    return {"status": "processed", "video_url": video_url}

async def handle_vercel_webhook(data: dict):
    """Handles callbacks from Vercel (deployment status)."""
    # Logic to notify user about deployment
    print(f"Vercel Deployment Update: {data}")
    return {"status": "received"}

async def generate_video_summary(repo: str, status: str):
    """Stub for HeyGen Video Generation."""
    if not HEYGEN_API_KEY:
        return "Video generation disabled (No API Key)"
    
    # Mock API call to HeyGen
    # In reality, you'd POST to https://api.heygen.com/v1/video/generate
    return "https://heygen.com/video/mock-id-123"
