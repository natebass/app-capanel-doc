import { createFileRoute, Link } from '@tanstack/react-router'
import {
	Bell,
	Clock,
	Construction,
	FolderOpen,
	HardHat,
	Info,
	ListOrdered,
	Mail,
	Rocket,
	Search,
	Users,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export const Route = createFileRoute('/_status/info-states')({
	component: InfoStatesPage,
	head: () => ({
		meta: [{ title: 'Info States Demo' }],
	}),
})

const infoPages = [
	{ name: 'Coming Soon', icon: Rocket, path: '/coming-soon', color: 'text-blue-500' },
	{ name: 'Maintenance', icon: Construction, path: '/maintenance', color: 'text-blue-500' },
	{
		name: 'Under Construction',
		icon: HardHat,
		path: '/under-construction',
		color: 'text-blue-500',
	},
	{ name: 'Verify Email', icon: Mail, path: '/verify-email', color: 'text-blue-500' },
	{ name: 'Login Required', icon: Users, path: '/login-required', color: 'text-blue-500' },
	{ name: '2FA Required', icon: Clock, path: '/2fa-required', color: 'text-blue-500' },
	{ name: 'Team Invitation', icon: Users, path: '/invitation', color: 'text-blue-500' },
	{ name: 'Processing', icon: Clock, path: '/processing', color: 'text-blue-500' },
	{ name: 'Queued', icon: ListOrdered, path: '/queued', color: 'text-blue-500' },
	{
		name: 'Empty State',
		icon: FolderOpen,
		path: '/empty-state',
		color: 'text-muted-foreground',
	},
	{ name: 'No Results', icon: Search, path: '/no-results', color: 'text-muted-foreground' },
	{ name: 'Cancelled', icon: Info, path: '/cancelled', color: 'text-muted-foreground' },
]

function InfoStatesPage() {
	return (
		<div className='w-full max-w-4xl space-y-8'>
			<Card>
				<CardHeader className='text-center'>
					<div className='mx-auto mb-4'>
						<div className='rounded-full bg-blue-500/10 p-4'>
							<Bell className='size-12 text-blue-500' />
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
										<Icon className={`size-4 ${page.color}`} />
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

export default InfoStatesPage
