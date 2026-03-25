import {
	Alert01Icon as AlertCircle,
	FileQuestionMarkIcon as FileWarning,
	Home01Icon as Home,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/bad-request')({
	component: BadRequestPage,
	head: () => ({
		meta: [{ title: '400 - Bad Request' }],
	}),
})

function BadRequestPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={FileWarning} className='size-16 text-destructive' />
				</div>
			}
			title='400 - Bad Request'
			description='The request could not be understood by the server.'
			footer={
				<>
					<Button render={<Link to='/' />}>
						<HugeiconsIcon icon={Home} className='mr-2 size-4' />
						Go Home
					</Button>
					<Button variant='outline' onClick={() => window.history.back()}>
						Go Back
					</Button>
				</>
			}
		>
			<Alert variant='destructive'>
				<HugeiconsIcon icon={AlertCircle} className='size-4' />
				<AlertTitle>Invalid Request</AlertTitle>
				<AlertDescription>
					Please check the URL or form data and try again. If the problem persists, contact support.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}
