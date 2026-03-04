import { createFileRoute, Link } from '@tanstack/react-router'
import { Clock, Home, RefreshCcw, Timer } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
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
					<Timer className='size-16 text-yellow-500' />
				</div>
			}
			title='408 - Request Timeout'
			description='The server took too long to respond.'
			footer={
				<>
					<Button onClick={() => window.location.reload()}>
						<RefreshCcw className='mr-2 size-4' />
						Try Again
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<Alert>
				<Clock className='size-4' />
				<AlertTitle>Connection Timed Out</AlertTitle>
				<AlertDescription>
					This could be due to slow network conditions or server load. Please try again.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}

export default TimeoutPage
