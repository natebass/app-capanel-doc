import { Home01Icon, Login01Icon, UserCircleIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/login-required')({
	component: LoginRequiredPage,
	head: () => ({
		meta: [{ title: 'Login Required' }],
	}),
})

function LoginRequiredPage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6'>
					<HugeiconsIcon icon={UserCircleIcon} className='size-16 text-blue-500' />
				</div>
			}
			title='Login Required'
			description='Please sign in to access this content.'
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
					This page requires authentication. Please sign in with your account to continue.
				</p>
				<Separator />
				<p className='text-sm text-muted-foreground'>
					New user?{' '}
					<Link to='/sign-up' className='text-primary hover:underline'>
						Create an account
					</Link>
				</p>
			</div>
		</StatusCard>
	)
}
