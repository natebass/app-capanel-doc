import { Home01Icon, Key01Icon, Login01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/401')({
	component: UnauthorizedPage,
	head: () => ({
		meta: [{ title: '401 - Unauthorized' }],
	}),
})

function UnauthorizedPage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<HugeiconsIcon icon={Key01Icon} className='size-16 text-yellow-500' />
				</div>
			}
			title='401 - Unauthorized'
			description='You need to sign in to access this page.'
			footer={
				<>
					<Button render={<Link to='/login' />}>
						<HugeiconsIcon icon={Login01Icon} className='mr-2 size-4' />
						Sign In
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4 text-center'>
				<p className='text-sm text-muted-foreground'>
					Please sign in with your credentials to continue.
				</p>
				<Separator />
				<p className='text-sm text-muted-foreground'>
					Don't have an account?{' '}
					<Link to='/sign-up' className='text-primary hover:underline'>
						Sign up
					</Link>
				</p>
			</div>
		</StatusCard>
	)
}
