import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../lib/api-client'

export default function Home() {
  const { data: playlists, isLoading, error } = useQuery({
    queryKey: ['playlists'],
    queryFn: () => apiClient.getPlaylists(),
  })

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="rounded-lg bg-surface p-8 text-center">
        <h2 className="mb-4 text-3xl font-bold">Welcome to Sunnify</h2>
        <p className="text-gray-400">
          Download your favorite tracks from Spotify and YouTube in one place
        </p>
      </div>

      {/* Playlists */}
      <section>
        <h3 className="mb-4 text-xl font-semibold">Your Playlists</h3>

        {isLoading && <p className="text-gray-400">Loading playlists...</p>}
        {error && (
          <p className="text-red-400">
            Error loading playlists. Make sure the backend is running.
          </p>
        )}

        {playlists && playlists.length === 0 && (
          <p className="text-gray-400">No playlists yet. Add one to get started.</p>
        )}

        {playlists && playlists.length > 0 && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {playlists.map((playlist) => (
              <div
                key={playlist.id}
                className="rounded-lg bg-surface p-4 hover:bg-surface-light transition"
              >
                {playlist.cover_url && (
                  <img
                    src={playlist.cover_url}
                    alt={playlist.name}
                    className="mb-4 h-32 w-full rounded object-cover"
                  />
                )}
                <h4 className="font-semibold">{playlist.name}</h4>
                <p className="text-sm text-gray-400">{playlist.owner}</p>
                <p className="mt-2 text-sm text-gray-500">
                  {playlist.total_tracks} tracks
                </p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Quick start */}
      <section className="rounded-lg bg-surface p-6">
        <h3 className="mb-4 text-lg font-semibold">Quick Start</h3>
        <ul className="space-y-2 text-sm text-gray-400">
          <li>✓ Add a Spotify playlist URL</li>
          <li>✓ Fetch tracks from Spotify</li>
          <li>✓ Find matching YouTube videos</li>
          <li>✓ Download and organize your music</li>
        </ul>
      </section>
    </div>
  )
}
