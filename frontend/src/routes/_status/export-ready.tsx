import { Download01Icon, FileDownloadIcon, Home01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/export-ready')({
	component: ExportReadyPage,
	head: () => ({
		meta: [{ title: 'Export Ready' }],
	}),
})

function ExportReadyPage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={FileDownloadIcon} className='size-16 text-green-500' />
				</div>
			}
			title='Export Ready'
			description='Your data export has been generated successfully.'
			footer={
				<>
					<Button>
						<HugeiconsIcon icon={Download01Icon} className='mr-2 size-4' />
						Download
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
					<Badge variant='default'>Ready</Badge>
				</div>

				<div className='rounded-lg border bg-muted/50 p-4'>
					<div className='flex items-center justify-between text-sm'>
						<span className='text-muted-foreground'>File</span>
						<span className='font-medium'>export_2026-02-01.zip</span>
					</div>
					<Separator className='my-2' />
					<div className='flex items-center justify-between text-sm'>
						<span className='text-muted-foreground'>Size</span>
						<span className='font-medium'>24.5 MB</span>
					</div>
					<Separator className='my-2' />
					<div className='flex items-center justify-between text-sm'>
						<span className='text-muted-foreground'>Records</span>
						<span className='font-medium'>1,234</span>
					</div>
				</div>

				<p className='text-center text-sm text-muted-foreground'>
					This download link expires in 24 hours.
				</p>
			</div>
		</StatusCard>
	)
}
