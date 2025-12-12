import os
import time
import json
import random
import streamlit as st
import httpx
import dotenv
from typing import Optional

# --- Load environment variables ---
env_path = dotenv.find_dotenv()
if env_path:
    dotenv.load_dotenv(env_path)

# --- Optional Imports with robust guards ---
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

# Google GenAI (New SDK)
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

# --- Configuration & Constants ---
ST_PAGE_TITLE = "🤖 Repo Insight Agent"
# NOTE: This endpoint requires an official API key from Pika's enterprise/partner API.
# If you are using a reverse-engineered wrapper, you may need to change this URL.
PIKA_API_URL = "https://api.pika.art/generate" 
CODERABBIT_API_URL = "https://api.coderabbit.ai/api/v1/report.generate"

# --- Helper functions ---

def get_api_key(label: str, env_keys) -> str:
    """Get API key from environment or sidebar input."""
    if isinstance(env_keys, str):
        env_keys = [env_keys]
    
    initial_value = ""
    for k in env_keys:
        v = os.getenv(k)
        if v:
            initial_value = v
            break
            
    # If found in env, mask it in UI but allow overwrite
    display_val = initial_value if initial_value else ""
    return st.sidebar.text_input(label, value=display_val, type="password")

def get_coderabbit_insights(repo_url: str, api_key: str) -> Optional[dict]:
    """Call CodeRabbit to generate a report."""
    if not api_key:
        return None
        
    headers = {
        "Content-Type": "application/json",
        "x-coderabbitai-api-key": api_key
    }
    # Dynamic window: last 14 days
    data = {
        "repository": repo_url,
        "from": "2024-05-01", 
        "to": "2024-05-15"
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(CODERABBIT_API_URL, headers=headers, json=data)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        st.error(f"CodeRabbit API failed: {e}")
        return None

def transcribe_audio(audio_file, api_key: str) -> str:
    """Transcribe using Groq Whisper."""
    if not api_key or not audio_file:
        return ""

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        # Check if it's a file uploader object or audio_input object
        filename = "audio.wav"
        if hasattr(audio_file, "name"):
            filename = audio_file.name
            
        files = {"file": (filename, audio_file, "audio/mpeg")}
        data = {"model": "whisper-large-v3", "response_format": "json"}

        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, headers=headers, files=files, data=data)
            resp.raise_for_status()
            return resp.json().get("text", "")
    except Exception as e:
        st.warning(f"Transcription failed: {e}")
        return ""

def generate_elevenlabs_audio(text: str, api_key: str) -> Optional[bytes]:
    """Generate audio via ElevenLabs."""
    if not api_key:
        st.error("Missing ElevenLabs API Key.")
        return None

    voice_id = "21m00Tcm4TlvDq8ikWAM" # Rachel
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.content
    except Exception as e:
        st.error(f"ElevenLabs error: {e}")
        return None

def summarize_with_llm(insights: dict, llm, mode="report", instructions="") -> str:
    """Generate specific content based on mode using LLM."""
    
    insight_str = json.dumps(insights, indent=2) if isinstance(insights, dict) else str(insights)
    
    prompts = {
        "report": "Convert this code analysis into a Markdown release note with 'Key Changes', 'Fixes', and 'Performance'.",
        "audio": "Write a 2-sentence conversational script for a developer update podcast about these changes.",
        "video": "Write a concise, single-paragraph AI video prompt describing a visual representation of these code changes. Focus on: abstract tech visualization, bugs being squashed, stability. No text overlays."
    }
    
    system_prompt = (
        f"You are a tech assistant. {prompts.get(mode, 'Summarize this.')}\n"
        f"User Instructions: {instructions}\n\n"
        f"Report Data:\n{insight_str}"
    )

    if llm:
        try:
            response = llm.invoke(system_prompt)
            return response.content
        except Exception as e:
            st.warning(f"LLM generation failed ({e}), using fallback.")
    
    # Fallback
    return f"Summary of changes: {str(insights)[:200]}..."

