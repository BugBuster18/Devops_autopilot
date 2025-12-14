
# 🚀 Autopilot.dev - Your 24/7 AI DevOps Team

FastAPI • Next.js • Kestra • MongoDB Atlas • Docker Compose

> **Paste any GitHub repo URL → AI agents (Cline + CodeRabbit) fix bugs, review PRs, deploy to Vercel preview, & send video report – zero human touch.**

**Built for AssembleHack25 🏆**

---

## 🎯 Problem & Solution

### The Problem

* Manual DevOps workflows are time-consuming and error-prone
* Code reviews require human attention and context switching
* Deployment processes lack automation and visibility
* Teams struggle with repetitive bug fixes and testing

### Our Solution

**Autopilot.dev** is an AI-powered DevOps automation platform that:

* 🤖 Automatically analyzes GitHub repositories using CodeRabbit
* 🔧 Intelligently fixes bugs using AI agents (Cline + GPT-4)
* 📝 Generates comprehensive reports using Together AI
* 🎬 Creates video summaries using Google Veo / Pika Labs
* 🚀 Deploys preview branches to Vercel automatically
* 📊 Provides real-time workflow visualization and logs

---

## 🧠 AI Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│                    (GitHub Repo URL)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                        │
│  • GitHub OAuth Authentication                                  │
│  • Request Validation & Rate Limiting                           │
│  • MongoDB Data Storage                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              KESTRA ORCHESTRATOR (Workflow Engine)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  1. SCAN     │→ │  2. FIX      │→ │  3. REVIEW   │         │
│  │ CodeRabbit   │  │ AI Agents    │  │ CodeRabbit   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                 │                  │                  │
│         └─────────────────┴──────────────────┘                  │
│                             │                                    │
│                             ▼                                    │
│                  ┌──────────────┐                                │
│                  │  4. DEPLOY   │                                │
│                  │   Vercel     │                                │
│                  └──────────────┘                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AI POST-PROCESSING (Background Tasks)               │
│  • Groq (Llama-3.3-70B) → Video Script Generation              │
│  • Google Veo / Pika Labs → Video Rendering                     │
│  • Together AI → Executive Report Generation                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND DASHBOARD (Next.js)                 │
│  • Real-time Workflow Visualization                             │
│  • Agent Logs & Status Tracking                                 │
│  • Video Playback & Report Display                              │
│  • Dark/Light Theme Support                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend

* FastAPI
* MongoDB (Atlas / Motor)
* Redis
* Kestra
* Docker

### AI & Automation

* OpenAI GPT-4
* Groq Llama-3.3-70B
* Together AI
* CodeRabbit
* Google Veo / Pika Labs

### Frontend

* Next.js 13
* Tailwind CSS
* Framer Motion
* Lucide React
* NextAuth.js

### Infrastructure

* Docker Compose
* Vercel
* Railway / Render

---



## Demo Video

https://youtu.be/EJ6GwYayyP8

---

## 🧪 How to Run

### Prerequisites

* Docker Desktop
* MongoDB Atlas or local MongoDB
* API keys for GitHub OAuth, OpenAI, Groq, Together AI, CodeRabbit, Google Veo/Pika

---

### One-Click Setup (Docker Compose)

```bash
git clone <repo>
cd autopilot-dev
```

```bash
cd backend
cp env.example .env
```

```bash
docker-compose up --build
```

Services:

* Backend API → localhost:8000
* API Docs → localhost:8000/docs
* Kestra UI → localhost:8080
* Frontend → localhost:3000

---

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📖 API Documentation

### Authentication

Use Bearer JWT token:

```
Authorization: Bearer <TOKEN>
```

### Key Endpoints

**Trigger Workflow**

```json
POST /api/trigger
{
  "repo_url": "",
  "branch": "main",
  "user_email": "example@mail.com"
}
```

**Workflow Status**

```
GET /api/status/{execution_id}
```

**Generated Video**

```
GET /api/video/{execution_id}
```

**Executive Report**

```
GET /api/together-ai/report/{execution_id}
```

---

## 🤝 Multi-Agent System

### Agents

1. Research Agent
2. Fix Agent
3. Review Agent
4. Deploy Agent
5. Report Agent

### agents.yaml Example

```yaml
agents:
  - name: researcher
    model: gpt-4
    timeout: 300

  - name: fixer
    model: gpt-4
    timeout: 600

  - name: reviewer
    service: coderabbit
    timeout: 180

  - name: deployer
    service: vercel
    timeout: 120

  - name: reporter
    model: together-ai
    timeout: 240
```

---

## 🏗️ Project Structure

```
backend/
  main.py
  agents.py
  auth_routes.py
  database.py
  kestra_client.py
  services/
  docker-compose.yml

kestra/
  flows/
    devops-autopilot.yaml

ai-engine/
  agent.py

frontend/
  pages/
  components/
  package.json
```

---

## 🎨 Features

### UI/UX

* Smooth animations
* Dark/Light mode
* Responsive
* SSE realtime logs
* Notifications
* Workflow visualization

### Performance

* Redis caching
* Retry logic
* Rate limiting
* Optimized queries

### Reliability

* Error handling
* Structured logs
* Unit tests
* JWT auth
* Health checks

---

## 👥 Team & Credits

Built for AssembleHack25
Technologies: FastAPI, Kestra, Next.js, MongoDB, Redis
AI Providers: OpenAI, Groq, Together AI, CodeRabbit, Google Veo/Pika

---


## 📞 Support

Open an issue in the repository (link removed).

---
