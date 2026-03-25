import {
	Clock01Icon,
	ConstructionIcon,
	FolderOpenIcon,
	Information,
	Mail01Icon,
	Menu01Icon,
	Notification01Icon,
	RocketIcon,
	Search01Icon,
	SecurityIcon,
	UserGroupIcon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export const Route = createFileRoute('/_status/info-states')({
	component: InfoStatesPage,
	head: () => ({
		meta: [{ title: 'Info States Demo' }],
	}),
})

const infoPages = [
	{ name: 'Coming Soon', icon: RocketIcon, path: '/coming-soon', color: 'text-blue-500' },
	{ name: 'Maintenance', icon: ConstructionIcon, path: '/maintenance', color: 'text-blue-500' },
	{
		name: 'Under Construction',
		icon: SecurityIcon,
		path: '/under-construction',
		color: 'text-blue-500',
	},
	{ name: 'Verify Email', icon: Mail01Icon, path: '/verify-email', color: 'text-blue-500' },
	{ name: 'Login Required', icon: UserGroupIcon, path: '/login-required', color: 'text-blue-500' },
	{ name: '2FA Required', icon: Clock01Icon, path: '/2fa-required', color: 'text-blue-500' },
	{ name: 'Team Invitation', icon: UserGroupIcon, path: '/invitation', color: 'text-blue-500' },
	{ name: 'Processing', icon: Clock01Icon, path: '/processing', color: 'text-blue-500' },
	{ name: 'Queued', icon: Menu01Icon, path: '/queued', color: 'text-blue-500' },
	{
		name: 'Empty State',
		icon: FolderOpenIcon,
		path: '/empty-state',
		color: 'text-muted-foreground',
	},
	{ name: 'No Results', icon: Search01Icon, path: '/no-results', color: 'text-muted-foreground' },
	{
		name: 'Cancelled',
		icon: Information,
		path: '/cancelled',
		color: 'text-muted-foreground',
	},
]

function InfoStatesPage() {
	return (
		<div className='w-full max-w-4xl space-y-8'>
			<Card>
				<CardHeader className='text-center'>
					<div className='mx-auto mb-4'>
						<div className='rounded-full bg-blue-500/10 p-4'>
							<HugeiconsIcon icon={Notification01Icon} className='size-12 text-blue-500' />
						</div>
					</div>
					<CardTitle className='text-3xl'>Informational States</CardTitle>
					<CardDescription className='text-base'>
						Notification, progress, and transitional pages
					</CardDescription>
				</CardHeader>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle className='text-lg'>Info Pages</CardTitle>
					<CardDescription>Click to view each informational state</CardDescription>
				</CardHeader>
				<CardContent>
					<div className='grid gap-2 sm:grid-cols-2 md:grid-cols-3'>
						{infoPages.map((page) => {
							const Icon = page.icon
							return (
								<Link
									key={page.path}
									to={page.path}
									className='flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors'
								>
									<div className='rounded-full bg-blue-500/10 p-2'>
										<HugeiconsIcon icon={Icon} className={`size-4 ${page.color}`} />
									</div>
									<div className='font-medium text-sm'>{page.name}</div>
								</Link>
							)
						})}
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle className='text-lg'>Common Use Cases</CardTitle>
					<CardDescription>When to use informational status pages</CardDescription>
				</CardHeader>
				<CardContent>
					<div className='grid gap-4 md:grid-cols-2'>
						<div className='space-y-2'>
							<h4 className='font-medium'>Pre-Launch</h4>
							<ul className='text-sm text-muted-foreground space-y-1'>
								<li>• Coming Soon - features not yet available</li>
								<li>• Under Construction - pages being built</li>
								<li>• Maintenance - scheduled downtime</li>
							</ul>
						</div>
						<div className='space-y-2'>
							<h4 className='font-medium'>Authentication Flow</h4>
							<ul className='text-sm text-muted-foreground space-y-1'>
								<li>• Login Required - unauthenticated access</li>
								<li>• Verify Email - pending verification</li>
								<li>• 2FA Required - second factor needed</li>
							</ul>
						</div>
						<div className='space-y-2'>
							<h4 className='font-medium'>Background Tasks</h4>
							<ul className='text-sm text-muted-foreground space-y-1'>
								<li>• Processing - task in progress</li>
								<li>• Queued - waiting in line</li>
							</ul>
						</div>
						<div className='space-y-2'>
							<h4 className='font-medium'>Empty States</h4>
							<ul className='text-sm text-muted-foreground space-y-1'>
								<li>• No Results - search returned nothing</li>
								<li>• Empty State - no data yet</li>
								<li>• Cancelled - action was cancelled</li>
							</ul>
						</div>
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle className='text-lg'>Quick Links</CardTitle>
					<CardDescription>Jump to related sections</CardDescription>
				</CardHeader>
				<CardContent className='flex flex-wrap gap-2'>
					<Button variant='outline' size='sm' render={<Link to='/error-demo' />}>
						Error States
					</Button>
					<Button variant='outline' size='sm' render={<Link to='/success-states' />}>
						Success States
					</Button>
					<Button variant='outline' size='sm' render={<Link to='/loading' />}>
						Loading States
					</Button>
					<Button variant='outline' size='sm' render={<Link to='/status' />}>
						System Status
					</Button>
				</CardContent>
			</Card>
		</div>
	)
}
