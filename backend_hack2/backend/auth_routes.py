import os
from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from datetime import datetime
from database import get_user_collection, UserSchema

router = APIRouter()
oauth = OAuth()

# --- GitHub Config ---
# Ensure these are in your .env file
oauth.register(
    name='github',
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'repo user:email'},
)

# --- Routes ---

@router.get("/auth/github/login")
async def login_github(request: Request):
    """Redirects user to GitHub for login."""
    redirect_uri = request.url_for('auth_github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/auth/github/callback")
async def auth_github_callback(request: Request):
    """Handles the callback from GitHub."""
    try:
        # 1. Exchange code for access token
        token = await oauth.github.authorize_access_token(request)
        access_token = token.get('access_token')
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve access token")

        # 2. Get User Info from GitHub
        resp = await oauth.github.get('user', token=token)
        user_info = resp.json()
        
        # Handle email (sometimes it's private in GitHub)
        email = user_info.get('email')
        if not email:
            # Fallback: fetch emails specifically
            email_resp = await oauth.github.get('user/emails', token=token)
            emails = email_resp.json()
            primary_email = next((e for e in emails if e['primary']), emails[0])
            email = primary_email['email']

        # 3. Save/Update User in MongoDB
        users_col = get_user_collection()
        
        user_data = {
            "email": email,
            "full_name": user_info.get('name') or user_info.get('login'),
            "github_username": user_info.get('login'),
            "github_token": access_token,
            "last_login": datetime.utcnow()
        }
        
        # Upsert (Update if exists, Insert if new)
        await users_col.update_one(
            {"email": email},
            {"$set": user_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True
        )

        return {
            "status": "success", 
            "message": "Logged in via GitHub", 
            "user": email
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Auth Failed: {str(e)}")