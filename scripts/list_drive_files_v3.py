#!/usr/bin/env python3
"""
Google Drive File Lister with local-path-to-folder-ID resolution

This script authenticates a user via OAuth2 and lists files from a folder in Google Drive.

Usage:
    python list_drive_files_v3.py <TOP_MOUNTED_DRIVE_PATH> <FULL_PATH_TO_FOLDER>

Example:
    python list_drive_files_v3.py /home/evan/GdriveMagnes /home/evan/GdriveMagnes/Github/Private/Blog/HTML/2025/Nobel_save/images

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


def get_relative_drive_path(top_mount_path, full_path):
    """
    Returns the relative path from the top_mount_path to the full_path.
    If full_path does not start with top_mount_path, raises ValueError.
    """
    full_path = os.path.abspath(full_path)
    top_mount_path = os.path.abspath(top_mount_path)

    if not full_path.startswith(top_mount_path):
        raise ValueError(f"Path '{full_path}' is not under mount root '{top_mount_path}'")

    relative_path = os.path.relpath(full_path, top_mount_path)
    return relative_path


def authenticate_drive():
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDS_FILE,
        SCOPES,
        redirect_uri='http://localhost:8080'
    )
    creds = flow.run_local_server(port=8080, open_browser=True)
    return creds


def resolve_local_path_to_folder_id(service, relative_path):
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
    service = build('drive', 'v3', credentials=creds)
    query = f"'{folder_id}' in parents" if folder_id and folder_id != 'root' else None

    results = service.files().list(
        q=query,
        pageSize=num_files,
        fields="nextPageToken, files(id, name)"
    ).execute()

    items = results.get('files', [])
    return items


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python list_drive_files_v3.py <TOP_MOUNTED_DRIVE_PATH> <FULL_PATH_TO_FOLDER>")
        sys.exit(1)

    top_mount = sys.argv[1]
    full_path = sys.argv[2]

    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)

    try:
        relative_path = get_relative_drive_path(top_mount, full_path)
        print(f"Resolved relative path: {relative_path}")

        folder_id = resolve_local_path_to_folder_id(service, relative_path)
        if folder_id:
            items = list_drive_files(creds, folder_id)
            output_file = os.path.join(full_path, 'Gdrive.list')
            with open(output_file, 'w') as f:
                for item in items:
                    line = f"{item['name']} ({item['id']})\n"
                    print(line.strip())
                    f.write(line)
            print(f"File list saved to: {output_file}")
        else:
            print("Could not resolve the provided path to a Drive folder ID.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
