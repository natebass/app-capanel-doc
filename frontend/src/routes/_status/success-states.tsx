import { createFileRoute, Link } from '@tanstack/react-router'
import {
	Check,
	CheckCircle2,
	Crown,
	Database,
	FileDown,
	FileUp,
	Key,
	KeyRound,
	Mail,
	PartyPopper,
	Shield,
	Sparkles,
	Webhook,
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export const Route = createFileRoute('/_status/success-states')({
	component: SuccessStatesPage,
	head: () => ({
		meta: [{ title: 'Success States Demo' }],
	}),
})

const successPages = [
	{ name: 'General Success', icon: CheckCircle2, path: '/success', color: 'text-green-500' },
	{ name: 'Welcome', icon: Sparkles, path: '/welcome', color: 'text-green-500' },
	{
		name: 'Upgrade Success',
		icon: Crown,
		path: '/upgrade-success',
		color: 'text-green-500',
	},
	{
		name: 'Password Changed',
		icon: KeyRound,
		path: '/password-changed',
		color: 'text-green-500',
	},
	{ name: 'Email Sent', icon: Mail, path: '/email-sent', color: 'text-green-500' },
	{ name: '2FA Enabled', icon: Shield, path: '/2fa-enabled', color: 'text-green-500' },
	{
		name: 'Device Verified',
		icon: Check,
		path: '/device-verified',
		color: 'text-green-500',
	},
	{ name: 'Export Ready', icon: FileDown, path: '/export-ready', color: 'text-green-500' },
	{
		name: 'Import Complete',
		icon: FileUp,
		path: '/import-complete',
		color: 'text-green-500',
	},
	{
		name: 'Backup Complete',
		icon: Database,
		path: '/backup-complete',
		color: 'text-green-500',
	},
	{ name: 'API Key Created', icon: Key, path: '/api-key-created', color: 'text-green-500' },
	{
		name: 'Webhook Configured',
		icon: Webhook,
		path: '/webhook-configured',
		color: 'text-green-500',
	},
]

function SuccessStatesPage() {
	return (
		<div className='w-full max-w-4xl space-y-8'>
			<Card>
				<CardHeader className='text-center'>
					<div className='mx-auto mb-4'>
						<div className='rounded-full bg-green-500/10 p-4'>
							<PartyPopper className='size-12 text-green-500' />
						</div>
					</div>
					<CardTitle className='text-3xl'>Success States</CardTitle>
					<CardDescription className='text-base'>
						Confirmation and success pages for completed actions
					</CardDescription>
				</CardHeader>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle className='text-lg'>Success Pages</CardTitle>
					<CardDescription>Click to view each success state</CardDescription>
				</CardHeader>
				<CardContent>
					<div className='grid gap-2 sm:grid-cols-2 md:grid-cols-3'>
						{successPages.map((page) => {
							const Icon = page.icon
							return (
								<Link
									key={page.path}
									to={page.path}
									className='flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors'
								>
									<div className='rounded-full bg-green-500/10 p-2'>
										<Icon className={`size-4 ${page.color}`} />
									</div>
									<div className='font-medium text-sm'>{page.name}</div>
								</Link>
							)
						})}
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle className='text-lg'>Usage Patterns</CardTitle>
					<CardDescription>When to redirect to success pages</CardDescription>
				</CardHeader>
				<CardContent className='space-y-4'>
					<div className='rounded-lg bg-muted p-4 font-mono text-xs overflow-auto'>
						<pre>{`// After successful form submission
const handleSubmit = async (data) => {
  await api.createUser(data)
  navigate({ to: '/success' })
}

// After successful authentication action
const handlePasswordChange = async () => {
  await api.changePassword(newPassword)
  navigate({ to: '/password-changed' })
}

// After successful payment
const handleUpgrade = async () => {
  await api.upgradePlan('pro')
  navigate({ to: '/upgrade-success' })
}`}</pre>
					</div>
					<div className='flex flex-wrap gap-2'>
						<Badge variant='outline'>navigate()</Badge>
						<Badge variant='outline'>redirect()</Badge>
						<Badge variant='outline'>replace: true</Badge>
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle className='text-lg'>StatusCard Variants</CardTitle>
					<CardDescription>Visual styles for different contexts</CardDescription>
				</CardHeader>
				<CardContent>
					<div className='grid gap-4 md:grid-cols-2'>
						<div className='flex items-center gap-3 p-4 rounded-lg border-2 border-green-500/50'>
							<CheckCircle2 className='size-6 text-green-500' />
							<div>
								<div className='font-medium'>variant="success"</div>
								<div className='text-xs text-muted-foreground'>Green border accent</div>
							</div>
						</div>
						<div className='flex items-center gap-3 p-4 rounded-lg border-2 border-blue-500/50'>
							<Sparkles className='size-6 text-blue-500' />
							<div>
								<div className='font-medium'>variant="info"</div>
								<div className='text-xs text-muted-foreground'>Blue border accent</div>
							</div>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	)
}

export default SuccessStatesPage
