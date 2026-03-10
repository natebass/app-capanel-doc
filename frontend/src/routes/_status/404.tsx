import { createFileRoute, Link } from '@tanstack/react-router'
import { FileQuestion, Home, Search } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export const Route = createFileRoute('/_status/404')({
	component: NotFoundPage,
	head: () => ({
		meta: [{ title: '404 - Page Not Found' }],
	}),
})

function NotFoundPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<FileQuestion className='size-16 text-destructive' />
				</div>
			}
			title='404 - Page Not Found'
			description="The page you're looking for doesn't exist or has been moved."
			footer={
				<>
					<Button render={<Link to='/' />}>
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
				<p className='text-center text-sm text-muted-foreground'>
					Try searching for what you need:
				</p>
				<div className='flex gap-2'>
					<Input placeholder='Search...' className='flex-1' />
					<Button variant='outline' size='icon'>
						<Search className='size-4' />
					</Button>
				</div>
			</div>
		</StatusCard>
	)
}

export default NotFoundPage
