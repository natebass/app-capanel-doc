import { createFileRoute, Link } from '@tanstack/react-router'
import { Home, Search, SearchX } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/no-results')({
	component: NoResultsPage,
	head: () => ({
		meta: [{ title: 'No Results Found' }],
	}),
})

function NoResultsPage() {
	return (
		<StatusCard
			variant='default'
			icon={
				<div className='rounded-full bg-muted p-6'>
					<SearchX className='size-16 text-muted-foreground' />
				</div>
			}
			title='No Results Found'
			description="We couldn't find anything matching your search."
			footer={
				<Button variant='outline' render={<Link to='/' />}>
					<Home className='mr-2 size-4' />
					Go Home
				</Button>
			}
		>
			<div className='space-y-4'>
				<div className='flex gap-2'>
					<Input placeholder='Try a different search...' className='flex-1' />
					<Button variant='outline' size='icon'>
						<Search className='size-4' />
					</Button>
				</div>

				<Separator />

				<div className='text-center text-sm text-muted-foreground'>
					<p>Suggestions:</p>
					<ul className='mt-2 space-y-1 text-left'>
						<li>Check for typos in your search</li>
						<li>Try using different keywords</li>
						<li>Use more general search terms</li>
						<li>Browse our categories instead</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}

export default NoResultsPage
