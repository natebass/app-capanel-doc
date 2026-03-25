import { FileRemoveIcon, Home01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/unsupported-media')({
	component: UnsupportedMediaPage,
	head: () => ({
		meta: [{ title: '415 - Unsupported Media Type' }],
	}),
})

function UnsupportedMediaPage() {
	return (
		<StatusCard
			variant='error'
			icon={
				<div className='rounded-full bg-destructive/10 p-6'>
					<HugeiconsIcon icon={FileRemoveIcon} className='size-16 text-destructive' />
				</div>
			}
			title='415 - Unsupported Media Type'
			description='The file format is not supported.'
			footer={
				<>
					<Button render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
					<Button variant='outline' onClick={() => window.history.back()}>
						Go Back
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<p className='text-center text-sm text-muted-foreground'>Supported file formats:</p>

				<div className='flex flex-wrap justify-center gap-2'>
					<Badge variant='outline'>JSON</Badge>
					<Badge variant='outline'>XML</Badge>
					<Badge variant='outline'>CSV</Badge>
					<Badge variant='outline'>PNG</Badge>
					<Badge variant='outline'>JPG</Badge>
					<Badge variant='outline'>PDF</Badge>
				</div>

				<Separator />

				<p className='text-center text-sm text-muted-foreground'>
					Please convert your file to a supported format and try again.
				</p>
			</div>
		</StatusCard>
	)
}
