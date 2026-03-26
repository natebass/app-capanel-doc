import { Folder01Icon, Home01Icon, PlusSignIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/empty-state')({
	component: EmptyStatePage,
	head: () => ({
		meta: [{ title: 'No items Yet' }],
	}),
})

function EmptyStatePage() {
	return (
		<StatusCard
			variant='default'
			icon={
				<div className='rounded-full bg-muted p-6'>
					<HugeiconsIcon icon={Folder01Icon} className='size-16 text-muted-foreground' />
				</div>
			}
			title='No Items Yet'
			description='This space is empty. Start by creating your first item.'
			footer={
				<>
					<Button>
						<HugeiconsIcon icon={PlusSignIcon} className='mr-2 size-4' />
						Create Item
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4 text-center'>
				<Separator />
				<p className='text-sm text-muted-foreground'>
					Items you create will appear here. Get started by clicking the button above.
				</p>
			</div>
		</StatusCard>
	)
}
