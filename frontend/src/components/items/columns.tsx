import { Copy01Icon, Tick02Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import type { ColumnDef } from '@tanstack/react-table'

import { Button } from '@/components/ui/button'
import type { ItemPublic } from '@/lib/client'
import { cn } from '@/lib/utils'
import { useCopyToClipboard } from '@/routes/-hooks/hooks/useCopyToClipboard'

import { ItemActionsMenu } from './ItemActionsMenu'

function CopyId({ id }: { id: string }) {
	const [copiedText, copy] = useCopyToClipboard()
	const isCopied = copiedText === id

	return (
		<div className='flex items-center gap-1.5 group'>
			<span className='font-mono text-xs text-muted-foreground'>{id}</span>
			<Button
				variant='ghost'
				size='icon'
				className='size-6 opacity-0 group-hover:opacity-100 transition-opacity'
				onClick={() => copy(id)}
			>
				{isCopied ? (
					<HugeiconsIcon icon={Tick02Icon} className='size-3 text-green-500' />
				) : (
					<HugeiconsIcon icon={Copy01Icon} className='size-3' />
				)}
				<span className='sr-only'>Copy ID</span>
			</Button>
		</div>
	)
}

interface CreateItemColumnsOptions {
	currentUserId?: string
	isSuperuser?: boolean
}

export function createItemColumns({
	currentUserId,
	isSuperuser = false,
}: CreateItemColumnsOptions): ColumnDef<ItemPublic>[] {
	const baseColumns: ColumnDef<ItemPublic>[] = [
		{
			accessorKey: 'id',
			header: 'ID',
			cell: ({ row }) => <CopyId id={row.original.id} />,
		},
		{
			accessorKey: 'title',
			header: 'Title',
			cell: ({ row }) => <span className='font-medium'>{row.original.title}</span>,
		},
		{
			accessorKey: 'description',
			header: 'Description',
			cell: ({ row }) => {
				const description = row.original.description
				return (
					<span
						className={cn(
							'max-w-xs truncate block text-muted-foreground',
							!description && 'italic',
						)}
					>
						{description || 'No description'}
					</span>
				)
			},
		},
	]

	if (isSuperuser) {
		baseColumns.push({
			accessorKey: 'owner_id',
			header: 'Owner',
			cell: ({ row }) => (
				<span className='font-mono text-xs text-muted-foreground'>
					{row.original.owner_id === currentUserId ? 'You' : row.original.owner_id}
				</span>
			),
		})
	}

	baseColumns.push({
		id: 'actions',
		header: () => <span className='sr-only'>Actions</span>,
		cell: ({ row }) => {
			const canManage = isSuperuser || row.original.owner_id === currentUserId
			return (
				<div className='flex justify-end'>
					<ItemActionsMenu item={row.original} canManage={canManage} />
				</div>
			)
		},
	})

	return baseColumns
}
