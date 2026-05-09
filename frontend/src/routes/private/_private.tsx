import { createFileRoute, Outlet, redirect } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import useAuth from '@/routes/-hooks/hooks/useAuth.ts'

export const Route = createFileRoute('/private/_private')({
	beforeLoad: ({ context, location }) => {
		// @ts-expect-error
		if (!context.auth.isAuthenticated) {
			throw redirect({
				to: '/login',
				search: {
					redirect: location.href,
				},
			})
		}
	},
	component: PrivateLayout,
})

function PrivateLayout() {
	const auth = useAuth()
	const userLabel = auth.user?.fullName || auth.user?.email || 'User'
	return (
		<>
			<div>
				<p>Welcome, {userLabel}!</p>
				<Button onClick={() => auth.logout()}>Logout</Button>
			</div>
			<hr />
			<Outlet />
		</>
	)
}
