import {
	ActivityIcon,
	Alert01Icon,
	Clock01Icon,
	CloudServerIcon as Server,
	Database01Icon,
	InternetIcon,
	Loading01Icon,
	Notification01Icon,
	Shield01Icon,
	SparklesIcon,
	Tick02Icon,
	ZapIcon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/status')({
	component: SystemStatusPage,
	head: () => ({
		meta: [{ title: 'System Status - FastAPI Cloud' }],
	}),
})

interface ServiceStatus {
	name: string
	status: 'operational' | 'degraded' | 'outage' | 'maintenance'
	icon: React.ReactNode
	uptime: number
	responseTime?: number
}

const services: ServiceStatus[] = [
	{
		name: 'API Gateway',
		status: 'operational',
		icon: <HugeiconsIcon icon={InternetIcon} className='size-5' />,
		uptime: 99.99,
		responseTime: 45,
	},
	{
		name: 'Database',
		status: 'operational',
		icon: <HugeiconsIcon icon={Database01Icon} className='size-5' />,
		uptime: 99.95,
		responseTime: 12,
	},
	{
		name: 'Authentication',
		status: 'operational',
		icon: <HugeiconsIcon icon={Shield01Icon} className='size-5' />,
		uptime: 99.98,
		responseTime: 89,
	},
	{
		name: 'Web Servers',
		status: 'operational',
		icon: <HugeiconsIcon icon={Server} className='size-5' />,
		uptime: 99.97,
		responseTime: 23,
	},
	{
		name: 'CDN',
		status: 'degraded',
		icon: <HugeiconsIcon icon={ZapIcon} className='size-5' />,
		uptime: 99.5,
		responseTime: 156,
	},
	{
		name: 'Background Jobs',
		status: 'operational',
		icon: <HugeiconsIcon icon={ActivityIcon} className='size-5' />,
		uptime: 99.9,
		responseTime: 34,
	},
]

function getStatusColor(status: ServiceStatus['status']) {
	switch (status) {
		case 'operational':
			return 'bg-green-500'
		case 'degraded':
			return 'bg-yellow-500'
		case 'outage':
			return 'bg-red-500'
		case 'maintenance':
			return 'bg-blue-500'
	}
}

function getStatusBadgeVariant(status: ServiceStatus['status']) {
	switch (status) {
		case 'operational':
			return 'default'
		case 'degraded':
			return 'secondary'
		case 'outage':
			return 'destructive'
		case 'maintenance':
			return 'outline'
	}
}