def create_google_veo_video(prompt: str, api_key: str):
    """Generate video using Google Veo (genai SDK) with robust 429/Quota handling."""
    if not genai:
        st.error("`google-genai` library not installed.")
        return

    try:
        # FIX 1: Explicitly request 'v1alpha' to access generate_videos
        client = genai.Client(
            api_key=api_key, 
            http_options={'api_version': 'v1alpha'}
        )
        
        # Double check capability
        if not hasattr(client.models, "generate_videos"):
            st.error("Even with v1alpha, `generate_videos` is missing. Your API Key may not have access to Veo/Trusted Tester program yet.")
            return

        with st.status("🎬 Rendering video with Google Veo...", expanded=True) as status:
            status.write("Sending prompt to Google Cloud (v1alpha)...")
            
            # FIX 2: RETRY LOGIC FOR 429 ERRORS
            max_retries = 3
            operation = None
            
            for attempt in range(max_retries):
                try:
                    operation = client.models.generate_videos(
                        model="veo-2.0-generate-preview-0123", 
                        prompt=prompt,
                        config=types.GenerateVideosConfig(number_of_videos=1)
                    )
                    break # Success, exit loop
                except Exception as e:
                    error_msg = str(e)
                    # Check for 429 Resource Exhausted
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) + random.uniform(0, 1) # Exponential backoff
                            status.write(f"Rate limit hit. Retrying in {wait_time:.1f} seconds...")
                            time.sleep(wait_time)
                            continue
                    # If it's not a 429, or we ran out of retries, re-raise
                    raise e
            
            if not operation:
                st.error("Failed to start video generation after retries.")
                return

            status.write(f"Operation started. Polling for result... (This takes ~60s)")
            
            # Polling logic
            while not operation.done:
                time.sleep(5)
            
            if operation.result:
                generated_video = operation.result.generated_videos[0]
                video_data = generated_video.video
                
                # Handle bytes vs URL
                if hasattr(video_data, "blob"):
                    video_bytes = video_data.blob
                else:
                    video_bytes = video_data
                    
                st.video(video_bytes)
                status.update(label="✅ Video Generated!", state="complete", expanded=False)
            else:
                status.update(label="❌ Generation failed", state="error")
                st.error("No result returned from Veo.")

    except Exception as e:
        st.error(f"Veo Error: {e}")
        # Detailed advice for common errors
        if "RESOURCE_EXHAUSTED" in str(e):
             st.warning(
                "⚠️ **Quota Limit Reached:** You have likely hit the **Daily Limit** for Veo. "
                "The Free/Preview tier allows very few videos per day. "
                "Try again in 24 hours or enable Billing on Google Cloud."
            )
        elif "404" in str(e):
            st.warning("Model not found. Try changing the model name in the code to 'veo-001-preview'.")

def create_pika_video(prompt: str, api_key: str):
    """Generate video using Pika Labs with 401 Debugging."""
    
    # Clean the key in case of accidental spaces
    clean_key = api_key.strip() if api_key else ""
    
    if not clean_key:
        st.error("⚠️ Pika API Key is empty. Please enter it in the sidebar.")
        return

    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {clean_key}"
    }
    payload = {"prompt": prompt, "options": {"aspect_ratio": "16:9"}}

    with st.status("🎬 Rendering with Pika...", expanded=True) as status:
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(PIKA_API_URL, headers=headers, json=payload)
                resp.raise_for_status()
                job_id = resp.json().get("id")
            
            if not job_id:
                raise ValueError("No Job ID returned from Pika")

            # Polling
            for _ in range(30): # 2.5 minutes max
                time.sleep(5)
                with httpx.Client(timeout=30.0) as client:
                    check = client.get(f"{PIKA_API_URL}/{job_id}", headers=headers)
                    data = check.json()
                    
                state = data.get("status")
                if state == "finished":
                    video_url = data.get("video_url") or data.get("output", {}).get("url")
                    st.video(video_url)
                    status.update(label="✅ Pika Video Ready!", state="complete")
                    return
                elif state == "failed":
                    raise Exception(f"Pika reported failure: {data.get('error')}")
            
            status.update(label="⚠️ Timed out", state="error")
            st.warning("Pika is taking too long. Check dashboard.")
            
        except httpx.HTTPStatusError as e:
            status.update(label="❌ API Error", state="error")
            st.error(f"Pika API Error: {e}")
            if e.response.status_code == 401:
                st.error("🚫 **401 Unauthorized:** Your Pika API Key is invalid.")
                st.markdown("""
                **Possible fixes:**
                1. Ensure you copied the full key without spaces.
                2. Note: Beta Discord bot keys **do not work** here. You need a Web API key.
                3. Your subscription may have expired.
                """)
        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(f"Pika failed: {e}")

# --- Main App ---

