# 🚀 Autopilot.dev

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Kestra](https://img.shields.io/badge/Kestra-0.18-4A154B?style=flat&logo=kestra&logoColor=white)](https://kestra.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

**Your 24/7 AI DevOps Team – Built for AssembleHack25 🏆**

> "Paste any GitHub repo URL → AI agents (Cline + CodeRabbit) fix bugs, review PRs, deploy to Vercel preview, & send video report – zero human touch."

[Demo Video](https://youtu.be/demo-link) | [Live Dashboard](https://autopilot.vercel.app)

---

## 🧠 Deep Dive: Architecture & Workflow

This project uses a **Microservices** approach orchestrated by **Kestra**. The system is composed of three main containers:
1.  **Backend (`autopilot-backend`)**: FastAPI server handling Auth, API, and Video Generation.
2.  **Kestra (`autopilot-kestra`)**: Orchestrator managing the complex "Scan -> Fix -> Deploy" pipeline.
3.  **AI Engine (`autopilot-ai-engine`)**: Ephemeral Docker container spawned by Kestra to run the heavy coding agents.

### Detailed Execution Flow

#### 1. Authentication (User Login)
*   **File**: `backend/auth_routes.py`
*   **Action**: User logs in via **GitHub OAuth**.
*   **Data**: The system captures the user's `email`, `github_username`, and `access_token`.
*   **Storage**: Saved to **MongoDB** (`users` collection) via `database.py`. This token is later used to open PRs on the user's behalf.

#### 2. The Trigger
*   **File**: `backend/main.py` (`POST /api/trigger`)
*   **Action**: User submits a Repo URL.
*   **Process**:
    *   Backend retrieves the user's GitHub token from MongoDB.
    *   Calls `kestra_client.trigger_workflow()`.
    *   Sends a request to Kestra API (`http://kestra:8080`) to start the `devops-autopilot` flow.

#### 3. The Orchestration (Kestra)
*   **File**: `kestra/flows/devops-autopilot.yaml`
*   **The Pipeline**:
    1.  **Scan**: Runs a shell command to analyze the repo with **CodeRabbit**.
    2.  **Fix (The "Brain")**:
        *   Kestra executes a `io.kestra.plugin.docker.Run` task.
        *   It spins up the `autopilot-ai-engine` container.
        *   Runs `python agent.py` inside this container.
        *   **Agent Logic**: Clones the repo, uses **OpenAI (GPT-4o)** to fix bugs, writes tests, and pushes a new branch.
    3.  **Review**: Triggers CodeRabbit to review the new PR.
    4.  **Deploy**: Deploys the preview branch to **Vercel**.
    5.  **Notify**: Kestra sends a POST webhook back to the Backend (`/webhook/kestra`) with the status.

#### 4. Video Generation (Post-Processing)
*   **File**: `backend/webhook_handlers.py` & `backend/agents.py`
*   **Trigger**: Kestra webhook hits `POST /webhook/kestra`.
*   **Process**:
    1.  Backend marks the run as `COMPLETED` in MongoDB.
    2.  **Async Task**: `agents.process_kestra_completion()` is called.
    3.  **Script Generation**: Uses **Groq (Llama-3)** to write a 30-word script summarizing the fixes (based on CodeRabbit insights).
    4.  **Video Rendering**: Calls **Google Veo** (or Pika Labs fallback) to generate an MP4 video from the text prompt.
    5.  **Storage**: The raw video bytes are stored in **MongoDB** (`artefacts` collection).

#### 5. Delivery
*   **File**: `backend/main.py` (`GET /api/video/{execution_id}`)
*   **Action**: Frontend polls for the video.
*   **Result**: The Backend streams the MP4 bytes directly from MongoDB to the browser.

---

## 📂 Critical File Breakdown

*   **`backend/main.py`**: The API Gateway. Integrates Auth, Database, Kestra Client, and Webhooks.
*   **`backend/agents.py`**: The Creative Director. Handles LLM interactions (Groq) and Video API calls (Veo/Pika).
*   **`backend/auth_routes.py`**: OAuth handler. Manages the "Login with GitHub" flow.
*   **`backend/database.py`**: MongoDB connection manager and Schema definitions (`UserSchema`).
*   **`backend/Dockerfile`**: Defines the Python environment for the backend (FastAPI, Uvicorn).
*   **`kestra/flows/devops-autopilot.yaml`**: The Master Plan. Defines the step-by-step DevOps workflow.
*   **`docker-compose.yml`**: The Glue. Defines how Backend, Kestra, and AI Engine network together.

---

## 🏃‍♂️ How to Run (Docker Compose)

### Prerequisites
1.  **Docker Desktop** installed and running.
2.  **MongoDB Atlas** URI (or a local Mongo instance).
3.  **API Keys** for services (GitHub, OpenAI, Groq, Google/Veo).

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/autopilot-dev
cd autopilot-dev
```

### Step 2: Environment Configuration
Navigate to the `backend` folder and create your `.env` file.

```bash
cd backend
# Create .env file
```

**`backend/.env` Content:**
```ini
# --- Database ---
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority

# --- Authentication (GitHub OAuth App) ---
GITHUB_CLIENT_ID=Iv1...
GITHUB_CLIENT_SECRET=e23...

# --- AI & Video Services ---
OPENAI_API_KEY=sk-...          # For the Code Fix Agent
CODERABBIT_API_KEY=...         # For Analysis
GROQ_API_KEY=gsk_...           # For Video Scripting
GOOGLE_API_KEY=AIza...         # For Veo Video Generation (Google GenAI)
PIKA_API_KEY=...               # (Optional) Fallback Video

# --- Kestra Integration ---
KESTRA_URL=http://kestra:8080  # Internal Docker URL
KESTRA_API_TOKEN=              # Leave empty if no Auth on Kestra
```

### Step 3: Build and Run
From the **root** directory (`autopilot-dev/`), run:

```bash
docker-compose up --build
```

### Step 4: Verify Deployment
1.  **Backend**: Open `http://localhost:8000`. You should see the "Autopilot.dev Backend" welcome message.
    *   Docs: `http://localhost:8000/docs`
2.  **Kestra UI**: Open `http://localhost:8080`. You should see the Kestra dashboard.
    *   Check **Flows** -> `devops-autopilot` to ensure the workflow is loaded.
3.  **Database**: Check your MongoDB Compass/Atlas to ensure connection is successful (logs will show `✅ Connected to MongoDB Atlas!`).

### Step 5: Trigger a Run
Use Postman or `curl` to start the magic:

```bash
curl -X POST "http://localhost:8000/api/trigger" \
     -H "Content-Type: application/json" \
     -d '{
           "repo_url": "https://github.com/username/buggy-repo",
           "user_email": "your-email@example.com"
         }'
```

Watch the **Kestra UI** to see the agent spin up, clone the repo, and fix bugs in real-time! 🍿

---

## 📜 License
MIT License. See `LICENSE` for details.
