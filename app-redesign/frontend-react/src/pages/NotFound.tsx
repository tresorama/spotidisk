import { Link } from '@tanstack/react-router'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh]">
      <h1 className="text-4xl font-bold mb-2">404</h1>
      <p className="text-gray-400 mb-6">Page not found</p>
      <Link
        to="/"
        className="px-4 py-2 bg-spotify text-white rounded hover:bg-opacity-90 transition"
      >
        Go Home
      </Link>
    </div>
  )
}
