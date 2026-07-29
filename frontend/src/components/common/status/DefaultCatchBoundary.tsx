import {
	Alert01Icon,
	Home01Icon,
	RefreshIcon,
	ArrowTurnBackwardIcon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { Link, type ErrorComponentProps, useRouter } from '@tanstack/react-router'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

import { StatusCard, StatusTemplate } from './StatusTemplate'

export interface DefaultCatchBoundaryProps extends Partial<ErrorComponentProps> {
	/** Whether to show the full template with header/footer */
	fullPage?: boolean
}

/**
 * A catch-all error boundary component that provides navigation-aware error recovery.
 * This is useful for route-level error boundaries where you want to offer
 * the user options to retry or navigate away.
 */
export function DefaultCatchBoundary({ error, reset, fullPage = true }: DefaultCatchBoundaryProps) {
	const router = useRouter()

	const isNotFound = error instanceof Error && error.message.includes('Not Found')
	const isNetworkError =
		error instanceof Error &&
		(error.message.includes('fetch') ||
			error.message.includes('network') ||
			error.message.includes('Failed to fetch'))

	const getErrorInfo = () => {
		if (isNotFound) {
			return {
				title: 'Page Not Found',
				description: 'The requested resource could not be found.',
				variant: 'warning' as const,
			}
		}
		if (isNetworkError) {
			return {
				title: 'Network Error',
				description: 'Unable to connect. Please check your internet connection.',
				variant: 'warning' as const,
			}
		}
		return {
			title: 'Something Went Wrong',
			description: 'An unexpected error occurred.',
			variant: 'error' as const,
		}
	}

	const errorInfo = getErrorInfo()
	const errorMessage = error instanceof Error ? error.message : 'Unknown error'

	const handleRetry = () => {
		if (reset) {
			reset()
		} else {
			void router.invalidate()
		}
	}

	const content = (
		<StatusCard
			variant={errorInfo.variant}
			icon={
				<div
					className={`rounded-full p-6 ${errorInfo.variant === 'error' ? 'bg-destructive/10' : 'bg-yellow-500/10'}`}
				>
					<HugeiconsIcon
						icon={Alert01Icon}
						className={`size-16 ${errorInfo.variant === 'error' ? 'text-destructive' : 'text-yellow-500'}`}
					/>
				</div>
			}
			title={errorInfo.title}
			description={errorInfo.description}
			footer={
				<>
					<Button onClick={handleRetry}>
						<HugeiconsIcon icon={RefreshIcon} className='mr-2 size-4' />
						Try Again
					</Button>
					<Button variant='outline' onClick={() => router.history.back()}>
						<HugeiconsIcon icon={ArrowTurnBackwardIcon} className='mr-2 size-4' />
						Go Back
					</Button>
					<Button variant='ghost' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Home
					</Button>
				</>
			}
		>
			<Alert variant={errorInfo.variant === 'error' ? 'destructive' : 'default'}>
				<HugeiconsIcon icon={Alert01Icon} className='size-4' />
				<AlertTitle>Error Details</AlertTitle>
				<AlertDescription className='break-words font-mono text-xs'>
					{errorMessage}
				</AlertDescription>
			</Alert>
		</StatusCard>
	)

	if (!fullPage) {
		return <div className='flex items-center justify-center min-h-[60vh] p-4'>{content}</div>
	}

	return <StatusTemplate>{content}</StatusTemplate>
}

export default DefaultCatchBoundary
