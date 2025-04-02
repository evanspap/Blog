#!/usr/bin/env python3
"""
Google Drive File Lister

This script authenticates a user via OAuth2 and lists files from their Google Drive.

Usage:
    python list_drive_files.py

Description:
    This script lists the first 20 files in the user's Google Drive root directory.

Requirements:
    - credentials.json must be in the same directory as this script.
    - Google API client libraries must be installed:
        pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Google Drive API configuration
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
# Get the directory where the current script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')

def authenticate_drive():
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDS_FILE,
        SCOPES,
        redirect_uri='http://localhost:8080'
    )
    creds = flow.run_local_server(port=8080)
    return creds

def list_drive_files(creds, num_files=20):
    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(
        pageSize=num_files,
        fields="nextPageToken, files(id, name)"
    ).execute()

    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files and IDs:')
        for item in items:
            print(f"{item['name']} ({item['id']})")

if __name__ == '__main__':
    creds = authenticate_drive()
    list_drive_files(creds)