import type { Meta, StoryObj } from '@storybook/react-vite'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {
	createMemoryHistory,
	createRootRoute,
	createRouter,
	RouterProvider,
} from '@tanstack/react-router'

import NavbarD52 from '../components/common/navbar/navbar-D52'
import { usersReadUserMeQueryKey } from '../lib/client'

// Create a mock QueryClient
const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			retry: false,
		},
	},
})

const meta = {
	title: 'layout/Navigation bar',
	component: NavbarD52,
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
	tags: ['autodocs'],
} satisfies Meta<typeof NavbarD52>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
	args: {
		shadow: false,
	},
}

export const WithShadow: Story = {
	args: {
		shadow: true,
	},
}

export const LoggedIn: Story = {
	args: {
		shadow: false,
	},
	decorators: [
		(Story) => {
			queryClient.setQueryData(usersReadUserMeQueryKey(), {
				id: '1',
				email: 'jane.doe@example.com',
				fullName: 'Jane Doe',
				isActive: true,
				isSuperuser: false,
			})
			return <Story />
		},
	],
}
