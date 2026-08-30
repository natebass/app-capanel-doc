import { LaptopIcon, Monitor, SmartPhone01Icon, Tick02Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/device-verified')({
	component: DeviceVerifiedPage,
	head: () => ({
		meta: [{ title: 'Device Verified' }],
	}),
})

function DeviceVerifiedPage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={LaptopIcon} className='size-16 text-green-500' />
				</div>
			}
			title='Device Verified'
			description='This device has been added to your trusted devices.'
			footer={<Button render={<Link to='/dashboard' />}>Continue to Dashboard</Button>}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Badge variant='default'>
						<HugeiconsIcon icon={Tick02Icon} className='mr-1 size-3' />
						Trusted
					</Badge>
				</div>

				<div className='rounded-lg border bg-muted/50 p-4'>
					<div className='flex items-center gap-3'>
						<HugeiconsIcon icon={Monitor} className='size-8 text-muted-foreground' />
						<div>
							<p className='font-medium text-sm'>Chrome on Linux</p>
							<p className='text-xs text-muted-foreground'>Added just now</p>
						</div>
					</div>
				</div>

				<Separator />

				<div className='text-sm text-muted-foreground text-center space-y-2'>
					<p>Your trusted devices:</p>
					<div className='flex justify-center gap-4'>
						<div className='flex items-center gap-1'>
							<HugeiconsIcon icon={Monitor} className='size-4' />
							<span>2</span>
						</div>
						<div className='flex items-center gap-1'>
							<HugeiconsIcon icon={SmartPhone01Icon} className='size-4' />
							<span>1</span>
						</div>
						<div className='flex items-center gap-1'>
							<HugeiconsIcon icon={LaptopIcon} className='size-4' />
							<span>1</span>
						</div>
					</div>
				</div>

				<Button variant='ghost' size='sm' className='w-full' render={<Link to='/user/settings' />}>
					Manage Devices
				</Button>
			</div>
		</StatusCard>
	)
}
