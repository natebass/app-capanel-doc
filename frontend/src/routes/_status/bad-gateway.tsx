import {
	Home01Icon as Home,
	StructureIcon as Network,
	RefreshIcon as RefreshCcw,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/bad-gateway')({
	component: BadGatewayPage,
	head: () => ({
		meta: [{ title: '502 - Bad Gateway' }],
	}),
})

function BadGatewayPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={Network} className='size-16 text-destructive' />
				</div>
			}
			title='502 - Bad Gateway'
			description='The server received an invalid response from an upstream server.'
			footer={
				<>
					<Button onClick={() => window.location.reload()}>
						<HugeiconsIcon icon={RefreshCcw} className='mr-2 size-4' />
						Retry
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<Alert variant='destructive'>
				<HugeiconsIcon icon={Network} className='size-4' />
				<AlertTitle>Gateway Error</AlertTitle>
				<AlertDescription>
					Our servers are having trouble communicating. This is usually temporary. Please try again.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}
