# blogger-image

A Python tool to upload images to **Google Blogger** using the resumable upload API, authenticated via Google OAuth2.

---

## Features

- OAuth2 authentication with automatic token refresh
- Resumable image upload to Blogger's photo storage
- Returns a direct, full-resolution image URL ready to embed in posts
- Session-based requests with retry logic (up to 30 attempts)

---

## Requirements

- Python 3.7+
- A Google Cloud project with the **Blogger API v3** enabled
- OAuth2 credentials (`credentials.json`) from the [Google Cloud Console](https://console.cloud.google.com/)

---

## Installation

```bash
git clone https://github.com/Kurdeus/blogger-image.git
cd blogger-image
pip install -r requirements.txt
```

---

## Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable the **Blogger API v3**.
3. Create **OAuth 2.0 Client ID** credentials (Desktop app type).
4. Publish your project.
5. Download the credentials and save them as `credentials.json` in the project root.

---

## Usage

```python
from main import Blogger

uploader = Blogger("./your-image.png")
url = uploader.upload()
print(url)  # Direct image URL
```



> On first run, a browser window will open for Google OAuth2 authorization. The token is saved to `token.pickle` for subsequent runs.

---

## How It Works

1. **Authentication** — Loads or refreshes credentials from `token.pickle`. If none exist, opens a browser for OAuth2 login.
2. **Get Upload URL** — Requests a resumable upload session from Google's upload endpoint.
3. **Upload** — Sends the image binary in a single request and extracts the resulting public URL.

---

## File Structure

```
blogger-image/
├── main.py            # Core Blogger uploader class
├── credentials.json   # OAuth2 client credentials (not committed)
├── token.pickle       # Saved auth token (auto-generated, not committed)
├── requirements.txt
└── README.md
```

---

## Notes

- Only `credentials.json` is needed to get started — `token.pickle` is generated automatically.
- Add both `credentials.json` and `token.pickle` to your `.gitignore` to keep them out of version control.
- The tool currently supports `image/png` uploads; modify the `content-type` headers in `upload()` for other formats.

---

## License

MIT