import { Clock01Icon, Home01Icon, RefreshIcon, TimerIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/timeout')({
	component: TimeoutPage,
	head: () => ({
		meta: [{ title: '408 - Request Timeout' }],
	}),
})

function TimeoutPage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<HugeiconsIcon icon={TimerIcon} className='size-16 text-yellow-500' />
				</div>
			}
			title='408 - Request Timeout'
			description='The server took too long to respond.'
			footer={
				<>
					<Button onClick={() => window.location.reload()}>
						<HugeiconsIcon icon={RefreshIcon} className='mr-2 size-4' />
						Try Again
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<Alert>
				<HugeiconsIcon icon={Clock01Icon} className='size-4' />
				<AlertTitle>Connection Timed Out</AlertTitle>
				<AlertDescription>
					This could be due to slow network conditions or server load. Please try again.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}
