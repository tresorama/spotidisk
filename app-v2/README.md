# SpotiDisk

Modern React + Python FastAPI rewrite of Sunnify.

## Architecture

```
┌──────────────────────────────┐
│   React + TypeScript         │
│   (Frontend) - Port 3000     │
└────────────────┬─────────────┘
                 │ HTTP REST API/OpenAPI
┌────────────────▼─────────────┐
│   FastAPI (Backend)          │
│   (Python) - Port 8000       │
└──────────────────────────────┘
```
