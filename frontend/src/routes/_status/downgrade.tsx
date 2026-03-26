import {
	Alert01Icon,
	ArrowDown01Icon,
	Tick02Icon,
	Home01Icon,
	Cancel01Icon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/downgrade')({
	component: DowngradePage,
	head: () => ({
		meta: [{ title: 'Plan Downgraded' }],
	}),
})

function DowngradePage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<HugeiconsIcon icon={ArrowDown01Icon} className='size-16 text-yellow-500' />
				</div>
			}
			title='Plan Downgraded'
			description='Your subscription has been downgraded to the Free plan.'
			footer={
				<>
					<Button render={<Link to='/dashboard' />}>Upgrade Again</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Alert>
					<HugeiconsIcon icon={Alert01Icon} className='size-4' />
					<AlertTitle>Features Removed</AlertTitle>
					<AlertDescription>
						Some features are no longer available on your current plan.
					</AlertDescription>
				</Alert>

				<Separator />

				<div className='space-y-2 text-sm'>
					<p className='font-medium'>What you've lost:</p>
					<ul className='space-y-1 text-muted-foreground'>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Cancel01Icon} className='size-4 text-destructive' />
							Unlimited API calls
						</li>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Cancel01Icon} className='size-4 text-destructive' />
							Priority support
						</li>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Cancel01Icon} className='size-4 text-destructive' />
							Team collaboration
						</li>
					</ul>
				</div>

				<div className='space-y-2 text-sm'>
					<p className='font-medium'>What you still have:</p>
					<ul className='space-y-1 text-muted-foreground'>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Tick02Icon} className='size-4 text-green-500' />
							1,000 API calls/month
						</li>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Tick02Icon} className='size-4 text-green-500' />
							Basic analytics
						</li>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Tick02Icon} className='size-4 text-green-500' />
							Email support
						</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}