def main():
    st.set_page_config(page_title="Repo Agent", layout="wide", page_icon="🤖")
    
    # Initialize Session State
    if "insights" not in st.session_state:
        st.session_state.insights = None
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False

    st.title(ST_PAGE_TITLE)

    # --- Sidebar ---
    with st.sidebar:
        st.header("🔑 API Credentials")
        coderabbit_key = get_api_key("CodeRabbit Key", ["CODERABBIT_API_KEY"])
        groq_key = get_api_key("Groq Key", ["GROQ_API_KEY"])
        google_key = get_api_key("Google GenAI Key", ["GOOGLE_API_KEY", "GOOGLE_GENAI_KEY"])
        pika_key = get_api_key("Pika Key", ["PIKA_API_KEY"])
        eleven_key = get_api_key("ElevenLabs Key", ["ELEVENLABS_API_KEY"])
        
        st.divider()
        st.info("Ensure you have `google-genai` >= 0.4.0 installed for Veo.")

    # --- Top Section: Inputs ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        repo_url = st.text_input("Git Repository URL", placeholder="https://github.com/owner/repo")
    
    with col2:
        # Audio instructions (Streamlit 1.40+)
        audio_inst = None
        if hasattr(st, "audio_input"):
            audio_inst = st.audio_input("Voice Instructions (Optional)")
        else:
            st.caption("Upgrade Streamlit to use Voice Input")

    # --- Step 1: Analyze ---
    if st.button("🚀 Analyze Repository", type="primary", use_container_width=True):
        if not repo_url:
            st.toast("Please enter a URL", icon="⚠️")
        else:
            with st.spinner("Analyzing code changes..."):
                # Transcribe instructions if present
                transcript = ""
                if audio_inst and groq_key:
                    transcript = transcribe_audio(audio_inst, groq_key)
                    st.session_state.instructions = transcript
                else:
                    st.session_state.instructions = ""

                # Fetch Insights
                if coderabbit_key:
                    insights = get_coderabbit_insights(repo_url, coderabbit_key)
                else:
                    # Mock for demo
                    time.sleep(1) 
                    insights = {
                        "summary": "Refactored the authentication middleware to use JWT. Fixed a critical SQL injection vulnerability in the login route. Improved Docker build time by 40%.",
                        "files_changed": ["auth.py", "Dockerfile", "routes/login.py"]
                    }
                    st.toast("Using Mock Data (No CodeRabbit Key)", icon="ℹ️")
                
                st.session_state.insights = insights
                st.session_state.analysis_complete = True
                st.rerun()

    # --- Step 2: Generate Outputs ---
    if st.session_state.analysis_complete and st.session_state.insights:
        st.divider()
        st.subheader("📦 Analysis Results")
        
        # Display Raw Summary context
        with st.expander("View Raw Insights", expanded=False):
            st.json(st.session_state.insights)
            if st.session_state.instructions:
                st.info(f"Context applied: {st.session_state.instructions}")

        # Initialize LLM
        llm = None
        if ChatGroq and groq_key:
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)

        # Tabs for Output Modes
        tab_report, tab_audio, tab_video = st.tabs(["📄 Report", "🎙️ Audio Briefing", "🎬 Video Gen"])

        with tab_report:
            if st.button("Generate Markdown Report"):
                report = summarize_with_llm(st.session_state.insights, llm, "report", st.session_state.instructions)
                st.markdown(report)
                st.download_button("Download .md", report, file_name="release_notes.md")

        with tab_audio:
            if st.button("Generate Audio Briefing"):
                script = summarize_with_llm(st.session_state.insights, llm, "audio", st.session_state.instructions)
                st.caption(f"Script: {script}")
                if eleven_key:
                    audio_bytes = generate_elevenlabs_audio(script, eleven_key)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.error("ElevenLabs Key required.")

        with tab_video:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown("#### Google Veo")
                if st.button("Generate with Veo"):
                    if not google_key:
                        st.error("Google Key required")
                    else:
                        prompt = summarize_with_llm(st.session_state.insights, llm, "video", st.session_state.instructions)
                        create_google_veo_video(prompt, google_key)
            
            with col_v2:
                st.markdown("#### Pika Labs")
                if st.button("Generate with Pika"):
                    # Pass the key from sidebar directly to function
                    if not pika_key:
                        st.error("Pika Key required")
                    else:
                        prompt = summarize_with_llm(st.session_state.insights, llm, "video", st.session_state.instructions)
                        create_pika_video(prompt, pika_key)

if __name__ == "__main__":
    main()