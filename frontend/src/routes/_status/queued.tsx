import { createFileRoute, Link } from '@tanstack/react-router'
import { Clock, Home, ListOrdered, Users } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/queued')({
	component: QueuedPage,
	head: () => ({
		meta: [{ title: 'Request Queued' }],
	}),
})

function QueuedPage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6'>
					<ListOrdered className='size-16 text-blue-500' />
				</div>
			}
			title='Request Queued'
			description='Your request has been added to the processing queue.'
			footer={
				<Button variant='outline' render={<Link to='/' />}>
					<Home className='mr-2 size-4' />
					Go Home
				</Button>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Badge variant='outline'>
						<Clock className='mr-1 size-3' />
						Waiting
					</Badge>
				</div>

				<div className='rounded-lg border bg-muted/50 p-4 text-center'>
					<div className='text-4xl font-bold'>12</div>
					<p className='text-sm text-muted-foreground'>Position in queue</p>
				</div>

				<Progress value={25}>
					<ProgressLabel>Estimated wait</ProgressLabel>
					<ProgressValue>{() => '~3 min'}</ProgressValue>
				</Progress>

				<Separator />

				<div className='flex items-center justify-center gap-2 text-sm text-muted-foreground'>
					<Users className='size-4' />
					<span>47 requests processed in the last hour</span>
				</div>

				<p className='text-center text-sm text-muted-foreground'>
					You'll be notified when your request is complete.
				</p>
			</div>
		</StatusCard>
	)
}

export default QueuedPage
