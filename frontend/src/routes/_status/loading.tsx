import { Loading01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute } from '@tanstack/react-router'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Spinner } from '@/components/ui/spinner'

export const Route = createFileRoute('/_status/loading')({
	component: LoadingDemoPage,
	head: () => ({
		meta: [{ title: 'Loading States Demo' }],
	}),
})

function LoadingDemoPage() {
	return (
		<div className='w-full max-w-4xl space-y-8'>
			<Card>
				<CardHeader className='text-center'>
					<div className='mx-auto mb-4'>
						<div className='rounded-full bg-primary/10 p-4'>
							<HugeiconsIcon icon={Loading01Icon} className='size-12 text-primary animate-spin' />
						</div>
					</div>
					<CardTitle className='text-3xl'>Loading States</CardTitle>
					<CardDescription className='text-base'>
						Different loading patterns available in the status system
					</CardDescription>
				</CardHeader>
			</Card>

			<div className='grid gap-6 md:grid-cols-2'>
				{/* Spinner Variant */}
				<Card>
					<CardHeader>
						<CardTitle className='text-lg'>Spinner Loading</CardTitle>
						<CardDescription>Simple spinner for quick loads</CardDescription>
					</CardHeader>
					<CardContent>
						<div className='flex flex-col items-center gap-4 p-4 rounded-lg bg-muted/50'>
							<Spinner className='size-8' />
							<p className='text-sm text-muted-foreground'>Loading...</p>
						</div>
						<Separator className='my-4' />
						<p className='text-xs text-muted-foreground'>
							Used by:{' '}
							<code className='bg-muted px-1 rounded'>DefaultPending variant="spinner"</code>
						</p>
					</CardContent>
				</Card>

				{/* Card Variant */}
				<Card>
					<CardHeader>
						<CardTitle className='text-lg'>Card Loading</CardTitle>
						<CardDescription>Rich loading state with progress</CardDescription>
					</CardHeader>
					<CardContent>
						<div className='p-4 rounded-lg bg-muted/50 space-y-4'>
							<div className='flex items-center justify-center'>
								<HugeiconsIcon icon={Loading01Icon} className='size-8 text-primary animate-spin' />
							</div>
							<Progress value={65}>
								<ProgressLabel>Loading</ProgressLabel>
								<ProgressValue>{() => '65%'}</ProgressValue>
							</Progress>
						</div>
						<Separator className='my-4' />
						<p className='text-xs text-muted-foreground'>
							Used by: <code className='bg-muted px-1 rounded'>DefaultPending variant="card"</code>
						</p>
					</CardContent>
				</Card>

				{/* Skeleton Variant */}
				<Card>
					<CardHeader>
						<CardTitle className='text-lg'>Skeleton Loading</CardTitle>
						<CardDescription>Content placeholder skeleton</CardDescription>
					</CardHeader>
					<CardContent>
						<div className='space-y-3 p-4 rounded-lg bg-muted/50'>
							<Skeleton className='h-6 w-3/4' />
							<Skeleton className='h-4 w-full' />
							<Skeleton className='h-4 w-full' />
							<Skeleton className='h-4 w-2/3' />
						</div>
						<Separator className='my-4' />
						<p className='text-xs text-muted-foreground'>
							Used by:{' '}
							<code className='bg-muted px-1 rounded'>DefaultPending variant="skeleton"</code>
						</p>
					</CardContent>
				</Card>

				{/* Usage Example */}
				<Card>
					<CardHeader>
						<CardTitle className='text-lg'>TanStack Integration</CardTitle>
						<CardDescription>How to use in your routes</CardDescription>
					</CardHeader>
					<CardContent>
						<div className='rounded-lg bg-muted p-4 font-mono text-xs overflow-auto'>
							<pre>{`// In your route file
export const Route = createFileRoute('/my-route')({
  component: MyComponent,
  pendingComponent: () => (
    <DefaultPending
      variant="card"
      message="Loading data..."
      showProgress
      progress={50}
    />
  ),
})`}</pre>
						</div>
						<Separator className='my-4' />
						<div className='flex gap-2'>
							<Badge variant='outline'>pendingComponent</Badge>
							<Badge variant='outline'>Suspense</Badge>
						</div>
					</CardContent>
				</Card>
			</div>

			<Card>
				<CardHeader>
					<CardTitle className='text-lg'>Live Demo</CardTitle>
					<CardDescription>Click to see the loading states in action</CardDescription>
				</CardHeader>
				<CardContent className='flex flex-wrap gap-2'>
					<Button variant='outline' onClick={() => (window.location.href = '/processing')}>
						View Processing Page
					</Button>
					<Button variant='outline' onClick={() => (window.location.href = '/queued')}>
						View Queued Page
					</Button>
				</CardContent>
			</Card>
		</div>
	)
}
