import { AlertCircleIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import useAuth from '@/routes/-hooks/hooks/useAuth'

export const Route = createFileRoute('/user/')({
	component: Dashboard,
	head: () => ({
		meta: [
			{
				title: 'dashboard - FastAPI Cloud',
			},
		],
	}),
})

function Dashboard() {
	const { user: currentUser } = useAuth()

	if (!currentUser) {
		return null
	}

	return (
		<div className='space-y-6'>
			<div className='space-y-2'>
				<div className='flex items-center gap-2'>
					<h1 className='text-2xl truncate max-w-sm'>
						Hi, {currentUser.fullName || currentUser.email}
					</h1>
					{currentUser.isSuperuser && <Badge>Admin</Badge>}
				</div>
				<p className='text-muted-foreground'>Welcome back. Choose what you want to manage.</p>
			</div>

			{currentUser.forcePasswordReset && (
				<Alert variant='destructive'>
					<HugeiconsIcon icon={AlertCircleIcon} className='size-4' />
					<AlertTitle>Password reset required</AlertTitle>
					<AlertDescription>
						Your account has <strong>forcePasswordReset</strong> enabled. Please update your
						password in settings.
					</AlertDescription>
				</Alert>
			)}

			<div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
				<div className='rounded-lg border p-4 space-y-3'>
					<h2 className='font-semibold'>Items</h2>
					<p className='text-sm text-muted-foreground'>
						{currentUser.isSuperuser
							? "View and edit all users' items."
							: 'Create and manage your items.'}
					</p>
					<Button size='sm' render={<Link to='/user/items' />}>
						Open Items
					</Button>
				</div>

				<div className='rounded-lg border p-4 space-y-3'>
					<h2 className='font-semibold'>Settings</h2>
					<p className='text-sm text-muted-foreground'>
						Update your profile, password, and account preferences.
					</p>
					<Button size='sm' variant='outline' render={<Link to='/user/settings' />}>
						Open Settings
					</Button>
				</div>

				{currentUser.isSuperuser && (
					<div className='rounded-lg border p-4 space-y-3'>
						<h2 className='font-semibold'>Admin</h2>
						<p className='text-sm text-muted-foreground'>
							View users and edit or delete any account.
						</p>
						<Button size='sm' variant='secondary' render={<Link to='/user/admin' />}>
							Open Admin
						</Button>
					</div>
				)}
			</div>
		</div>
	)
}
