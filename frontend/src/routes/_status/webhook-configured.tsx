import { Home01Icon, Tick01Icon, WebhookIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/webhook-configured')({
	component: WebhookConfiguredPage,
	head: () => ({
		meta: [{ title: 'Webhook Configured' }],
	}),
})

function WebhookConfiguredPage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={WebhookIcon} className='size-16 text-green-500' />
				</div>
			}
			title='Webhook Configured'
			description='Your webhook endpoint has been set up successfully.'
			footer={
				<>
					<Button render={<Link to='/user/settings' />}>Manage Webhooks</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Badge variant='default'>
						<HugeiconsIcon icon={Tick01Icon} className='mr-1 size-3' />
						Active
					</Badge>
				</div>

				<div className='rounded-lg border bg-muted/50 p-4 space-y-2 text-sm'>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Endpoint</span>
						<span className='font-mono text-xs'>https://api.example.com/webhook</span>
					</div>
					<Separator />
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Events</span>
						<span className='font-medium'>All events</span>
					</div>
					<Separator />
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Status</span>
						<Badge variant='outline' className='text-xs'>
							Verified
						</Badge>
					</div>
				</div>

				<p className='text-center text-sm text-muted-foreground'>
					Events will be sent to your endpoint in real-time.
				</p>
			</div>
		</StatusCard>
	)
}
