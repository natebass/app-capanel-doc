import { Clock01Icon, Home01Icon, Settings01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Spinner } from '@/components/ui/spinner'

export const Route = createFileRoute('/_status/processing')({
	component: ProcessingPage,
	head: () => ({
		meta: [{ title: 'Processing...' }],
	}),
})

function ProcessingPage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6 animate-pulse'>
					<HugeiconsIcon
						icon={Settings01Icon}
						className='size-16 text-blue-500 animate-spin'
						style={{ animationDuration: '3s' }}
					/>
				</div>
			}
			title='Processing...'
			description='Your request is being processed. Please wait.'
			footer={
				<Button variant='outline' render={<Link to='/' />}>
					<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
					Go Home
				</Button>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Spinner className='size-4' />
					<Badge variant='outline'>
						<HugeiconsIcon icon={Clock01Icon} className='mr-1 size-3' />
						In Progress
					</Badge>
				</div>

				<Progress value={68}>
					<ProgressLabel>Progress</ProgressLabel>
					<ProgressValue>{() => '68%'}</ProgressValue>
				</Progress>

				<Separator />

				<div className='space-y-3'>
					<div className='flex items-center gap-3'>
						<Skeleton className='size-4 rounded-full' />
						<Skeleton className='h-4 flex-1' />
					</div>
					<div className='flex items-center gap-3'>
						<Skeleton className='size-4 rounded-full' />
						<Skeleton className='h-4 flex-1' />
					</div>
					<div className='flex items-center gap-3'>
						<Skeleton className='size-4 rounded-full' />
						<Skeleton className='h-4 w-3/4' />
					</div>
				</div>

				<p className='text-center text-sm text-muted-foreground'>This may take a few moments...</p>
			</div>
		</StatusCard>
	)
}
