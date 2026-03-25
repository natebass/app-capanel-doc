import { Tick02Icon, Home01Icon, SparklesIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/success')({
	component: SuccessPage,
	head: () => ({
		meta: [{ title: 'Success!' }],
	}),
})

function SuccessPage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={Tick02Icon} className='size-16 text-green-500' />
				</div>
			}
			title='Success!'
			description='Your action was completed successfully.'
			footer={
				<>
					<Button render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
					<Button variant='outline' render={<Link to='/dashboard' />}>
						Go to Dashboard
					</Button>
				</>
			}
		>
			<div className='space-y-4 text-center'>
				<div className='flex items-center justify-center gap-2'>
					<HugeiconsIcon icon={SparklesIcon} className='size-5 text-yellow-500' />
					<Badge variant='default'>Completed</Badge>
					<HugeiconsIcon icon={SparklesIcon} className='size-5 text-yellow-500' />
				</div>

				<Separator />

				<div className='space-y-2 text-sm text-muted-foreground'>
					<p>What's next?</p>
					<ul className='space-y-1'>
						<li>
							<Link to='/dashboard' className='text-primary hover:underline'>
								View your dashboard
							</Link>
						</li>
						<li>
							<Link to='/user/settings' className='text-primary hover:underline'>
								Update your settings
							</Link>
						</li>
						<li>
							<Link to='/' className='text-primary hover:underline'>
								Read the documentation
							</Link>
						</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}
