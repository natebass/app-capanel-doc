import { createFileRoute, Link } from '@tanstack/react-router'
import { Activity, Home, Sparkles } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/bandwidth-exceeded')({
	component: BandwidthExceededPage,
	head: () => ({
		meta: [{ title: '509 - Bandwidth Exceeded' }],
	}),
})

function BandwidthExceededPage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<Activity className='size-16 text-yellow-500' />
				</div>
			}
			title='509 - Bandwidth Exceeded'
			description='You have exceeded your bandwidth limit for this period.'
			footer={
				<>
					<Button render={<Link to='/dashboard' />}>
						<Sparkles className='mr-2 size-4' />
						Upgrade Plan
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center'>
					<Badge variant='destructive'>Limit Reached</Badge>
				</div>

				<Progress value={100}>
					<ProgressLabel>Bandwidth Used</ProgressLabel>
					<ProgressValue>{() => '100%'}</ProgressValue>
				</Progress>

				<Separator />

				<div className='space-y-2 text-sm'>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Current Plan</span>
						<span className='font-medium'>Basic</span>
					</div>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Resets On</span>
						<span className='font-medium'>Feb 1, 2026</span>
					</div>
				</div>

				<Separator />

				<p className='text-center text-sm text-muted-foreground'>
					Upgrade your plan for unlimited bandwidth.
				</p>
			</div>
		</StatusCard>
	)
}

export default BandwidthExceededPage
