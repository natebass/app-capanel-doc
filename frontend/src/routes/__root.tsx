import { TanStackDevtools } from '@tanstack/react-devtools'
import type { QueryClient } from '@tanstack/react-query'
import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'

import { DefaultPending } from '@/components/common/status/DefaultPending'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/sonner'

import TanStackQueryDevtools from '../integrations/tanstack-query/devtools'
import { Provider } from '../integrations/tanstack-query/root-provider'
import StoreDevtools from '../lib/demo-store-devtools'

interface MyRouterContext {
	queryClient: QueryClient
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
	pendingComponent: () => (
		<DefaultPending fullPage={false} variant='card' message='Loading application...' />
	),
	component: RootComponent,
})

export function RootComponent() {
	const { queryClient } = Route.useRouteContext()
	return (
		<ThemeProvider defaultTheme='light' storageKey='vite-ui-theme'>
			<Provider queryClient={queryClient}>
				<Outlet />
				<Toaster richColors closeButton />
				<TanStackDevtools
					config={{
						position: 'bottom-right',
					}}
					plugins={[
						{
							name: 'Tanstack Router',
							render: <TanStackRouterDevtoolsPanel />,
						},
						TanStackQueryDevtools,
						StoreDevtools,
					]}
				/>
			</Provider>
		</ThemeProvider>
	)
}
