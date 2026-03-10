import { createFileRoute, Link } from '@tanstack/react-router'
import { Check, Home, Mail, Users, X } from 'lucide-react'

import { StatusCard } from '@/components/StatusTemplate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

export const Route = createFileRoute('/_status/invitation')({
	component: InvitationPage,
	head: () => ({
		meta: [{ title: 'Team Invitation' }],
	}),
})

function InvitationPage() {
	return (
		<StatusCard
			variant='info'
			icon={
				<div className='rounded-full bg-blue-500/10 p-6'>
					<Mail className='size-16 text-blue-500' />
				</div>
			}
			title="You're Invited!"
			description="You've been invited to join a team."
			footer={
				<>
					<Button>
						<Check className='mr-2 size-4' />
						Accept
					</Button>
					<Button variant='outline'>
						<X className='mr-2 size-4' />
						Decline
					</Button>
				</>
			}
		>
			<div className='space-y-4'>
				<Card size='sm'>
					<CardHeader className='pb-2'>
						<div className='flex items-center justify-between'>
							<CardTitle className='text-sm'>Acme Corp</CardTitle>
							<Badge variant='outline'>
								<Users className='mr-1 size-3' />
								Team
							</Badge>
						</div>
						<CardDescription className='text-xs'>12 members</CardDescription>
					</CardHeader>
					<CardContent className='text-xs text-muted-foreground'>
						Invited by: john@acme.com
					</CardContent>
				</Card>

				<Separator />

				<p className='text-center text-sm text-muted-foreground'>
					By accepting, you'll join this team and have access to their shared resources.
				</p>

				<div className='text-center'>
					<Button variant='ghost' size='sm' render={<Link to='/' />}>
						<Home className='mr-2 size-4' />
						Skip for now
					</Button>
				</div>
			</div>
		</StatusCard>
	)
}

export default InvitationPage
