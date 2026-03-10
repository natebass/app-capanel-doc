import { createFileRoute, Link } from '@tanstack/react-router'
import { AlertTriangle, ArrowDown, Check, Home, X } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
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
					<ArrowDown className='size-16 text-yellow-500' />
				</div>
			}
			title='Plan Downgraded'
			description='Your subscription has been downgraded to the Free plan.'
			footer={
				<>
					<Button render={<Link to='/dashboard' />}>Upgrade Again</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Alert>
					<AlertTriangle className='size-4' />
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
							<X className='size-4 text-destructive' />
							Unlimited API calls
						</li>
						<li className='flex items-center gap-2'>
							<X className='size-4 text-destructive' />
							Priority support
						</li>
						<li className='flex items-center gap-2'>
							<X className='size-4 text-destructive' />
							Team collaboration
						</li>
					</ul>
				</div>

				<div className='space-y-2 text-sm'>
					<p className='font-medium'>What you still have:</p>
					<ul className='space-y-1 text-muted-foreground'>
						<li className='flex items-center gap-2'>
							<Check className='size-4 text-green-500' />
							1,000 API calls/month
						</li>
						<li className='flex items-center gap-2'>
							<Check className='size-4 text-green-500' />
							Basic analytics
						</li>
						<li className='flex items-center gap-2'>
							<Check className='size-4 text-green-500' />
							Email support
						</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}

export default DowngradePage
