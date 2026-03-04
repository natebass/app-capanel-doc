import { Link, type ErrorComponentProps } from '@tanstack/react-router'
import { AlertOctagon, Bug, Home, RefreshCcw } from 'lucide-react'

import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from '@/components/ui/accordion'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

import { StatusCard, StatusTemplate } from './StatusTemplate'

export interface DefaultErrorProps extends Partial<ErrorComponentProps> {
	/** Whether to show the full template with header/footer */
	fullPage?: boolean
}

export function DefaultError({ error, reset, info, fullPage = true }: DefaultErrorProps) {
	const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred'
	const errorStack = error instanceof Error ? error.stack : undefined

	const content = (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<AlertOctagon className='size-16 text-destructive' />
				</div>
			}
			title='Something Went Wrong'
			description='An unexpected error occurred while processing your request.'
			footer={
				<>
					{reset ? (
						<Button onClick={reset}>
							<RefreshCcw className='mr-2 size-4' />
							Try Again
						</Button>
					) : (
						<Button onClick={() => window.location.reload()}>
							<RefreshCcw className='mr-2 size-4' />
							Reload Page
						</Button>
					)}
					<Button variant='outline' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Alert variant='destructive'>
					<Bug className='size-4' />
					<AlertTitle>Error Details</AlertTitle>
					<AlertDescription className='break-words'>{errorMessage}</AlertDescription>
				</Alert>

				{(errorStack || info?.componentStack) && (
					<Accordion>
						<AccordionItem value='stack'>
							<AccordionTrigger className='text-sm'>Technical Details</AccordionTrigger>
							<AccordionContent>
								<div className='rounded-md bg-muted p-3 font-mono text-xs overflow-auto max-h-48'>
									<p className='mb-2'>Timestamp: {new Date().toISOString()}</p>
									<p className='mb-2'>
										URL: {typeof window !== 'undefined' ? window.location.href : 'Unknown'}
									</p>
									{errorStack && (
										<>
											<p className='font-semibold mb-1'>Stack Trace:</p>
											<pre className='whitespace-pre-wrap text-destructive/80'>{errorStack}</pre>
										</>
									)}
									{info?.componentStack && (
										<>
											<p className='font-semibold mb-1 mt-2'>Component Stack:</p>
											<pre className='whitespace-pre-wrap text-muted-foreground'>
												{info.componentStack}
											</pre>
										</>
									)}
								</div>
							</AccordionContent>
						</AccordionItem>
					</Accordion>
				)}
			</div>
		</StatusCard>
	)

	if (!fullPage) {
		return <div className='flex items-center justify-center min-h-[60vh] p-4'>{content}</div>
	}

	return <StatusTemplate>{content}</StatusTemplate>
}

export default DefaultError
