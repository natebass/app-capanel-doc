import {
	Cancel01Icon as Ban,
	Home01Icon as Home,
	RefreshIcon as RefreshCcw,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/cancelled')({
	component: CancelledPage,
	head: () => ({
		meta: [{ title: 'Action Cancelled' }],
	}),
})

function CancelledPage() {
	return (
		<StatusCard
			variant='default'
			icon={
				<div className='rounded-full bg-muted p-6'>
					<HugeiconsIcon icon={Ban} className='size-16 text-muted-foreground' />
				</div>
			}
			title='Action Cancelled'
			description='The operation was cancelled. No changes were made.'
			footer={
				<>
					<Button onClick={() => window.history.back()}>
						<HugeiconsIcon icon={RefreshCcw} className='mr-2 size-4' />
						Try Again
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<Alert>
				<HugeiconsIcon icon={Ban} className='size-4' />
				<AlertTitle>No Changes Made</AlertTitle>
				<AlertDescription>
					Your data remains unchanged. You can safely navigate away or try again.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}
