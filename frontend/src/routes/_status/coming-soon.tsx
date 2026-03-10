import { createFileRoute, Link } from '@tanstack/react-router'
import { Bell, Home, Rocket, Sparkles } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/coming-soon')({
	component: ComingSoonPage,
	head: () => ({
		meta: [{ title: 'Coming Soon' }],
	}),
})

function ComingSoonPage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6'>
					<Rocket className='size-16 text-blue-500' />
				</div>
			}
			title='Coming Soon'
			description="We're working on something exciting. Stay tuned!"
			footer={
				<Button variant='outline' render={<Link to='/' />}>
					<Home className='mr-2 size-4' />
					Go Home
				</Button>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2 text-sm text-muted-foreground'>
					<Sparkles className='size-4 text-yellow-500' />
					<span>New features launching soon</span>
				</div>

				<Separator />

				<div className='space-y-2'>
					<p className='text-center text-sm text-muted-foreground'>Get notified when we launch:</p>
					<div className='flex gap-2'>
						<Input type='email' placeholder='your@email.com' className='flex-1' />
						<Button size='icon'>
							<Bell className='size-4' />
						</Button>
					</div>
				</div>

				<Separator />

				<div className='grid grid-cols-3 gap-4 text-center'>
					<div>
						<div className='text-2xl font-bold'>12</div>
						<div className='text-xs text-muted-foreground'>Days</div>
					</div>
					<div>
						<div className='text-2xl font-bold'>08</div>
						<div className='text-xs text-muted-foreground'>Hours</div>
					</div>
					<div>
						<div className='text-2xl font-bold'>45</div>
						<div className='text-xs text-muted-foreground'>Minutes</div>
					</div>
				</div>
			</div>
		</StatusCard>
	)
}

export default ComingSoonPage
