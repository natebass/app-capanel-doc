import { TanStackDevtools } from '@tanstack/react-devtools'
import type { QueryClient } from '@tanstack/react-query'
import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'

import { DefaultPending } from '@/components/status/DefaultPending'

import TanStackQueryDevtools from '../integrations/tanstack-query/devtools'
import { Provider } from '../integrations/tanstack-query/root-provider'
import AiDevtools from '../lib/ai-devtools'
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

function RootComponent() {
	const { queryClient } = Route.useRouteContext()
	return (
		<Provider queryClient={queryClient}>
			<Outlet />
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
					AiDevtools,
				]}
			/>
		</Provider>
	)
}
