import type { Meta, StoryObj } from '@storybook/react-vite'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {
	createMemoryHistory,
	createRootRoute,
	createRouter,
	RouterProvider,
} from '@tanstack/react-router'
import { expect, within } from 'storybook/test'

import { RouteComponent as Page } from '@/routes/index'

// Create a mock QueryClient
const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			retry: false,
		},
	},
})

const meta = {
	title: 'Layout/Page',
	component: Page,
	parameters: {
		layout: 'fullscreen',
	},
	decorators: [
		(Story) => {
			const rootRoute = createRootRoute({
				component: Story,
			})
			const router = createRouter({
				routeTree: rootRoute,
				history: createMemoryHistory(),
			})
			return (
				<QueryClientProvider client={queryClient}>
					<RouterProvider router={router} />
				</QueryClientProvider>
			)
		},
	],
} satisfies Meta<typeof Page>

export default meta
type Story = StoryObj<typeof meta>

export const Homepage: Story = {
	play: async ({ canvasElement }) => {
		const canvas = within(canvasElement)
		const title = canvas.getByText(/California Accountability Panel/i)
		await expect(title).toBeInTheDocument()
	},
}
