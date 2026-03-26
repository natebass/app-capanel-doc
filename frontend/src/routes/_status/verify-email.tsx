import { Home01Icon, Mail01Icon, RefreshIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/verify-email')({
	component: VerifyEmailPage,
	head: () => ({
		meta: [{ title: 'Verify Your Email' }],
	}),
})

function VerifyEmailPage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6'>
					<HugeiconsIcon icon={Mail01Icon} className='size-16 text-blue-500' />
				</div>
			}
			title='Verify Your Email'
			description='Please check your inbox and click the verification link.'
			footer={
				<>
					<Button variant='outline'>
						<HugeiconsIcon icon={RefreshIcon} className='mr-2 size-4' />
						Resend Email
					</Button>
					<Button variant='ghost' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Alert>
					<HugeiconsIcon icon={Mail01Icon} className='size-4' />
					<AlertTitle>Check Your Inbox</AlertTitle>
					<AlertDescription>
						We've sent a verification email to your registered email address.
					</AlertDescription>
				</Alert>

				<Separator />

				<div className='text-center text-sm text-muted-foreground'>
					<p>Didn't receive the email?</p>
					<ul className='mt-2 space-y-1 text-left'>
						<li>Check your spam folder</li>
						<li>Make sure your email address is correct</li>
						<li>Wait a few minutes and try again</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}
