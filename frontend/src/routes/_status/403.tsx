import { Home01Icon, SecurityBlockIcon as ShieldOff } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/403')({
	component: ForbiddenPage,
	head: () => ({
		meta: [{ title: '403 - Forbidden' }],
	}),
})

function ForbiddenPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={ShieldOff} className='size-16 text-destructive' />
				</div>
			}
			title='403 - Forbidden'
			description="You don't have permission to access this resource."
			footer={
				<>
					<Button render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						Contact Support
					</Button>
				</>
			}
		>
			<Alert>
				<HugeiconsIcon icon={ShieldOff} className='size-4' />
				<AlertTitle>Access Denied</AlertTitle>
				<AlertDescription>
					If you believe this is an error, please contact your administrator or support team.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}
