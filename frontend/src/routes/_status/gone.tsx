import { AlertCircleIcon, Home01Icon, Search01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/gone')({
	component: GonePage,
	head: () => ({
		meta: [{ title: '410 - Gone' }],
	}),
})

function GonePage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-muted p-6'>
					<HugeiconsIcon icon={AlertCircleIcon} className='size-16 text-muted-foreground' />
				</div>
			}
			title='410 - Gone'
			description='This resource has been permanently removed.'
			footer={
				<Button render={<Link to='/' />}>
					<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
					Go Home
				</Button>
			}
		>
			<div className='space-y-4'>
				<p className='text-center text-sm text-muted-foreground'>
					The content you're looking for has been permanently deleted and is no longer available.
				</p>

				<Separator />

				<div className='space-y-2'>
					<p className='text-center text-sm text-muted-foreground'>
						Try searching for what you need:
					</p>
					<div className='flex gap-2'>
						<Input placeholder='Search...' className='flex-1' />
						<Button variant='outline' size='icon'>
							<HugeiconsIcon icon={Search01Icon} className='size-4' />
						</Button>
					</div>
				</div>
			</div>
		</StatusCard>
	)
}
