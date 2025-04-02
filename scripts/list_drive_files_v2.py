#!/usr/bin/env python3
"""
Google Drive File Lister with local-path-to-folder-ID resolution

This script authenticates a user via OAuth2 and lists files from a folder in Google Drive.

Usage:
    python list_drive_files.py [LOCAL_PATH]

If LOCAL_PATH is provided (relative or absolute within the Google Drive desktop-mount),
the script attempts to traverse the folder tree by matching each directory name in Google Drive.
If not provided, it lists files from the Drive root.

Requirements:
    - credentials.json must be in the same directory as this script.
    - Google API client libraries must be installed:
        pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Note:
    This approach relies on folder names in the local path matching exactly the corresponding
    Google Drive folder names. If multiple folders share the same name at a level, the first
    encountered in the Drive API listing is used.
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Drive API configuration
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')


def authenticate_drive():
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(
        CREDS_FILE,
        SCOPES,
        redirect_uri='http://localhost:8080'  # Must match what’s in your OAuth client settings
    )
    # run_local_server can open a browser automatically, but you can disable if WSL can't open
    creds = flow.run_local_server(port=8080, open_browser=False)
    return creds


def resolve_local_path_to_folder_id(service, local_path):
    """
    Given a local path (string), attempt to find the corresponding folder ID in Drive by:
    1. Splitting the path into components.
    2. Starting from 'root', searching for a folder with each component's name.
    3. Descending one level at a time.

    Returns the folder ID if found, or None if any component is not found.
    """
    abs_path = os.path.abspath(local_path)
    relative_path = os.path.relpath(abs_path, os.getcwd())

    if relative_path == '.' or not relative_path:
        return 'root'

    components = [comp for comp in relative_path.split(os.sep) if comp not in ('.', '..', '')]
    folder_id = 'root'

    for comp in components:
        query = f"'{folder_id}' in parents and name = '{comp}' and mimeType = 'application/vnd.google-apps.folder'"
        response = service.files().list(q=query, fields='files(id, name)').execute()
        folders = response.get('files', [])

        if not folders:
            print(f"Folder '{comp}' not found under parent ID '{folder_id}'.")
            return None
        folder_id = folders[0]['id']

    return folder_id

def list_drive_files(creds, folder_id=None, num_files=20):
    """Lists up to num_files from the specified folder_id in Google Drive (or root if None)."""
    service = build('drive', 'v3', credentials=creds)
    query = f"'{folder_id}' in parents" if folder_id and folder_id != 'root' else None

    results = service.files().list(
        q=query,
        pageSize=num_files,
        fields="nextPageToken, files(id, name)"
    ).execute()

    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print(f"Listing up to {num_files} items from folder ID: {folder_id if folder_id else 'root'}")
        for item in items:
            print(f"{item['name']} ({item['id']})")

if __name__ == '__main__':
    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)

    local_path = sys.argv[1] if len(sys.argv) > 1 else None
    if local_path:
        print(f"Attempting to resolve local path: {local_path}")
        folder_id = resolve_local_path_to_folder_id(service, local_path)
        if folder_id:
            list_drive_files(creds, folder_id)
        else:
            print("Could not resolve the provided path to a Drive folder ID.")
    else:
        # No path provided: Just list from root
        list_drive_files(creds, folder_id='root')
