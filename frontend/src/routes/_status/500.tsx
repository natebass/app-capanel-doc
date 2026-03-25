import {
	Alert01Icon as AlertTriangle,
	Home01Icon as Home,
	RefreshIcon as RefreshCcw,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/500')({
	component: InternalServerErrorPage,
	head: () => ({
		meta: [{ title: '500 - Internal Server Error' }],
	}),
})

function InternalServerErrorPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={AlertTriangle} className='size-16 text-destructive' />
				</div>
			}
			title='500 - Internal Server Error'
			description="Something went wrong on our end. We're working to fix it."
			footer={
				<>
					<Button onClick={() => window.location.reload()}>
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
			<Alert variant='destructive'>
				<HugeiconsIcon icon={AlertTriangle} className='size-4' />
				<AlertTitle>Error Details</AlertTitle>
				<AlertDescription>
					Our team has been notified and is investigating the issue. Please try again in a few
					minutes.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}
