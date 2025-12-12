# ----------------------------------------------------------------------
# agents.py   (pure‑python helper – no Streamlit code)
# ----------------------------------------------------------------------
import os, json, time, random, base64, logging
from datetime import datetime, timedelta
import httpx
from functools import wraps
from typing import Callable, Any

# Optional SDKs ---------------------------------------------------------
try:
    from langchain_groq import ChatGroq           # LLM for prompt creation
except ImportError:                               # pragma: no cover
    ChatGroq = None

try:
    from google import genai
    from google.genai import types
except ImportError:                               # pragma: no cover
    genai = None
    types = None

# ----------------------------------------------------------------------
# Retry decorator for external API calls
# ----------------------------------------------------------------------
def retry_on_failure(max_retries: int = 3, backoff_factor: float = 2.0,
                     exceptions: tuple = (Exception,)):
    """Decorator to retry function calls with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt + random.uniform(0, 1)
                        logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {exc}. "
                                      f"Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        logging.error(f"All {max_retries} attempts failed for {func.__name__}: {exc}")
            raise last_exception
        return wrapper
    return decorator

# ----------------------------------------------------------------------
# 1️⃣ CodeRabbit helper (unchanged)
# ----------------------------------------------------------------------
CODERABBIT_API_URL = "https://api.coderabbit.ai/api/v1/report.generate"

@retry_on_failure(max_retries=3, backoff_factor=2.0, exceptions=(httpx.HTTPError, httpx.TimeoutException))
def get_coderabbit_insights(repo_url: str, api_key: str) -> dict:
    if not api_key:
        raise RuntimeError("CodeRabbit API key missing")
    headers = {
        "Content-Type": "application/json",
        "x-coderabbitai-api-key": api_key,
    }
    data = {
        "repository": repo_url,
        "from": (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d"),
        "to": datetime.utcnow().strftime("%Y-%m-%d"),
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(CODERABBIT_API_URL, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()


# ----------------------------------------------------------------------
# 2️⃣ LLM prompt builder (video‑mode)
# ----------------------------------------------------------------------
def build_video_prompt(insights: dict, llm: ChatGroq) -> str:
    if not llm:
        raise RuntimeError("LLM client not available")
    insight_str = json.dumps(insights, indent=2)
    system_prompt = (
        "You are a tech‑storyteller.  Write **ONE short paragraph** (≈30 words) "
        "that can be fed to an AI video generator to visualise the bugs / "
        "issues that were fixed.  Mention the repo name.  Do NOT add any on‑screen "
        "text, logos, or titles.\n\nInsights:\n" + insight_str
    )
    resp = llm.invoke(system_prompt)
    return resp.content.strip()


# ----------------------------------------------------------------------
# 3️⃣ Google Veo – now returns **raw MP4 bytes** (not a URL)
# ----------------------------------------------------------------------
def create_google_veo_video(prompt: str, api_key: str) -> bytes:
    """
    Calls Veo and returns the binary MP4 data.
    Raises RuntimeError on failure.
    """
    if not genai:
        raise RuntimeError("google‑genai library not installed")
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": "v1alpha"},
    )
    if not hasattr(client.models, "generate_videos"):
        raise RuntimeError("Veo endpoint not available for this key")

    # ---------- retry on quota errors ----------
    max_retries = 3
    operation = None
    for attempt in range(max_retries):
        try:
            operation = client.models.generate_videos(
                model="veo-2.0-generate-preview-0123",
                prompt=prompt,
                config=types.GenerateVideosConfig(number_of_videos=1),
            )
            break
        except Exception as exc:
            if "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc):
                if attempt < max_retries - 1:
                    backoff = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(backoff)
                    continue
            raise RuntimeError(f"Veo generation failed: {exc}") from exc

    if not operation:
        raise RuntimeError("Veo operation never started")

    # ---------- poll until video is ready ----------
    while not operation.done:
        time.sleep(5)

    if not operation.result:
        raise RuntimeError("Veo finished without a result")

    video_obj = operation.result.generated_videos[0]
    # Veo returns a protobuf “blob”.  Convert to plain bytes.
    if hasattr(video_obj.video, "blob"):
        return video_obj.video.blob          # <- raw MP4 bytes
    # Fallback: maybe Veo already gave us a URL – download it.
    if isinstance(video_obj.video, str):
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(video_obj.video)
            resp.raise_for_status()
            return resp.content
    raise RuntimeError("Unable to extract video bytes from Veo response")


# ----------------------------------------------------------------------
# 4️⃣ Pika Labs fallback – also returns raw MP4 bytes
# ----------------------------------------------------------------------
def create_pika_video(prompt: str, api_key: str) -> bytes:
    if not api_key:
        raise RuntimeError("Pika API key missing")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key.strip()}",
    }
    payload = {"prompt": prompt, "options": {"aspect_ratio": "16:9"}}
    with httpx.Client(timeout=30.0) as client:
        resp = client.post("https://api.pika.art/generate", headers=headers, json=payload)
        resp.raise_for_status()
        job_id = resp.json().get("id")
        if not job_id:
            raise RuntimeError("Pika did not return a job ID")

        # poll the job
        for _ in range(30):                 # ≈ 2.5 min max
            time.sleep(5)
            check = client.get(f"https://api.pika.art/generate/{job_id}", headers=headers)
            data = check.json()
            state = data.get("status")
            if state == "finished":
                # Pika returns a URL – download the file.
                video_url = data.get("video_url") or data.get("output", {}).get("url")
                if not video_url:
                    raise RuntimeError("Pika finished but gave no video URL")
                video_resp = client.get(video_url)
                video_resp.raise_for_status()
                return video_resp.content
            if state == "failed":
                raise RuntimeError(f"Pika failure: {data.get('error')}")
        raise RuntimeError("Pika video generation timed out")


# ----------------------------------------------------------------------
# 5️⃣ Public entry‑point – called from the FastAPI webhook.
# ----------------------------------------------------------------------
    # ---- 5️⃣ Return info for the webhook to write back ---------------
    return {
        "message": "✅ Autopilot finished – video ready",
        "artefact_id": str(artefact_doc["_id"]),
    }


# ----------------------------------------------------------------------
# 6️⃣ Together AI – Report Generation
# ----------------------------------------------------------------------
@retry_on_failure(max_retries=3, backoff_factor=2.0, exceptions=(httpx.HTTPError, httpx.TimeoutException))
def generate_together_report(insights: dict, api_key: str) -> str:
    if not api_key:
        raise RuntimeError("Together AI API key missing")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    insight_str = json.dumps(insights, indent=2)
    prompt = (
        "You are an expert DevOps consultant. Generate a concise, professional executive summary "
        "of the following bug analysis and fixes. Focus on the impact and improvements.\n\n"
        f"Insights:\n{insight_str}"
    )
    
    payload = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"]
    }
    
    with httpx.Client(timeout=30.0) as client:
        resp = client.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

# Update process_kestra_completion to include Together AI report
async def process_kestra_completion(
    *,
    repo_url: str,
    execution_id: str,
    user_email: str,
    db,                                   # Motor DB handle
) -> dict:
    """
    Orchestrates the post‑Kestra work:
    1. CodeRabbit insights
    2. Together AI report
    3. Video generation (Veo/Pika)
    4. Store everything in Mongo
    """
    # ---- 1️⃣ CodeRabbit -------------------------------------------------
    coderabbit_key = os.getenv("CODERABBIT_API_KEY")
    if not coderabbit_key:
        raise RuntimeError("CODERABBIT_API_KEY missing")
    insights = get_coderabbit_insights(repo_url, coderabbit_key)

    # ---- 2️⃣ Together AI Report -----------------------------------------
    together_key = os.getenv("TOGETHER_API_KEY")
    together_report = None
    if together_key:
        try:
            together_report = generate_together_report(insights, together_key)
        except Exception as exc:
            logging.error(f"Together AI report generation failed: {exc}")
            together_report = "Report generation failed."

    # ---- 3️⃣ LLM video‑prompt -------------------------------------------
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY missing")
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)
    video_prompt = build_video_prompt(insights, llm)

    # ---- 4️⃣ Generate video (Veo first, Pika fallback) ------------------
    video_bytes: bytes | None = None
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_KEY")
    if google_key:
        try:
            video_bytes = create_google_veo_video(video_prompt, google_key)
        except Exception as exc:
            logging.exception("Veo failed, will try Pika: %s", exc)

    if not video_bytes:
        pika_key = os.getenv("PIKA_API_KEY")
        if not pika_key:
            raise RuntimeError("No video provider key (Google or Pika) available")
        video_bytes = create_pika_video(video_prompt, pika_key)

    # ---- 5️⃣ Persist artefact (store binary data in Mongo) --------------
    artefact_doc = {
        "session": execution_id,
        "user_email": user_email,
        "repo_url": repo_url,
        "tool": "video_generation",
        "prompt": video_prompt,
        "video_bytes": video_bytes,          # <-- raw MP4 stored as BSON binary
        "report": together_report,           # <-- New Together AI report
        "status": "READY",
        "created_at": datetime.utcnow(),
    }
    await db["artefacts"].insert_one(artefact_doc)

    # ---- 6️⃣ Return info for the webhook to write back ---------------
    return {
        "message": "✅ Autopilot finished – video & report ready",
        "artefact_id": str(artefact_doc["_id"]),
    }
