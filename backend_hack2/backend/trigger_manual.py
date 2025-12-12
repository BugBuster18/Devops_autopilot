import asyncio
import os

# Force localhost for manual script (must be before importing kestra_client)
os.environ["KESTRA_URL"] = "http://localhost:8080"

from dotenv import load_dotenv
import kestra_client 
from kestra_client import trigger_workflow
import base64

# Patch headers for Basic Auth (admin:admin)
creds = base64.b64encode(b"admin:admin").decode("utf-8")
kestra_client.HEADERS = {"Authorization": f"Basic {creds}"}
print(f"DEBUG: Using Headers: {kestra_client.HEADERS}")

# Load environment variables
load_dotenv()

async def main():
    # 1. Get configuration
    repo_url = input("Enter Repo URL (default: https://github.com/Abhi-vish/Agent): ") or "https://github.com/Abhi-vish/Agent"
    branch = input("Enter Branch (default: main): ") or "main"
    user_email = input("Enter User Email (default: test@example.com): ") or "test@example.com"
    
    # 2. Get GitHub Token (Critical)
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ Error: GITHUB_TOKEN not found in .env")
        return

    print(f"\n🚀 Triggering Autopilot for:")
    print(f"  Repo: {repo_url}")
    print(f"  Branch: {branch}")
    print(f"  Email: {user_email}")
    print(f"  Token: {github_token[:4]}...{github_token[-4:]}")

    try:
        # 3. Call Kestra
        # Note: We are bypassing the backend API and calling Kestra directly via the client helper
        execution = await trigger_workflow(
            repo_url=repo_url,
            branch=branch,
            user_email=user_email,
            github_token=github_token,
            coderabbit_token=os.getenv("CODERABBIT_API_KEY", "test-token")
        )
        
        print(f"\n✅ Success! Execution started.")
        print(f"  ID: {execution['id']}")
        print(f"  Link: http://localhost:8080/ui/executions/hackathon/devops-autopilot/{execution['id']}")
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
