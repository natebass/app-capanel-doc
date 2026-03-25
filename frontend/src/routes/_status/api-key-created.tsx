import { AlertCircleIcon, Copy01Icon, Home01Icon, Key01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { StatusCard } from '@/components/layout/status/StatusTemplate'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/api-key-created')({
	component: ApiKeyCreatedPage,
	head: () => ({
		meta: [{ title: 'API Key Created' }],
	}),
})

function ApiKeyCreatedPage() {
	const apiKey = 'sk_live_abc123xyz789def456'

	return (
		<StatusCard
			variant='success'
			icon={
				<div className='rounded-full bg-green-500/10 p-6'>
					<HugeiconsIcon icon={Key01Icon} className='size-16 text-green-500' />
				</div>
			}
			title='API Key Created'
			description='Your new API key has been generated.'
			footer={
				<>
					<Button render={<Link to='/user/settings' />}>View API Keys</Button>
					<Button variant='outline' render={<Link to='/' />}>
						<HugeiconsIcon icon={Home01Icon} className='mr-2 size-4' />
						Go Home
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Alert variant='destructive'>
					<HugeiconsIcon icon={AlertCircleIcon} className='size-4' />
					<AlertTitle>Save This Key Now</AlertTitle>
					<AlertDescription>
						This is the only time you'll see this key. Copy it and store it securely.
					</AlertDescription>
				</Alert>

				<div className='relative'>
					<div className='rounded-lg border bg-muted p-3 font-mono text-xs break-all pr-10'>
						{apiKey}
					</div>
					<Button
						variant='ghost'
						size='icon-xs'
						className='absolute right-2 top-1/2 -translate-y-1/2'
						onClick={() => navigator.clipboard.writeText(apiKey)}
					>
						<HugeiconsIcon icon={Copy01Icon} className='size-3' />
					</Button>
				</div>

				<Separator />

				<p className='text-center text-sm text-muted-foreground'>
					Use this key in the Authorization header of your API requests.
				</p>
			</div>
		</StatusCard>
	)
}
