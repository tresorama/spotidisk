# SpotiDisk

Desktop app for downloading Spotify playlists to MP3 files on you computer.
- `Spotify Public Playlist` -> Source of truth
- `Youtube` -> Audio source

## Folders

- `app-v1` - not working (anymore) prototype, vibecoded edits on top of [sunnify](https://github.com/sunnypatell/sunnify-spotify-downloader)
- `app-v2` - stable version of the app (Backend: Python, Frontend: React)
  - `backend-python` - Python backend (FastAPI + OpenAPI)
  - `frontend-react` - React frontend (Vite + TS + React + tanstack-router + kubb OpenAPI client + tanstack-query)
  - `electron-builder` - Electron app builder for bundling the app into single executable
  - `test-e2e` - E2E tests (playwright)
  - `guides` - Guides and documentation for Devs

## Credits

- [Sunnify](https://github.com/sunnypatell/sunnify-spotify-downloader) this project recycled some code from this repo.