import {
	ArrowRight01Icon as ArrowRight,
	Book01Icon as BookOpen,
	RocketIcon as Rocket,
	Settings01Icon as Settings,
	SparklesIcon as Sparkles,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/welcome')({
	component: WelcomePage,
	head: () => ({
		meta: [{ title: 'Welcome!' }],
	}),
})

function WelcomePage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={Sparkles} className='size-16 text-green-500' />
				</div>
			}
			title='Welcome to FastAPI Cloud!'
			description='Your account has been successfully created.'
			footer={
				<Button render={<Link to='/dashboard' />}>
					Get Started
					<HugeiconsIcon icon={ArrowRight} className='ml-2 size-4' />
				</Button>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center'>
					<Badge variant='default'>
						<HugeiconsIcon icon={Sparkles} className='mr-1 size-3' />
						Account Active
					</Badge>
				</div>

				<Separator />

				<div className='space-y-3'>
					<p className='text-center text-sm text-muted-foreground'>Quick start guide:</p>

					<Card size='sm'>
						<CardHeader className='pb-2'>
							<CardTitle className='flex items-center gap-2 text-sm'>
								<HugeiconsIcon icon={Rocket} className='size-4' />
								Explore the Dashboard
							</CardTitle>
						</CardHeader>
						<CardContent>
							<CardDescription className='text-xs'>
								<Link to='/dashboard' className='text-primary hover:underline'>
									View your dashboard
								</Link>
							</CardDescription>
						</CardContent>
					</Card>

					<Card size='sm'>
						<CardHeader className='pb-2'>
							<CardTitle className='flex items-center gap-2 text-sm'>
								<HugeiconsIcon icon={Settings} className='size-4' />
								Configure Settings
							</CardTitle>
						</CardHeader>
						<CardContent>
							<CardDescription className='text-xs'>
								<Link to='/user/settings' className='text-primary hover:underline'>
									Update your preferences
								</Link>
							</CardDescription>
						</CardContent>
					</Card>

					<Card size='sm'>
						<CardHeader className='pb-2'>
							<CardTitle className='flex items-center gap-2 text-sm'>
								<HugeiconsIcon icon={BookOpen} className='size-4' />
								Read the Docs
							</CardTitle>
						</CardHeader>
						<CardContent>
							<CardDescription className='text-xs'>
								<Link to='/' className='text-primary hover:underline'>
									Learn how to get the most out of FastAPI Cloud
								</Link>
							</CardDescription>
						</CardContent>
					</Card>
				</div>
			</div>
		</StatusCard>
	)
}
