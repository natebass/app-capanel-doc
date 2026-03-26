import { Home01Icon, Delete02Icon, Undo02Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/deleted')({
	component: DeletedPage,
	head: () => ({
		meta: [{ title: 'Account Deleted' }],
	}),
})

function DeletedPage() {
	return (
		<StatusCard
			variant='default'
			icon={
				<div className='rounded-full bg-muted p-6'>
					<HugeiconsIcon icon={Delete02Icon} className='size-16 text-muted-foreground' />
				</div>
			}
			title='Account Deleted'
			description='Your account has been successfully deleted.'
			footer={
				<>
					<Button variant='outline' render={<Link to='/sign-up' />}>
						Create New Account
					</Button>
					<Button variant='ghost' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Alert>
					<HugeiconsIcon icon={Undo02Icon} className='size-4' />
					<AlertTitle>30-Day Recovery Period</AlertTitle>
					<AlertDescription>
						You can recover your account within 30 days by contacting support.
					</AlertDescription>
				</Alert>

				<Separator />

				<div className='text-center text-sm text-muted-foreground'>
					<p>What happens next:</p>
					<ul className='mt-2 space-y-1 text-left'>
						<li>All data will be permanently deleted after 30 days</li>
						<li>You'll stop receiving all emails from us</li>
						<li>Your username may become available for others</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}
