import { Home01Icon, LockIcon, Mail01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/locked')({
	component: LockedPage,
	head: () => ({
		meta: [{ title: '423 - Account Locked' }],
	}),
})

function LockedPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={LockIcon} className='size-16 text-destructive' />
				</div>
			}
			title='423 - Account Locked'
			description='Your account has been temporarily locked.'
			footer={
				<>
					<Button render={<Link to='/' />}>
						<HugeiconsIcon icon={Mail01Icon} className='mr-2 size-4' />
						Contact Support
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<Alert variant='destructive'>
				<HugeiconsIcon icon={LockIcon} className='size-4' />
				<AlertTitle>Account Security</AlertTitle>
				<AlertDescription>
					This may be due to multiple failed login attempts or suspicious activity. Please contact
					support to unlock your account.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}
