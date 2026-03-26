import {
	Ticket02Icon as Check,
	Database01Icon as Database,
	Download01Icon as Download,
	Home01Icon as Home,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/common/status/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/backup-complete')({
	component: BackupCompletePage,
	head: () => ({
		meta: [{ title: 'Backup Complete' }],
	}),
})

function BackupCompletePage() {
	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={Database} className='size-16 text-green-500' />
				</div>
			}
			title='Backup Complete'
			description='Your data has been backed up successfully.'
			footer={
				<>
					<Button>
						<HugeiconsIcon icon={Download} className='mr-2 size-4' />
						Download Backup
					</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<div className='flex items-center justify-center gap-2'>
					<Badge variant='default'>
						<HugeiconsIcon icon={Check} className='mr-1 size-3' />
						Verified
					</Badge>
				</div>

				<div className='rounded-lg border bg-muted/50 p-4 space-y-2 text-sm'>
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Backup ID</span>
						<span className='font-mono text-xs'>bkp_abc123xyz</span>
					</div>
					<Separator />
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Size</span>
						<span className='font-medium'>156 MB</span>
					</div>
					<Separator />
					<div className='flex items-center justify-between'>
						<span className='text-muted-foreground'>Created</span>
						<span className='font-medium'>{new Date().toLocaleString()}</span>
					</div>
				</div>

				<p className='text-center text-sm text-muted-foreground'>
					Backups are retained for 30 days.
				</p>
			</div>
		</StatusCard>
	)
}
