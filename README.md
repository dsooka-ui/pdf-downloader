# PDF Auto-Downloader

Zero-install, browser-only bulk PDF downloader using GitHub Actions.

## How it works
1. Paste URLs into `urls.txt` on GitHub
2. Click **Run workflow** in the Actions tab
3. GitHub downloads all PDFs and gives you a zip file

## Setup (one time)

1. Create a new repo on [github.com/new](https://github.com/new)
2. Name it anything (e.g. `pdf-downloader`)
3. Make it **Public**
4. Upload these 4 files:
   - `.github/workflows/download-pdfs.yml`
   - `download_pdfs.py`
   - `urls.txt`
   - `README.md`

> Click **"Add file" → "Upload files"** and drag all 4 in.

## Usage

1. Edit `urls.txt` (pencil icon) — one URL per line
2. Commit the change
3. Go to **Actions** → **Download PDFs** → **Run workflow**
4. Wait ~1–2 minutes, then download the `downloaded-pdfs` artifact
