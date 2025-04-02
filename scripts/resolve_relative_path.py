#!/usr/bin/env python3
"""
Given a top-level mounted Google Drive path and a full absolute local path,
this script will extract and print the path relative to the mount root.

Usage:
    python resolve_relative_path.py <TOP_MOUNTED_DRIVE_PATH> <FULL_PATH_TO_FOLDER>

Example:
    python resolve_relative_path.py /home/evan/GdriveMagnes /home/evan/GdriveMagnes/Github/Private/Blog
    Output: Github/Private/Blog

This is useful for mapping WSL-mounted Google Drive paths to
Google Drive folder trees based on name.
"""

import os
import sys

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

def main():
    if len(sys.argv) != 3:
        print("Usage: python resolve_relative_path.py <TOP_MOUNTED_DRIVE_PATH> <FULL_PATH_TO_FOLDER>")
        sys.exit(1)

    top_mount = sys.argv[1]
    full_path = sys.argv[2]

    try:
        relative = get_relative_drive_path(top_mount, full_path)
        print(f"Relative path: {relative}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()