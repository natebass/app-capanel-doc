import { createFileRoute, Link } from '@tanstack/react-router'
import { GitMerge, Home, RefreshCcw } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/conflict')({
	component: ConflictPage,
	head: () => ({
		meta: [{ title: '409 - Conflict' }],
	}),
})

function ConflictPage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<GitMerge className='size-16 text-yellow-500' />
				</div>
			}
			title='409 - Conflict'
			description='The request conflicts with the current state of the resource.'
			footer={
				<>
					<Button onClick={() => window.location.reload()}>
						<RefreshCcw className='mr-2 size-4' />
						Refresh
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<Alert>
				<GitMerge className='size-4' />
				<AlertTitle>Resource Conflict</AlertTitle>
				<AlertDescription>
					This usually happens when the resource was modified by another request. Please refresh and
					try again.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}

export default ConflictPage
