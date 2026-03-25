import { AlertCircleIcon, Bug01Icon, Home01Icon, RefreshIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from '@/components/ui/accordion'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_status/error')({
	component: GenericErrorPage,
	head: () => ({
		meta: [{ title: 'Error Occurred' }],
	}),
})

function GenericErrorPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={AlertCircleIcon} className='size-16 text-destructive' />
				</div>
			}
			title='Something Went Wrong'
			description='An unexpected error occurred while processing your request.'
			footer={
				<>
					<Button onClick={() => window.location.reload()}>
						<HugeiconsIcon icon={RefreshIcon} className='mr-2 size-4' />
						Try Again
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Alert variant='destructive'>
					<HugeiconsIcon icon={Bug01Icon} className='size-4' />
					<AlertTitle>Error Code: E_UNKNOWN</AlertTitle>
					<AlertDescription>
						This error has been logged and our team will investigate.
					</AlertDescription>
				</Alert>

				<Accordion>
					<AccordionItem value='details'>
						<AccordionTrigger className='text-sm'>Technical Details</AccordionTrigger>
						<AccordionContent>
							<div className='rounded-md bg-muted p-3 font-mono text-xs'>
								<p>Timestamp: {new Date().toISOString()}</p>
								<p>Request ID: req_abc123xyz</p>
								<p>
									User Agent:{' '}
									{typeof navigator !== 'undefined'
										? navigator.userAgent.substring(0, 50) + '...'
										: 'Unknown'}
								</p>
							</div>
						</AccordionContent>
					</AccordionItem>
				</Accordion>
			</div>
		</StatusCard>
	)
}
