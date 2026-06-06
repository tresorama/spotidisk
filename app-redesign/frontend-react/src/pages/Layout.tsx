import { Outlet } from '@tanstack/react-router'

export default function Layout() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-surface-light bg-surface">
        <div className="mx-auto max-w-7xl px-4 py-4">
          <h1 className="text-2xl font-bold text-spotify">Sunnify</h1>
          <p className="text-sm text-gray-400">Spotify & YouTube Music Downloader</p>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-7xl px-4 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-light bg-surface py-4">
        <div className="mx-auto max-w-7xl px-4 text-center text-sm text-gray-500">
          <p>v2.1.0 • Educational project • Desktop app</p>
        </div>
      </footer>
    </div>
  )
}
