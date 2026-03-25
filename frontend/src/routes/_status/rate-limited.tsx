import {
	Clock01Icon,
	DashboardCircleIcon as Gauge,
	Home01Icon,
	TimerIcon as Timer,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/rate-limited')({
	component: RateLimitedPage,
	head: () => ({
		meta: [{ title: '429 - Rate Limited' }],
	}),
})

function RateLimitedPage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<HugeiconsIcon icon={Gauge} className='size-16 text-yellow-500' />
				</div>
			}
			title='429 - Too Many Requests'
			description="You've exceeded the rate limit. Please slow down."
			footer={
				<>
					<Button disabled>
						<HugeiconsIcon icon={Timer} className='mr-2 size-4' />
						Wait 60 seconds
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Badge variant='secondary'>
						<HugeiconsIcon icon={Clock01Icon} className='mr-1 size-3' />
						Cooldown Active
					</Badge>
				</div>

				<Progress value={100}>
					<ProgressLabel>Rate Limit</ProgressLabel>
					<ProgressValue>{() => '100/100'}</ProgressValue>
				</Progress>

				<Separator />

				<div className='space-y-2 text-sm'>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Requests Used</span>
						<span className='font-medium'>100 / 100</span>
					</div>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Reset In</span>
						<span className='font-medium'>60 seconds</span>
					</div>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Rate Limit</span>
						<span className='font-medium'>100 req/min</span>
					</div>
				</div>

				<Separator />

				<p className='text-center text-sm text-muted-foreground'>
					Need higher limits?{' '}
					<Link to='/dashboard' className='text-primary hover:underline'>
						Upgrade your plan
					</Link>
				</p>
			</div>
		</StatusCard>
	)
}
