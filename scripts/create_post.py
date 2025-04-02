"""
Create Blog Post from File (with Images)

This script reads an HTML file from a command line argument and posts its content to Blogger.

Usage:
    python create_post.py <html_file> [<post_title>]

Example:
    python create_post.py my_formatted_post.html "Exciting Update"

Requirements:
- Enable Blogger API in Google Cloud Console.
- Create OAuth Credentials (Desktop App) and download 'client_secret.json'.
- Install required Python libraries: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client.
- Place this script and 'client_secret_4676203276-kg4ui39sai1auibi9suofqels2sqcis4.apps.googleusercontent.com.json'
  in the same folder.

Including Images:
- Blogger doesn't allow direct image uploads via API.
- To include images, reference them in your HTML with <img> tags.
- Host images externally (e.g., Google Drive, Imgur, or your own server) and use the public URL.
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ==========================
# Configuration
# ==========================
SCOPES = ["https://www.googleapis.com/auth/blogger"]
# Use the same JSON file and naming as in blog_hello_world.py
CLIENT_SECRET_FILE = "client_secret_4676203276-kg4ui39sai1auibi9suofqels2sqcis4.apps.googleusercontent.com.json"
# Use the same BLOG_ID as in blog_hello_world.py
BLOG_ID = "5963855917365984730"

def authenticate():
    """
    Uses OAuth 2.0 InstalledAppFlow to get credentials,
    matching the blog_hello_world.py approach.
    """
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Error: {CLIENT_SECRET_FILE} not found in current directory.")
        sys.exit(1)

    # Match the blog_hello_world.py approach:
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES,
        redirect_uri="http://localhost"  # specify the same redirect URI
    )
    # Use a fixed port that is added in your Google Cloud Console's Authorized Redirect URIs
    creds = flow.run_local_server(port=8080)
    return creds

def create_blog_post_from_file(credentials, blog_id, title, file_path):
    """
    Reads HTML content from 'file_path' and creates a new post on Blogger.

    Images:
    - If you want to include images, embed <img> tags in the HTML.
    - Ensure those images are publicly accessible or they won't display.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Open the file with error handling for encoding issues
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            html_content = f.read()

    service = build("blogger", "v3", credentials=credentials)
    post_body = {
        "title": title,
        "content": html_content
    }

    post = service.posts().insert(blogId=blog_id, body=post_body).execute()
    print(f"✅ New post created: {post['url']}")

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python create_post.py <html_file> [<post_title>]")
        sys.exit(1)

    html_file_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "My Rich HTML Post"

    # 1. Authenticate and get credentials
    credentials = authenticate()

    # 2. Create the post
    create_blog_post_from_file(credentials, BLOG_ID, title, html_file_path)

