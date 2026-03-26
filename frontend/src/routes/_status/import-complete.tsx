import { ArrowRight01Icon, Home01Icon, Tick01Icon, Upload02Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress, ProgressLabel, ProgressValue } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/import-complete')({
	component: ImportCompletePage,
	head: () => ({
		meta: [{ title: 'Import Complete' }],
	}),
})

function ImportCompletePage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={Upload02Icon} className='size-16 text-green-500' />
				</div>
			}
			title='Import Complete'
			description='Your data has been imported successfully.'
			footer={
				<>
					<Button render={<Link to='/dashboard' />}>
						View Data
						<HugeiconsIcon icon={ArrowRight01Icon} className='ml-2 size-4' />
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Badge variant='default'>
						<HugeiconsIcon icon={Tick01Icon} className='mr-1 size-3' />
						Success
					</Badge>
				</div>

				<Progress value={100}>
					<ProgressLabel>Import Progress</ProgressLabel>
					<ProgressValue>{() => '100%'}</ProgressValue>
				</Progress>

				<Separator />

				<div className='space-y-2 text-sm'>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Total Records</span>
						<span className='font-medium'>2,500</span>
					</div>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Imported</span>
						<span className='font-medium text-green-500'>2,487</span>
					</div>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Skipped</span>
						<span className='font-medium text-yellow-500'>13</span>
					</div>
				</div>
			</div>
		</StatusCard>
	)
}
