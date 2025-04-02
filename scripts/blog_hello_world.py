"""
Blogger API Post Example

This script authenticates with Google OAuth 2.0 and posts a new blog entry to Blogger using the Blogger API.

Requirements:
- Enable Blogger API in Google Cloud Console.
- Create OAuth Credentials (Desktop App) and download `client_secret.json`.
- Ensure that `http://localhost` and `http://localhost:8080` are added as Authorized Redirect URIs in Google Cloud Console.
- Install required Python libraries: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`.

Usage:
Run the script to authenticate and create a new blog post titled 'Hello World'.
"""

import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 🔹 Replace with your Blog ID from Blogger
BLOG_ID = "5963855917365984730"  # Blog ID from your Blogger URL

# 🔹 Define API Scope (Full Blogger Access)
SCOPES = ["https://www.googleapis.com/auth/blogger"]

# 🔹 Update JSON file name (keep your original file)
CLIENT_SECRET_FILE = "client_secret_4676203276-kg4ui39sai1auibi9suofqels2sqcis4.apps.googleusercontent.com.json"

def authenticate():
    """Handles OAuth authentication and returns credentials."""
    creds = None
    # Ensure the correct JSON file exists
    if os.path.exists(CLIENT_SECRET_FILE):
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE, SCOPES, redirect_uri="http://localhost"
        )
        creds = flow.run_local_server(port=8080)  # Use a fixed port to match the redirect URI
    else:
        print(f"❌ Error: '{CLIENT_SECRET_FILE}' file not found. Check your Google API credentials.")
        exit()
    
    return creds

def create_blog_post(credentials, blog_id, title, content):
    """Posts a new blog entry to Blogger."""
    service = build("blogger", "v3", credentials=credentials)
    
    post_body = {
        "title": title,
        "content": content
    }

    post = service.posts().insert(blogId=blog_id, body=post_body).execute()
    print(f"✅ New post created: {post['url']}")

# 🔹 Authenticate and get credentials
credentials = authenticate()

# 🔹 Create a new post
create_blog_post(credentials, BLOG_ID, "Hello World", "<p>🚀 This is my first post via API on Blogger!</p>")

