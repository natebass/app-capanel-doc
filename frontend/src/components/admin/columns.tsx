import type { ColumnDef } from '@tanstack/react-table'

import { Badge } from '@/components/ui/badge'
import type { UserPublic } from '@/lib/client'
import { cn } from '@/lib/utils'

import { UserActionsMenu } from './UserActionsMenu'

export type UserTableData = UserPublic & {
	isCurrentUser: boolean
}

export const columns: ColumnDef<UserTableData>[] = [
	{
		accessorKey: 'fullName',
		header: 'Full Name',
		cell: ({ row }) => {
			const fullName = row.original.fullName
			return (
				<div className='flex items-center gap-2'>
					<span className={cn('font-medium', !fullName && 'text-muted-foreground')}>
						{fullName || 'N/A'}
					</span>
					{row.original.isCurrentUser && (
						<Badge variant='outline' className='text-xs'>
							You
						</Badge>
					)}
				</div>
			)
		},
	},
	{
		accessorKey: 'email',
		header: 'Email',
		cell: ({ row }) => <span className='text-muted-foreground'>{row.original.email}</span>,
	},
	{
		accessorKey: 'isSuperuser',
		header: 'Role',
		cell: ({ row }) => (
			<Badge variant={row.original.isSuperuser ? 'default' : 'secondary'}>
				{row.original.isSuperuser ? 'Superuser' : 'User'}
			</Badge>
		),
	},
	{
		accessorKey: 'isActive',
		header: 'Status',
		cell: ({ row }) => (
			<div className='flex items-center gap-2'>
				<span
					className={cn(
						'size-2 rounded-full',
						row.original.isActive ? 'bg-green-500' : 'bg-gray-400',
					)}
				/>
				<span className={row.original.isActive ? '' : 'text-muted-foreground'}>
					{row.original.isActive ? 'Active' : 'Inactive'}
				</span>
			</div>
		),
	},
	{
		accessorKey: 'forcePasswordReset',
		header: 'Security',
		cell: ({ row }) =>
			row.original.forcePasswordReset ? (
				<Badge variant='destructive'>Reset Required</Badge>
			) : (
				<span className='text-muted-foreground text-sm'>Normal</span>
			),
	},
	{
		id: 'actions',
		header: () => <span className='sr-only'>Actions</span>,
		cell: ({ row }) => (
			<div className='flex justify-end'>
				<UserActionsMenu user={row.original} />
			</div>
		),
	},
]
