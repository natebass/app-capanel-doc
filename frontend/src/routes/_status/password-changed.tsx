import { createFileRoute, Link } from '@tanstack/react-router'
import { Check, Home, KeyRound, LogIn } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/password-changed')({
	component: PasswordChangedPage,
	head: () => ({
		meta: [{ title: 'Password Changed' }],
	}),
})

function PasswordChangedPage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<KeyRound className='size-16 text-green-500' />
				</div>
			}
			title='Password Changed'
			description='Your password has been updated successfully.'
			footer={
				<>
					<Button render={<Link to='/login' />}>
						<LogIn className='mr-2 size-4' />
						Sign In
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
					<Badge variant='default'>
						<Check className='mr-1 size-3' />
						Secured
					</Badge>
				</div>

				<Alert>
					<KeyRound className='size-4' />
					<AlertTitle>Security Notice</AlertTitle>
					<AlertDescription>
						You've been logged out of all devices for security. Please sign in with your new
						password.
					</AlertDescription>
				</Alert>
			</div>
		</StatusCard>
	)
}

export default PasswordChangedPage
