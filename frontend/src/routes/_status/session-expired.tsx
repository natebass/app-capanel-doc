import { createFileRoute, Link } from '@tanstack/react-router'
import { Clock, Home, LogIn, TimerOff } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/session-expired')({
	component: SessionExpiredPage,
	head: () => ({
		meta: [{ title: 'Session Expired' }],
	}),
})

function SessionExpiredPage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<TimerOff className='size-16 text-yellow-500' />
				</div>
			}
			title='Session Expired'
			description='Your session has expired due to inactivity.'
			footer={
				<>
					<Button render={<Link to='/login' />}>
						<LogIn className='mr-2 size-4' />
						Sign In Again
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
				<AlertTitle>Security Notice</AlertTitle>
				<AlertDescription>
					For your security, sessions automatically expire after 30 minutes of inactivity.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}

export default SessionExpiredPage
