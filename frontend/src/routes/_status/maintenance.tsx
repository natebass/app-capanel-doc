import { createFileRoute, Link } from '@tanstack/react-router'
import { Clock, Construction, Home, Wrench } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/maintenance')({
	component: MaintenancePage,
	head: () => ({
		meta: [{ title: 'Scheduled Maintenance' }],
	}),
})

function MaintenancePage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6'>
					<Construction className='size-16 text-blue-500' />
				</div>
			}
			title='Scheduled Maintenance'
			description="We're performing scheduled maintenance to improve our services."
			footer={
				<>
					<Button variant='outline' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Go Home
					</Button>
					<Button variant='outline' render={<Link to='/status' />}>
						View Status
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Badge variant='outline'>
						<Wrench className='mr-1 size-3' />
						In Progress
					</Badge>
				</div>

				<Progress value={45}>
					<ProgressLabel>Maintenance Progress</ProgressLabel>
					<ProgressValue>45%</ProgressValue>
				</Progress>

				<Separator />

				<div className='space-y-2 text-sm'>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Started</span>
						<span className='flex items-center gap-1'>
							<Clock className='size-3' />
							2:00 AM UTC
						</span>
					</div>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Expected End</span>
						<span className='flex items-center gap-1'>
							<Clock className='size-3' />
							4:00 AM UTC
						</span>
					</div>
				</div>

				<Separator />

				<div className='text-center text-sm text-muted-foreground'>
					<p>Updates being performed:</p>
					<ul className='mt-2 space-y-1'>
						<li>Database optimization</li>
						<li>Security patches</li>
						<li>Performance improvements</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}

export default MaintenancePage
