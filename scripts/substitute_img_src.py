"""
substitute_img_src.py
----------------------

This script takes an HTML file with <img src="images/..."> tags and replaces the src attributes with corresponding Google Drive links.
It uses a `Gdrive.list` file located in the `images/` directory, which maps local image filenames to their Google Drive file IDs.

Example of Gdrive.list:
    image1.jpg (1AbcDeFgHiJkLmNoPqRsTuVwXyZ123456)
    image2.png (2BcDeFgHiJkLmNoPqRsTuVwXyZ654321)

Example usage:
    python substitute_img_src.py Nobel.html

This will create a new file called Nobel_Gdrive.html with updated image source links.
"""

import sys
import os
import re

def parse_gdrive_list(filepath):
    """Reads Gdrive.list and returns a mapping of image filename to file ID."""
    mapping = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r'(.+?)\s+\(([^)]+)\)', line.strip())
            if match:
                filename, file_id = match.groups()
                mapping[filename] = file_id
    return mapping

def substitute_img_src(html_content, gdrive_map):
    """Substitute the src attribute in img tags using the Blogger-compatible Google Drive image link."""
    def replacer(match):
        tag = match.group(0)
        src = match.group(1)
        filename = os.path.basename(src)
        if filename in gdrive_map:
            new_src = f'https://lh3.google.com/u/0/d/{gdrive_map[filename]}=s400'
            return tag.replace(src, new_src)
        return tag

    return re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', replacer, html_content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python substitute_img_src.py Nobel.html")
        sys.exit(1)

    html_file = sys.argv[1]
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    img_dir = os.path.join(os.path.dirname(html_file), "images")
    gdrive_list_path = os.path.join(img_dir, "Gdrive.list")

    if not os.path.isfile(gdrive_list_path):
        print(f"Error: Gdrive.list not found in {img_dir}")
        sys.exit(1)

    gdrive_map = parse_gdrive_list(gdrive_list_path)
    updated_html = substitute_img_src(html_content, gdrive_map)

    output_file = os.path.splitext(html_file)[0] + "_Gdrive.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(updated_html)

    print(f"Updated HTML saved to: {output_file}")

if __name__ == "__main__":
    main()
