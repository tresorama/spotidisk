# Sunnify Redesign

Modern React + Python FastAPI rewrite of Sunnify with type-safe APIs.

## Architecture

```
┌──────────────────────────────┐
│   React + TypeScript         │
│   (Frontend) - Port 5173     │
└────────────────┬─────────────┘
                 │ HTTP REST API
┌────────────────▼─────────────┐
│   FastAPI (Backend)          │
│   (Python) - Port 8000       │
└──────────────────────────────┘
```

## Quick Start

### Backend

```bash
cd backend-python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Spotify credentials
python main.py
```

API available at: http://127.0.0.1:8000
Docs at: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend-react
npm install
npm run dev
```

App available at: http://localhost:5173

## Project Structure

```
app-redesign/
├── backend-python/           # FastAPI backend
│   ├── main.py              # App + endpoints
│   ├── models.py            # Pydantic models (API types)
│   ├── config.py            # Settings
│   ├── requirements.txt
│   └── README.md
├── frontend-react/           # React + Vite frontend
│   ├── src/
│   │   ├── lib/
│   │   │   └── api-client.ts  # API client (typed)
│   │   ├── pages/
│   │   │   ├── Layout.tsx
│   │   │   ├── Home.tsx
│   │   │   └── NotFound.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
└── README.md (this file)
```

## Development Notes

- **Type Safety**: Backend models (Python Pydantic) → Frontend types (TypeScript)
- **API Client**: Manually typed at `src/lib/api-client.ts` (can be auto-generated from OpenAPI)
- **State Management**: TanStack Query for server state
- **Routing**: TanStack Router for SPA navigation
- **Styling**: Tailwind CSS 4 + shadcn/ui ready

## Next Steps

1. Implement backend endpoints (integrate existing Python code)
2. Build frontend pages (Playlists, SongTable, Download UI)
3. Add WebSocket for real-time progress
4. Setup Electron for desktop app
5. Auto-generate TypeScript types from OpenAPI spec

## Original App

The original PyQt5 desktop app remains at the root directory and continues to work independently.
