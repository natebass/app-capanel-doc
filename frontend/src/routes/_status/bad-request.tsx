import { createFileRoute, Link } from '@tanstack/react-router'
import { AlertCircle, FileWarning, Home } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
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
					<FileWarning className='size-16 text-destructive' />
				</div>
			}
			title='400 - Bad Request'
			description='The request could not be understood by the server.'
			footer={
				<>
					<Button render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Go Home
					</Button>
					<Button variant='outline' onClick={() => window.history.back()}>
						Go Back
					</Button>
				</>
			}
		>
			<Alert variant='destructive'>
				<AlertCircle className='size-4' />
				<AlertTitle>Invalid Request</AlertTitle>
				<AlertDescription>
					Please check the URL or form data and try again. If the problem persists, contact support.
				</AlertDescription>
			</Alert>
		</StatusCard>
	)
}

export default BadRequestPage
