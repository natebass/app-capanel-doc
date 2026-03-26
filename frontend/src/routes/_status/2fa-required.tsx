import { Home01Icon, Shield01Icon, SmartPhone01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Button } from '@/components/ui/button'
import { InputOTP, InputOTPGroup, InputOTPSeparator, InputOTPSlot } from '@/components/ui/input-otp'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/2fa-required')({
	component: TwoFactorRequiredPage,
	head: () => ({
		meta: [{ title: 'Two-Factor Authentication' }],
	}),
})

function TwoFactorRequiredPage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6'>
					<HugeiconsIcon icon={Shield01Icon} className='size-16 text-blue-500' />
				</div>
			}
			title='Two-Factor Authentication'
			description='Enter the code from your authenticator app.'
			footer={
				<>
					<Button>Verify</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Cancel
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex justify-center'>
					<InputOTP maxLength={6}>
						<InputOTPGroup>
							<InputOTPSlot index={0} />
							<InputOTPSlot index={1} />
							<InputOTPSlot index={2} />
						</InputOTPGroup>
						<InputOTPSeparator />
						<InputOTPGroup>
							<InputOTPSlot index={3} />
							<InputOTPSlot index={4} />
							<InputOTPSlot index={5} />
						</InputOTPGroup>
					</InputOTP>
				</div>

				<Separator />

				<div className='flex items-center justify-center gap-2 text-sm text-muted-foreground'>
					<HugeiconsIcon icon={SmartPhone01Icon} className='size-4' />
					<span>Open your authenticator app</span>
				</div>

				<p className='text-center text-sm text-muted-foreground'>
					Don't have access to your device?{' '}
					<Link to='/recover-password' className='text-primary hover:underline'>
						Use a recovery code
					</Link>
				</p>
			</div>
		</StatusCard>
	)
}
