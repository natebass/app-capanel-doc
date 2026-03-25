import { Loading01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { Spinner } from '@/components/ui/spinner'

import { StatusTemplate } from './StatusTemplate'

export interface DefaultPendingProps {
	/** Whether to show the full template with header/footer */
	fullPage?: boolean
	/** Custom message to display */
	message?: string
	/** Show progress bar */
	showProgress?: boolean
	/** Progress value (0-100) */
	progress?: number
	/** Variant style */
	variant?: 'spinner' | 'skeleton' | 'card'
}

export function DefaultPending({
	fullPage = true,
	message = 'Loading...',
	showProgress = false,
	progress,
	variant = 'spinner',
}: DefaultPendingProps) {
	const content = (() => {
		switch (variant) {
			case 'skeleton':
				return (
					<div className='w-full max-w-md space-y-4 p-4'>
						<Skeleton className='h-8 w-3/4' />
						<Skeleton className='h-4 w-full' />
						<Skeleton className='h-4 w-full' />
						<Skeleton className='h-4 w-2/3' />
						<div className='flex gap-2 pt-4'>
							<Skeleton className='h-10 w-24' />
							<Skeleton className='h-10 w-24' />
						</div>
					</div>
				)

			case 'card':
				return (
					<Card className='w-full max-w-md'>
						<CardHeader className='text-center'>
							<div className='mx-auto mb-4'>
								<div className='rounded-full bg-primary/10 p-6'>
									<HugeiconsIcon
										icon={Loading01Icon}
										className='size-16 text-primary animate-spin'
									/>
								</div>
							</div>
							<CardTitle className='text-2xl'>{message}</CardTitle>
							<CardDescription>Please wait while we load your content.</CardDescription>
						</CardHeader>
						{showProgress && (
							<CardContent>
								<Progress value={progress ?? 0} />
								{progress !== undefined && (
									<p className='text-center text-sm text-muted-foreground mt-2'>
										{Math.round(progress)}% complete
									</p>
								)}
							</CardContent>
						)}
					</Card>
				)

			case 'spinner':
			default:
				return (
					<div className='flex flex-col items-center justify-center gap-4'>
						<Spinner className='size-12' />
						<p className='text-muted-foreground'>{message}</p>
						{showProgress && (
							<div className='w-48'>
								<Progress value={progress ?? 0} />
							</div>
						)}
					</div>
				)
		}
	})()

	if (!fullPage) {
		return <div className='flex items-center justify-center min-h-[60vh] p-4'>{content}</div>
	}

	return (
		<StatusTemplate showHeader={false} showFooter={false}>
			{content}
		</StatusTemplate>
	)
}

export default DefaultPending
