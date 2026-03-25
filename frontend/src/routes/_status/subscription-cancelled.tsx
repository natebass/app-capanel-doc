import { CreditCardIcon, Home01Icon, SparklesIcon, Cancel01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/subscription-cancelled')({
	component: SubscriptionCancelledPage,
	head: () => ({
		meta: [{ title: 'Subscription Cancelled' }],
	}),
})

function SubscriptionCancelledPage() {
	return (
		<StatusCard
			variant='default'
			icon={
				<div className='rounded-full bg-muted p-6'>
					<HugeiconsIcon icon={Cancel01Icon} className='size-16 text-muted-foreground' />
				</div>
			}
			title='Subscription Cancelled'
			description='Your subscription has been cancelled.'
			footer={
				<>
					<Button render={<Link to='/dashboard' />}>
						<HugeiconsIcon icon={SparklesIcon} className='mr-2 size-4' />
						Resubscribe
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Alert>
					<HugeiconsIcon icon={CreditCardIcon} className='size-4' />
					<AlertTitle>Access Until End of Billing Period</AlertTitle>
					<AlertDescription>
						You'll continue to have access to Pro features until Feb 28, 2026.
					</AlertDescription>
				</Alert>

				<Separator />

				<p className='text-center text-sm text-muted-foreground'>
					We're sorry to see you go. If you change your mind, you can resubscribe anytime.
				</p>
			</div>
		</StatusCard>
	)
}
