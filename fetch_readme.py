# coding: utf-8
"""
******************************************************************************
*  Copyright 2024 Thomas Reidemeister.                                       *
*                                                                            *
* Licensed under the Apache License, Version 2.0 (the "License");            *
* you may not use this project except in compliance with the License.        *
* You may obtain a copy of the License at                                    *
*                                                                            *
*     http://www.apache.org/licenses/LICENSE-2.0                             *
*                                                                            *
* Unless required by applicable law or agreed to in writing, software        *
* distributed under the License is distributed on an "AS IS" BASIS,          *
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   *
* See the License for the specific language governing permissions and        *
* limitations under the License.                                             *
******************************************************************************
"""
__author__ = "Thomas Reidemeister"

import argparse
import re
import json
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://dash.readme.com/api/v1"
TOKEN = ""

REQUESTS_TIMEOUT = 10

HEADERS = {
    "accept": "application/json",
}


def download_image(image_url, local_dir):
    # Extract the filename from the URL
    filename = image_url.split('/')[-1]
    local_path = Path(local_dir) / filename
    local_path.parent.mkdir(parents=True, exist_ok=True)

    # Download the image and save it to the local path
    response = requests.get(image_url, timeout=REQUESTS_TIMEOUT)
    if response.status_code == 200:
        with open(local_path, 'wb') as file:
            file.write(response.content)
        return local_path.name
    print(f"Failed to download {image_url}")
    return None


def replace_image_blocks_in_markdown(content, local_dir):
    # Define the regular expression pattern to match the specified text blocks
    pattern = r'\[block:image\]\n({.*?\n})\n\[/block\]'

    # Function to convert the matched block into Markdown image syntax
    def replacement(match):
        block_content = json.loads(match.group(1))
        markdown_images = ''

        for image in block_content['images']:
            image_url, _, caption = image['image']
            # Check if the image URL matches the specified prefix
            if image_url.startswith("https://files.readme.io/"):
                # Download the image and get the local path
                if (local_path := download_image(image_url, local_dir)) is not None:
                    # Use the local path in the Markdown image representation
                    markdown_image = f'![{caption}]({local_path})\n'
                    print(f"    * {local_path}")
                else:
                    # If download failed, use the original URL
                    markdown_image = f'![{caption}]({image_url})\n'
            else:
                markdown_image = f'![{caption}]({image_url})\n'
            markdown_images += markdown_image

        return markdown_images

    # Replace the matched blocks with their Markdown image representation
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    return updated_content


def get_categories():
    results = []
    counter = 1
    while True:
        url = f"{BASE_URL}/categories?perPage=100&page={counter}"
        response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(TOKEN, ''), timeout=REQUESTS_TIMEOUT)
        if response.status_code == 200:
            if len(response.json()) > 0:
                results += response.json()
                counter += 1
            else:
                return results
        else:
            return results


def get_all_documents_for_cat(slug):
    url = f"{BASE_URL}/categories/{slug}/docs"
    response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(TOKEN, ''), timeout=REQUESTS_TIMEOUT)
    if response.status_code == 200:
        return response.json()
    return []


def get_document_details(slug):
    url = f"{BASE_URL}/docs/{slug}"

    response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(TOKEN, ''), timeout=REQUESTS_TIMEOUT)
    if response.status_code == 200:
        document = response.json()
        return document
    return None


def process_markdown_links(markdown_content):
    # Regular expression to match markdown links of the form [description](link)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    def append_md_suffix(match):
        text, link = match.groups()
        # treat document references as relative links
        if link.startswith("doc:"):
            link = link[4:]

        # Split the link at "#" to handle fragment identifiers
        parts = link.split('#', 1)
        base = parts[0]
        fragment = '#' + parts[1] if len(parts) > 1 else ''

        # Check if the link is relative (doesn't start with http(s)) and doesn't contain a file extension
        if not base.startswith(('http:', 'https:')) and not '.' in base.split('/')[-1]:
            base += '.md'

        # Reassemble the link with ".md" before "#" if present
        link = base + fragment
        return f'[{text}]({link})'

    # Replace links in the markdown content using the append_md_suffix function
    processed_content = link_pattern.sub(append_md_suffix, markdown_content)
    return processed_content


def download_doc(cat_path, doc):
    item = get_document_details(doc['slug'])
    file_path = cat_path / Path(doc["slug"] + ".md")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    print(f" * Title: {item['title']}, Slug: {item['slug']}")
    with file_path.open("w") as file:
        file.write(f"# {item['title']}\n\n---\n\n")
        body = process_markdown_links(replace_image_blocks_in_markdown(item["body"], file_path.parent))
        file.write(body)
    # Recurse into children
    for child in doc["children"]:
        download_doc(cat_path, child)

def main(parent_path):
    for category in get_categories():
        print(f"Category: {category['title']}, Slug: {category['slug']}, Order: {category['order']}")
        cat_path = parent_path / Path(category['slug'])
        cat_path.mkdir(parents=True, exist_ok=True)

        docs = get_all_documents_for_cat(category['slug'])
        for doc in docs:
            download_doc(cat_path, doc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script to process and write markdown files for categories and documents.")
    parser.add_argument("--path", type=str, default="docs",
                        help="The parent path where the markdown files will be written. Defaults to 'docs'.")
    parser.add_argument("--token", type=str, default="", required=True,
                        help="Your Readme.io API token.")
    args = parser.parse_args()

    # Convert the path argument to a Path object
    target_path = Path(args.path)
    TOKEN = args.token
    main(target_path)