function SystemStatusPage() {
	const allOperational = services.every((s) => s.status === 'operational')
	const hasOutage = services.some((s) => s.status === 'outage')

	return (
		<div className='w-full max-w-4xl space-y-8'>
			{/* Main Status Card */}
			<Card>
				<CardHeader className='text-center'>
					<div className='mx-auto mb-4'>
						{allOperational ? (
							<div className='rounded-full bg-green-500/10 p-4'>
								<HugeiconsIcon icon={Tick02Icon} className='size-12 text-green-500' />
							</div>
						) : hasOutage ? (
							<div className='rounded-full bg-red-500/10 p-4'>
								<HugeiconsIcon icon={ActivityIcon} className='size-12 text-red-500' />
							</div>
						) : (
							<div className='rounded-full bg-yellow-500/10 p-4'>
								<HugeiconsIcon icon={ActivityIcon} className='size-12 text-yellow-500' />
							</div>
						)}
					</div>
					<CardTitle className='text-3xl'>
						{allOperational
							? 'All Systems Operational'
							: hasOutage
								? 'Service Outage Detected'
								: 'Partial System Degradation'}
					</CardTitle>
					<CardDescription className='text-base'>
						{allOperational
							? 'All services are running normally.'
							: 'Some services are experiencing issues.'}
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div className='flex items-center justify-center gap-4 text-sm text-muted-foreground'>
						<div className='flex items-center gap-2'>
							<HugeiconsIcon icon={Clock01Icon} className='size-4' />
							<span>Last updated: {new Date().toLocaleTimeString()}</span>
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Quick Navigation to Status Pages */}
			<Card>
				<CardHeader>
					<CardTitle>Status Page Categories</CardTitle>
					<CardDescription>Explore different status page types</CardDescription>
				</CardHeader>
				<CardContent>
					<div className='grid gap-4 sm:grid-cols-2 md:grid-cols-4'>
						<Link
							to='/error-demo'
							className='flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-muted/50 transition-colors'
						>
							<div className='rounded-full bg-destructive/10 p-3'>
								<HugeiconsIcon icon={Alert01Icon} className='size-6 text-destructive' />
							</div>
							<span className='font-medium'>Error States</span>
							<span className='text-xs text-muted-foreground'>HTTP errors & failures</span>
						</Link>
						<Link
							to='/success-states'
							className='flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-muted/50 transition-colors'
						>
							<div className='rounded-full bg-green-500/10 p-3'>
								<HugeiconsIcon icon={SparklesIcon} className='size-6 text-green-500' />
							</div>
							<span className='font-medium'>Success States</span>
							<span className='text-xs text-muted-foreground'>Confirmations</span>
						</Link>
						<Link
							to='/info-states'
							className='flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-muted/50 transition-colors'
						>
							<div className='rounded-full bg-blue-500/10 p-3'>
								<HugeiconsIcon icon={Notification01Icon} className='size-6 text-blue-500' />
							</div>
							<span className='font-medium'>Info States</span>
							<span className='text-xs text-muted-foreground'>Notifications</span>
						</Link>
						<Link
							to='/loading'
							className='flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-muted/50 transition-colors'
						>
							<div className='rounded-full bg-primary/10 p-3'>
								<HugeiconsIcon icon={Loading01Icon} className='size-6 text-primary' />
							</div>
							<span className='font-medium'>Loading States</span>
							<span className='text-xs text-muted-foreground'>Pending & progress</span>
						</Link>
					</div>
				</CardContent>
			</Card>

			{/* Service Status */}
			<Card>
				<CardHeader>
					<CardTitle>Service Status</CardTitle>
					<CardDescription>Current status of all system components</CardDescription>
				</CardHeader>
				<CardContent className='space-y-4'>
					{services.map((service, index) => (
						<div key={service.name}>
							<div className='flex items-center justify-between py-3'>
								<div className='flex items-center gap-3'>
									<div className='text-muted-foreground'>{service.icon}</div>
									<div>
										<p className='font-medium'>{service.name}</p>
										{service.responseTime && (
											<p className='text-sm text-muted-foreground'>
												Response time: {service.responseTime}ms
											</p>
										)}
									</div>
								</div>
								<div className='flex items-center gap-3'>
									<span className='text-sm text-muted-foreground'>{service.uptime}% uptime</span>
									<Badge variant={getStatusBadgeVariant(service.status)}>
										<span
											className={`mr-1.5 size-2 rounded-full ${getStatusColor(service.status)}`}
										/>
										{service.status.charAt(0).toUpperCase() + service.status.slice(1)}
									</Badge>
								</div>
							</div>
							{index < services.length - 1 && <Separator />}
						</div>
					))}
				</CardContent>
			</Card>

			{/* Stats */}
			<div className='grid gap-4 md:grid-cols-3'>
				<Card>
					<CardHeader>
						<CardTitle className='text-lg'>Overall Uptime</CardTitle>
						<CardDescription>Last 30 days</CardDescription>
					</CardHeader>
					<CardContent>
						<Progress value={99.87}>
							<ProgressLabel>Uptime</ProgressLabel>
							<ProgressValue>{() => '99.87%'}</ProgressValue>
						</Progress>
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<CardTitle className='text-lg'>Incidents</CardTitle>
						<CardDescription>Last 30 days</CardDescription>
					</CardHeader>
					<CardContent>
						<div className='text-3xl font-bold'>2</div>
						<p className='text-sm text-muted-foreground'>Resolved incidents</p>
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<CardTitle className='text-lg'>Avg Response</CardTitle>
						<CardDescription>Current average</CardDescription>
					</CardHeader>
					<CardContent>
						<div className='text-3xl font-bold'>59ms</div>
						<p className='text-sm text-muted-foreground'>API response time</p>
					</CardContent>
				</Card>
			</div>

			{/* common Status Pages Quick Links */}
			<Card>
				<CardHeader>
					<CardTitle>Quick Links</CardTitle>
					<CardDescription>Common status pages</CardDescription>
				</CardHeader>
				<CardContent>
					<div className='flex flex-wrap gap-2'>
						<Button variant='outline' size='sm' render={<Link to='/404' />}>
							404
						</Button>
						<Button variant='outline' size='sm' render={<Link to='/500' />}>
							500
						</Button>
						<Button variant='outline' size='sm' render={<Link to='/maintenance' />}>
							Maintenance
						</Button>
						<Button variant='outline' size='sm' render={<Link to='/coming-soon' />}>
							Coming Soon
						</Button>
						<Button variant='outline' size='sm' render={<Link to='/success' />}>
							Success
						</Button>
						<Button variant='outline' size='sm' render={<Link to='/offline' />}>
							Offline
						</Button>
					</div>
				</CardContent>
			</Card>
		</div>
	)
}
