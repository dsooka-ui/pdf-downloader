#!/usr/bin/env python3
"""
GitHub Actions PDF downloader.
Reads urls.txt, finds PDFs, downloads them to /downloads.
"""
import os
import sys
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

URLS_FILE = "urls.txt"
OUTPUT_DIR = "downloads"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def sanitize(name):
    bad = '\\/:*?"<>|'
    for c in bad:
        name = name.replace(c, '_')
    name = name.replace(' ', '_')
    return name.strip('._') or 'file'


def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        r.raise_for_status()
        return r
    except Exception as e:
        print("  FAILED: %s — %s" % (url, e))
        return None


def extract_pdf_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.path.lower().endswith(".pdf") or ".pdf" in parsed.query.lower():
            links.add(absolute)
    return links


def download_file(url, folder, idx):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        r.raise_for_status()
    except Exception as e:
        print("  Download error: %s" % e)
        return None

    fname = None
    cd = r.headers.get("Content-Disposition", "")
    if "filename=" in cd:
        fname = cd.split("filename=")[-1]
        fname = fname.strip()
        if len(fname) > 1:
            if fname[0] == fname[-1] and fname[0] in ('"', "'"):
                fname = fname[1:-1]

    if not fname:
        path = urlparse(url).path
        fname = os.path.basename(path) or ("file_%d" % idx)
        if not fname.lower().endswith(".pdf"):
            fname += ".pdf"

    fname = sanitize(fname)
    fname = "%02d_%s" % (idx, fname)
    filepath = os.path.join(folder, fname)

    with open(filepath, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    size = os.path.getsize(filepath) / 1024
    print("  Saved: %s (%.1f KB)" % (fname, size))
    return filepath


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(URLS_FILE):
        print("ERROR: %s not found." % URLS_FILE)
        sys.exit(1)

    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print("Found %d URL(s) in %s\n" % (len(urls), URLS_FILE))
    downloaded = 0

    for i, url in enumerate(urls, start=1):
        print("[%d/%d] %s" % (i, len(urls), url))
        parsed = urlparse(url)
        is_direct = parsed.path.lower().endswith(".pdf")

        if is_direct:
            pdf_urls = {url}
        else:
            resp = fetch(url)
            if resp is None:
                continue
            pdf_urls = extract_pdf_links(resp.text, resp.url)

        if not pdf_urls:
            print("  No PDF links found.")
            continue

        print("  %d PDF link(s) found" % len(pdf_urls))
        for pdf_url in sorted(pdf_urls):
            downloaded += 1
            download_file(pdf_url, OUTPUT_DIR, downloaded)

    print("\n" + "=" * 50)
    print("DONE. Total PDFs downloaded: %d" % downloaded)
    print("Saved to: %s/" % OUTPUT_DIR)


if __name__ == "__main__":
    main()
