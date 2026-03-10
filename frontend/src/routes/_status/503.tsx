import { createFileRoute, Link } from '@tanstack/react-router'
import { Clock, Home, ServerOff } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress, ProgressLabel } from '@/components/ui/progress'

export const Route = createFileRoute('/_status/503')({
	component: ServiceUnavailablePage,
	head: () => ({
		meta: [{ title: '503 - Service Unavailable' }],
	}),
})

function ServiceUnavailablePage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<ServerOff className='size-16 text-yellow-500' />
				</div>
			}
			title='503 - Service Unavailable'
			description='The service is temporarily unavailable. Please try again later.'
			footer={
				<>
					<Button onClick={() => window.location.reload()}>Retry Connection</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-between'>
					<span className='text-sm text-muted-foreground'>Status</span>
					<Badge variant='secondary'>
						<Clock className='mr-1 size-3' />
						Recovering
					</Badge>
				</div>
				<Progress value={65}>
					<ProgressLabel>Recovery Progress</ProgressLabel>
				</Progress>
				<p className='text-center text-sm text-muted-foreground'>Estimated recovery: ~5 minutes</p>
			</div>
		</StatusCard>
	)
}

export default ServiceUnavailablePage
