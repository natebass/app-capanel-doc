import type { VariantProps } from 'class-variance-authority'
import { forwardRef } from 'react'

import { Button, type buttonVariants } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'
import { cn } from '@/lib/utils'

export interface LoadingButtonProps
	extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
	loading?: boolean
}

const LoadingButton = forwardRef<HTMLButtonElement, LoadingButtonProps>(
	({ className, children, loading, disabled, ...props }, ref) => {
		return (
			<Button
				ref={ref}
				className={cn('relative', className)}
				disabled={loading || disabled}
				{...props}
			>
				{loading && (
					<Spinner className='absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2' />
				)}
				<span className={cn(loading && 'invisible')}>{children}</span>
			</Button>
		)
	},
)

LoadingButton.displayName = 'LoadingButton'

export { LoadingButton }
