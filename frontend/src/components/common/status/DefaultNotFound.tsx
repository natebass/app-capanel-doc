import { FileQuestionMarkIcon, Home01Icon, Search01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { Link, type NotFoundRouteProps } from '@tanstack/react-router'
import type { ReactNode } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import { StatusCard, StatusTemplate } from './StatusTemplate'

export interface DefaultNotFoundProps {
	/** Data passed from notFoundComponent */
	data?: NotFoundRouteProps['data']
	/** Whether to show the full template with header/footer (default: true for standalone, false when nested) */
	fullPage?: boolean
}

export function DefaultNotFound({ data, fullPage = true }: DefaultNotFoundProps) {
	const content = (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={FileQuestionMarkIcon} className='size-16 text-destructive' />
				</div>
			}
			title='404 - Page Not Found'
			description="The page you're looking for doesn't exist or has been moved."
			footer={
				<>
					<Button render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
					<Button variant='outline' render={<Link to='/status' />}>
						View Status
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<p className='text-center text-sm text-muted-foreground'>
					Try searching for what you need:
				</p>
				<div className='flex gap-2'>
					<Input placeholder='Search...' className='flex-1' />
					<Button variant='outline' size='icon'>
						<HugeiconsIcon icon={Search01Icon} className='size-4' />
					</Button>
				</div>
				{data != null ? (
					<p className='text-center text-xs text-muted-foreground font-mono'>
						Path:{' '}
						{typeof data === 'object' && 'pathname' in data ? String(data.pathname) : 'Unknown'}
					</p>
				) : null}
			</div>
		</StatusCard>
	) as ReactNode

	if (!fullPage) {
		return <div className='flex items-center justify-center min-h-[60vh] p-4'>{content}</div>
	}

	return <StatusTemplate>{content}</StatusTemplate>
}

export default DefaultNotFound
