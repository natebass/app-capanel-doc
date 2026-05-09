import { QueryClient } from '@tanstack/react-query'
import { createRouter, RouterProvider } from '@tanstack/react-router'
import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'

import { DefaultError } from '@/components/common/status/DefaultError'
import { DefaultNotFound } from '@/components/common/status/DefaultNotFound'

import './globals.css'
import { client } from './lib/client/client.gen'
import { routeTree } from './routeTree.gen'

const trimTrailingSlash = (value: string): string => value.replace(/\/+$/, '')

const normalizeApiBaseUrl = (value: string | undefined): string | undefined => {
	if (!value) return
	const trimmed = trimTrailingSlash(value.trim())
	if (!trimmed || trimmed === '/api' || trimmed === '/api/v1') return
	if (trimmed.endsWith('/api/v1')) return trimmed.slice(0, -7)
	if (trimmed.endsWith('/api')) return trimmed.slice(0, -4)
	return trimmed
}

const apiBaseUrl = normalizeApiBaseUrl(
	import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL,
)

client.setConfig({
	baseUrl: apiBaseUrl,
	auth: async () => localStorage.getItem('access_token') || '',
})

client.interceptors.error.use((_error, response) => {
	if (response && [401, 403].includes(response.status)) {
		localStorage.removeItem('access_token')
		window.location.href = '/login'
	}
	return _error
})

const queryClient = new QueryClient()

/**
 * Detect if value is a JSON string (starts with { [ " or is a number/boolean)
 * but we'll try JSON.parse on everything and fallback to raw string
 */
const router = createRouter({
	routeTree,
	scrollRestoration: true,
	context: {
		queryClient,
	},
	defaultPreload: 'intent',
	defaultPreloadStaleTime: 0,
	defaultNotFoundComponent: () => <DefaultNotFound fullPage />,
	defaultErrorComponent: ({ error, reset, info }) => (
		<DefaultError error={error} reset={reset} info={info} fullPage />
	),
	parseSearch: (searchStr) => {
		const search: Record<string, any> = {}
		const params = new URLSearchParams(searchStr)
		params.forEach((value, key) => {
			try {
				search[key] = JSON.parse(value)
			} catch {
				search[key] = value
			}
		})
		return search
	},
	stringifySearch: (search) => {
		const params = new URLSearchParams()
		Object.entries(search).forEach(([key, value]) => {
			if (value === undefined || value === null) return
			if (typeof value === 'string') {
				params.set(key, value)
			} else {
				params.set(key, JSON.stringify(value))
			}
		})
		const searchStr = params.toString()
		return searchStr ? `?${searchStr}` : ''
	},
})
declare module '@tanstack/react-router' {
	interface Register {
		router: typeof router
	}
}

ReactDOM.createRoot(document.getElementById('root')!).render(
	<StrictMode>
		<RouterProvider router={router} />
	</StrictMode>,
)
