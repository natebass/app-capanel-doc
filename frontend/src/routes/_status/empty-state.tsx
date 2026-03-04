import { createFileRoute, Link } from '@tanstack/react-router'
import { FolderOpen, Home, Plus } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/empty-state')({
	component: EmptyStatePage,
	head: () => ({
		meta: [{ title: 'No Items Yet' }],
	}),
})

function EmptyStatePage() {
	return (
		<StatusCard
			variant='default'
			icon={
				<div className='rounded-full bg-muted p-6'>
					<FolderOpen className='size-16 text-muted-foreground' />
				</div>
			}
			title='No Items Yet'
			description='This space is empty. Start by creating your first item.'
			footer={
				<>
					<Button>
						<Plus className='mr-2 size-4' />
						Create Item
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
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

export default EmptyStatePage
