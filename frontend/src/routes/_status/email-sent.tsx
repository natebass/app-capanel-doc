import { Home01Icon, Mail01Icon, RefreshIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/email-sent')({
	component: EmailSentPage,
	head: () => ({
		meta: [{ title: 'Email Sent' }],
	}),
})

function EmailSentPage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={Mail01Icon} className='size-16 text-green-500' />
				</div>
			}
			title='Email Sent'
			description="We've sent an email to your address."
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
			<div className='space-y-4 text-center'>
				<p className='text-sm text-muted-foreground'>
					Please check your inbox and follow the instructions in the email.
				</p>

				<Separator />

				<div className='text-sm text-muted-foreground'>
					<p>Can't find the email?</p>
					<ul className='mt-2 space-y-1 text-left'>
						<li>Check your spam or junk folder</li>
						<li>Make sure the email address is correct</li>
						<li>Wait a few minutes and try again</li>
					</ul>
				</div>
			</div>
		</StatusCard>
	)
}
