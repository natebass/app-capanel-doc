import { AlertCircleIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import ChangePassword from '@/components/form/ChangePassword'
import DeleteConfirmation from '@/components/form/DeleteConfirmation'
import UserInformation from '@/components/form/UserInformation'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import useAuth from '@/lib/hooks/useAuth.ts'

const tabsConfig = [
	{ value: 'my-profile', title: 'My profile', component: UserInformation },
	{ value: 'password', title: 'Password', component: ChangePassword },
	{
		value: 'danger-zone',
		title: 'Danger zone',
		component: () => (
			<div className='max-w-md mt-4 rounded-lg border border-destructive/50 p-4'>
				<h3 className='font-semibold text-destructive'>Delete Account</h3>
				<p className='mt-1 text-sm text-muted-foreground'>
					Permanently delete your account and all associated data.
				</p>
				<DeleteConfirmation />
			</div>
		),
	},
]

export const Route = createFileRoute('/user/settings')({
	component: UserSettings,
	head: () => ({
		meta: [
			{
				title: 'Settings - FastAPI Cloud',
			},
		],
	}),
})

function UserSettings() {
	const { user: currentUser } = useAuth()
	const finalTabs = tabsConfig
	const defaultTab = currentUser?.force_password_reset ? 'password' : 'my-profile'

	if (!currentUser) {
		return null
	}

	return (
		<div className='flex flex-col gap-6'>
			<div className='space-y-2'>
				<div className='flex items-center gap-2'>
					<h1 className='text-2xl font-bold tracking-tight'>User Settings</h1>
					{currentUser.is_superuser && <Badge>Admin</Badge>}
				</div>
				<p className='text-muted-foreground'>
					Manage your profile, security settings, and account controls.
				</p>
			</div>

			{currentUser.force_password_reset && (
				<Alert variant='destructive'>
					<HugeiconsIcon icon={AlertCircleIcon} className='size-4' />
					<AlertTitle>Forced Password Reset Required</AlertTitle>
					<AlertDescription>
						Your account has <strong>force_password_reset</strong> enabled. Update your password now
						to continue using all features.
					</AlertDescription>
				</Alert>
			)}

			{currentUser.is_superuser && (
				<div className='rounded-lg border p-4 flex flex-col gap-3'>
					<div>
						<h2 className='text-sm font-semibold'>Admin Controls</h2>
						<p className='text-sm text-muted-foreground'>
							Admins can view, edit, and delete users. Admins can also view and edit any user&apos;s
							items.
						</p>
					</div>
					<div className='flex flex-wrap gap-2'>
						<Button render={<Link to='/user/admin' />}>Manage Users</Button>
						<Button variant='outline' render={<Link to='/user/items' />}>
							Manage Items
						</Button>
					</div>
				</div>
			)}

			<Tabs defaultValue={defaultTab} className='space-y-4'>
				<TabsList>
					{finalTabs.map((tab) => (
						<TabsTrigger key={tab.value} value={tab.value}>
							{tab.title}
						</TabsTrigger>
					))}
				</TabsList>
				{finalTabs.map((tab) => (
					<TabsContent key={tab.value} value={tab.value}>
						<tab.component />
					</TabsContent>
				))}
			</Tabs>
		</div>
	)
}
