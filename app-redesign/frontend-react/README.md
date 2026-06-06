# Sunnify Frontend (React)

Modern React + TypeScript frontend for Sunnify music downloader.

## Stack

- **Vite**: Lightning-fast bundler
- **React 18**: UI framework
- **TypeScript**: Type safety
- **TanStack Router**: Client-side SPA routing
- **TanStack Query**: Server state management
- **Tailwind CSS 4**: Utility-first styling
- **shadcn/ui**: Headless components (ready to add)

## Setup

```bash
npm install
```

## Development

```bash
# Terminal 1: Backend (Python)
cd ../backend-python
python main.py

# Terminal 2: Frontend (React)
npm run dev
```

Open http://localhost:5173

API calls proxy to http://127.0.0.1:8000 via Vite config.

## Build

```bash
npm run build
npm run preview
```

## Type Safety

API types are manually maintained in `src/lib/api-client.ts`. 
Eventually, these should be generated from the backend's OpenAPI spec:

```bash
npx swagger-typescript-api \
  --url http://localhost:8000/openapi.json \
  --output ./src/api
```

## Project Structure

```
frontend-react/
├── src/
│   ├── lib/
│   │   └── api-client.ts      # API types and client
│   ├── pages/
│   │   ├── Layout.tsx         # Root layout
│   │   ├── Home.tsx           # Home page
│   │   └── NotFound.tsx       # 404 page
│   ├── index.css              # Tailwind imports
│   └── main.tsx               # Router + Query setup
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## TODO

- [ ] Add shadcn/ui components (Button, Card, Dialog, etc)
- [ ] Create Playlist list page
- [ ] Create Playlist detail page with song table
- [ ] Create Download progress UI
- [ ] WebSocket integration for real-time progress
- [ ] ID3 tag editor modal
- [ ] Settings page
