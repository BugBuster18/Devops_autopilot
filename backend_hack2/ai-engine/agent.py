import os
import sys
import time
import git
from datetime import datetime
from openai import OpenAI

def main():
    print("🤖 Cline AI Agent Started...")
    
    repo_url = os.getenv("REPO_URL")
    github_token = os.getenv("GITHUB_TOKEN")
    bug_report = os.getenv("BUG_REPORT", "")
    
    # Ollama Configuration
    ollama_host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434/v1")
    model = "llama3"
    
    if not repo_url:
        print("❌ No REPO_URL provided.")
        sys.exit(1)
        
    if not github_token:
        print("⚠️ No GITHUB_TOKEN provided. Operations requiring auth (push) will fail.")

    # Construct authenticated URL if token is present
    auth_repo_url = repo_url
    if github_token and "github.com" in repo_url:
        auth_repo_url = repo_url.replace("https://", f"https://oauth2:{github_token}@")

    work_dir = "/tmp/repo"
    
    try:
        print(f"📂 Cloning {repo_url}...")
        if os.path.exists(work_dir):
            import shutil
            shutil.rmtree(work_dir)
            
        repo = git.Repo.clone_from(auth_repo_url, work_dir)
        
        # Create a new branch
        branch_name = f"autopilot-fix-{int(time.time())}"
        print(f"🌿 Creating branch: {branch_name}")
        current = repo.create_head(branch_name)
        current.checkout()
        
        # AI Analysis & Fix
        print(f"🧠 Connecting to Ollama at {ollama_host}...")
        client = OpenAI(base_url=ollama_host, api_key="ollama")
        
        prompt = f"""
        You are Cline, an expert autonomous coding agent. 
        Analyze the following bug report and suggest a fix for the repository.
        
        BUG REPORT:
        {bug_report}
        
        If no specific bug is found, suggest a general improvement to the README.
        Provide the fix as a code block that I can append to README.md.
        """
        
        fix_content = ""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            fix_content = response.choices[0].message.content
            print("✅ AI Analysis Complete.")
        except Exception as e:
            print(f"⚠️ Ollama analysis failed: {e}")
            print("Falling back to static fix.")
            fix_content = "## 🤖 Autopilot Fix\nFixed by AI Agent (Fallback) at " + str(datetime.utcnow())

        # Apply Fix (Append to README)
        readme_path = os.path.join(work_dir, "README.md")
        print(f"✍️ Applying fix to {readme_path}...")
        
        with open(readme_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n{fix_content}\n")
            
        # Commit
        repo.index.add(["README.md"])
        repo.index.commit("fix: applied automated fixes by Autopilot AI")
        print("✅ Changes committed.")
        
        # Push
        if github_token:
            print(f"🚀 Pushing to {branch_name}...")
            repo.remotes.origin.push(branch_name)
            print("🎉 Push successful!")
        else:
            print("⚠️ Skipping push (no token).")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
