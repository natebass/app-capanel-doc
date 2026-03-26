import { Clock01Icon, Home01Icon, RefreshIcon, CloudServerIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/gateway-timeout')({
	component: GatewayTimeoutPage,
	head: () => ({
		meta: [{ title: '504 - Gateway Timeout' }],
	}),
})

function GatewayTimeoutPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={CloudServerIcon} className='size-16 text-destructive' />
				</div>
			}
			title='504 - Gateway Timeout'
			description='The upstream server failed to respond in time.'
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
				<AlertTitle>Server Timeout</AlertTitle>
				<AlertDescription>
					The server is taking longer than expected to respond. This could be due to high traffic or
					a temporary issue.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}
