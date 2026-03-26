import { RefreshIcon, WifiOffIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/offline')({
	component: OfflinePage,
	head: () => ({
		meta: [{ title: 'You Are Offline' }],
	}),
})

function OfflinePage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<HugeiconsIcon icon={WifiOffIcon} className='size-16 text-yellow-500' />
				</div>
			}
			title="You're Offline"
			description="It looks like you've lost your internet connection."
			footer={
				<Button onClick={() => window.location.reload()}>
					<HugeiconsIcon icon={RefreshIcon} className='mr-2 size-4' />
					Retry Connection
				</Button>
			}
		>
			<div className='space-y-4'>
				<Alert>
					<HugeiconsIcon icon={WifiOffIcon} className='size-4' />
					<AlertTitle>No Internet Connection</AlertTitle>
					<AlertDescription>Please check your network settings and try again.</AlertDescription>
				</Alert>

				<div className='text-center text-sm text-muted-foreground'>
					<p>Things to try:</p>
					<ul className='mt-2 space-y-1 text-left'>
						<li>Check your Wi-Fi connection</li>
						<li>Check your router or modem</li>
						<li>Disable airplane mode if enabled</li>
						<li>Try using mobile data</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}
