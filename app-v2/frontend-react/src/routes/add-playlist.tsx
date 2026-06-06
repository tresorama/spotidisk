import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/add-playlist')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/add-playlist"!</div>
}
