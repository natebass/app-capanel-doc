import {
	Clock01Icon as Clock,
	Home01Icon as Home,
	CloudServerIcon as ServerOff,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
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
					<HugeiconsIcon icon={ServerOff} className='size-16 text-yellow-500' />
				</div>
			}
			title='503 - Service Unavailable'
			description='The service is temporarily unavailable. Please try again later.'
			footer={
				<>
					<Button onClick={() => window.location.reload()}>Retry Connection</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-between'>
					<span className='text-sm text-muted-foreground'>Status</span>
					<Badge variant='secondary'>
						<HugeiconsIcon icon={Clock} className='mr-1 size-3' />
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
