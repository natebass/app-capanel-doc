import { Link } from '@tanstack/react-router'
import type { ReactNode } from 'react'

import { Button } from '@/components/ui/button'
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils.ts'

export interface StatusTemplateProps {
	children: ReactNode
	showHeader?: boolean
	showFooter?: boolean
}

export function StatusTemplate({
	children,
	showHeader = true,
	showFooter = true,
}: StatusTemplateProps) {
	return (
		<div className='min-h-screen bg-gradient-to-b from-background to-muted/30 flex flex-col'>
			{showHeader && (
				<header className='w-full border-b bg-background/80 backdrop-blur-sm'>
					<div className='container mx-auto px-4 py-4 flex items-center justify-between'>
						<Link to='/' className='text-xl font-bold tracking-tight'>
							FastAPI Cloud
						</Link>
						<nav className='flex items-center gap-2'>
							<Button variant='ghost' size='sm' render={<Link to='/' />}>
								Home
							</Button>
							<Button variant='ghost' size='sm' render={<Link to='/status' />}>
								Status
							</Button>
						</nav>
					</div>
				</header>
			)}

			<main className='flex-1 flex items-center justify-center p-4'>{children}</main>

			{showFooter && (
				<footer className='border-t bg-background/80 backdrop-blur-sm'>
					<div className='container mx-auto px-4 py-6'>
						<div className='flex flex-col md:flex-row items-center justify-between gap-4'>
							<p className='text-sm text-muted-foreground'>FastAPI Cloud Status Portal</p>
							<div className='flex items-center gap-4 text-sm text-muted-foreground'>
								<Link to='/status' className='hover:text-foreground transition-colors'>
									System Status
								</Link>
								<Separator orientation='vertical' className='h-4' />
								<a
									href='https://docs.example.com'
									className='hover:text-foreground transition-colors'
								>
									Documentation
								</a>
								<Separator orientation='vertical' className='h-4' />
								<Link to='/' className='hover:text-foreground transition-colors'>
									Support
								</Link>
							</div>
						</div>
					</div>
				</footer>
			)}
		</div>
	)
}

export interface StatusCardProps {
	icon?: ReactNode
	title: string
	description?: string
	children?: ReactNode
	footer?: ReactNode
	variant?: 'default' | 'error' | 'warning' | 'success' | 'info'
	className?: string
}

export function StatusCard({
	icon,
	title,
	description,
	children,
	footer,
	variant = 'default',
	className,
}: StatusCardProps) {
	const variantStyles = {
		default: '',
		error: 'border-destructive/50',
		warning: 'border-yellow-500/50',
		success: 'border-green-500/50',
		info: 'border-blue-500/50',
	}

	return (
		<Card className={cn('w-full max-w-md', variantStyles[variant], className)}>
			<CardHeader className='text-center'>
				{icon && <div className='mx-auto mb-4'>{icon}</div>}
				<CardTitle className='text-2xl'>{title}</CardTitle>
				{description && <CardDescription className='text-base'>{description}</CardDescription>}
			</CardHeader>
			{children && <CardContent>{children}</CardContent>}
			{footer && <CardFooter className='justify-center gap-2'>{footer}</CardFooter>}
		</Card>
	)
}

export default StatusTemplate
