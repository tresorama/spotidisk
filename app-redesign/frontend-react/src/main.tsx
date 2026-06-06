import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RootRoute, Router, RootRouteWithoutId } from '@tanstack/react-router'
import './index.css'

// Pages
import Layout from './pages/Layout'
import Home from './pages/Home'
import NotFound from './pages/NotFound'

// Setup React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
    },
  },
})

// Setup Router
const rootRoute = new RootRoute({
  component: Layout,
})

const homeRoute = new RootRouteWithoutId({
  getParentRoute: () => rootRoute,
  path: '/',
  component: Home,
})

const notFoundRoute = new RootRouteWithoutId({
  getParentRoute: () => rootRoute,
  path: '*',
  component: NotFound,
})

const routeTree = rootRoute.addChildren([homeRoute, notFoundRoute])

const router = new Router({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <router.RootComponent />
    </QueryClientProvider>
  </React.StrictMode>,
)
