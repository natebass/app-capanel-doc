import { createFileRoute, Link } from '@tanstack/react-router'
import { HardHat, Home, Wrench } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/under-construction')({
	component: UnderConstructionPage,
	head: () => ({
		meta: [{ title: 'Under Construction' }],
	}),
})

function UnderConstructionPage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6'>
					<HardHat className='size-16 text-blue-500' />
				</div>
			}
			title='Under Construction'
			description="We're building something amazing here!"
			footer={
				<Button variant='outline' render={<Link to='/' />}>
					<Home className='mr-2 size-4' />
					Go Home
				</Button>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Badge variant='outline'>
						<Wrench className='mr-1 size-3' />
						Work in Progress
					</Badge>
				</div>

				<Progress value={35}>
					<ProgressLabel>Build Progress</ProgressLabel>
					<ProgressValue>{() => '35%'}</ProgressValue>
				</Progress>

				<Separator />

				<div className='text-center text-sm text-muted-foreground'>
					<p>What we're working on:</p>
					<ul className='mt-2 space-y-1'>
						<li>New dashboard design</li>
						<li>Enhanced analytics</li>
						<li>Team collaboration features</li>
						<li>API improvements</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}

export default UnderConstructionPage
