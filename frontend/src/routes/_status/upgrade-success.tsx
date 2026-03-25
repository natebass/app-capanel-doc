import {
	ArrowRight01Icon as ArrowRight,
	Tick01Icon as Check,
	CrownIcon as Crown,
	SparklesIcon as PartyPopper,
	SparklesIcon as Sparkles,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/upgrade-success')({
	component: UpgradeSuccessPage,
	head: () => ({
		meta: [{ title: 'Upgrade Successful!' }],
	}),
})

function UpgradeSuccessPage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={Crown} className='size-16 text-green-500' />
				</div>
			}
			title='Upgrade Successful!'
			description='Welcome to Pro! Your new features are now active.'
			footer={
				<Button render={<Link to='/dashboard' />}>
					Explore New Features
					<HugeiconsIcon icon={ArrowRight} className='ml-2 size-4' />
				</Button>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<HugeiconsIcon icon={PartyPopper} className='size-5 text-yellow-500' />
					<Badge variant='default'>
						<HugeiconsIcon icon={Sparkles} className='mr-1 size-3' />
						Pro Member
					</Badge>
					<HugeiconsIcon icon={PartyPopper} className='size-5 text-yellow-500' />
				</div>

				<Separator />

				<div className='space-y-2 text-sm'>
					<p className='font-medium text-center'>New features unlocked:</p>
					<ul className='space-y-1 text-muted-foreground'>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Check} className='size-4 text-green-500' />
							Unlimited API calls
						</li>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Check} className='size-4 text-green-500' />
							Priority support
						</li>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Check} className='size-4 text-green-500' />
							Advanced analytics
						</li>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Check} className='size-4 text-green-500' />
							Team collaboration
						</li>
						<li className='flex items-center gap-2'>
							<HugeiconsIcon icon={Check} className='size-4 text-green-500' />
							Custom integrations
						</li>
					</ul>
				</div>

				<Separator />

				<p className='text-center text-sm text-muted-foreground'>
					Thank you for upgrading! Your support helps us build better tools.
				</p>
			</div>
		</StatusCard>
	)
}
