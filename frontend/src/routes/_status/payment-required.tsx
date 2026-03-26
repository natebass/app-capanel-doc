import { CreditCardIcon, Home01Icon, SparklesIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/payment-required')({
	component: PaymentRequiredPage,
	head: () => ({
		meta: [{ title: '402 - Payment Required' }],
	}),
})

function PaymentRequiredPage() {
	return (
		<StatusCard
			variant='warning'
			icon={
				<div className='rounded-full bg-yellow-500/10 p-6'>
					<HugeiconsIcon icon={CreditCardIcon} className='size-16 text-yellow-500' />
				</div>
			}
			title='402 - Payment Required'
			description='You need an active subscription to access this feature.'
			footer={
				<>
					<Button render={<Link to='/dashboard' />}>
						<HugeiconsIcon icon={SparklesIcon} className='mr-2 size-4' />
						View Plans
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Separator />

				<div className='grid gap-2'>
					<Card size='sm'>
						<CardHeader className='pb-2'>
							<div className='flex items-center justify-between'>
								<CardTitle className='text-sm'>Pro Plan</CardTitle>
								<Badge variant='default'>Popular</Badge>
							</div>
							<CardDescription className='text-xs'>$29/month</CardDescription>
						</CardHeader>
						<CardContent className='text-xs text-muted-foreground'>
							Unlimited API calls, priority support
						</CardContent>
					</Card>

					<Card size='sm'>
						<CardHeader className='pb-2'>
							<CardTitle className='text-sm'>Team Plan</CardTitle>
							<CardDescription className='text-xs'>$99/month</CardDescription>
						</CardHeader>
						<CardContent className='text-xs text-muted-foreground'>
							Everything in Pro + team features
						</CardContent>
					</Card>
				</div>
			</div>
		</StatusCard>
	)
}
