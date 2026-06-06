# Sunnify Backend (Python)

FastAPI backend for Sunnify - Spotify & YouTube music downloader.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your Spotify API credentials:
- Get them from https://developer.spotify.com/dashboard

## Run

```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API docs available at: http://localhost:8000/docs

## Project Structure

```
backend-python/
├── main.py           # FastAPI app + endpoints
├── config.py         # Settings from .env
├── models.py         # Pydantic models for API
├── requirements.txt
├── .env.example
└── README.md
```

## TODO

- [ ] Implement playlist fetching from Spotify
- [ ] Implement download with yt-dlp
- [ ] Implement metadata management
- [ ] Implement ID3 tags reading/writing
- [ ] WebSocket for progress updates
- [ ] Config file (JSON) persistence
