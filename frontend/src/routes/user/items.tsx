import { Search01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { useSuspenseQuery } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import { Suspense, useMemo } from 'react'

import { DataTable } from '@/components/common/DataTable'
import PendingItems from '@/components/common/pending/PendingItems'
import AddItem from '@/components/items/AddItem'
import { createItemColumns } from '@/components/items/columns'
import { ItemsService } from '@/lib/client'
import useAuth from '@/routes/-hooks/hooks/useAuth'

function getItemsQueryOptions() {
	return {
		queryFn: async () => {
			const response = await ItemsService.itemsReadItems({ query: { skip: 0, limit: 100 } })
			if (response.error || !response.data) {
				throw response.error ?? new Error('Failed to fetch items')
			}
			return response.data
		},
		queryKey: ['items'],
	}
}

export const Route = createFileRoute('/user/items')({
	component: Items,
	head: () => ({
		meta: [
			{
				title: 'items - FastAPI Cloud',
			},
		],
	}),
})

function ItemsTableContent() {
	const { user: currentUser } = useAuth()
	const { data: items } = useSuspenseQuery(getItemsQueryOptions())
	const columns = useMemo(
		() =>
			createItemColumns({
				currentUserId: currentUser?.id,
				isSuperuser: currentUser?.isSuperuser,
			}),
		[currentUser?.id, currentUser?.isSuperuser],
	)

	if (items.data.length === 0) {
		return (
			<div className='flex flex-col items-center justify-center text-center py-12'>
				<div className='rounded-full bg-muted p-4 mb-4'>
					<HugeiconsIcon icon={Search01Icon} className='h-8 w-8 text-muted-foreground' />
				</div>
				<h3 className='text-lg font-semibold'>
					{currentUser?.isSuperuser ? "There aren't any items yet" : "You don't have any items yet"}
				</h3>
				<p className='text-muted-foreground'>
					{currentUser?.isSuperuser
						? 'Create one or wait for users to add their items'
						: 'Add a new item to get started'}
				</p>
			</div>
		)
	}

	return <DataTable columns={columns} data={items.data} />
}

function ItemsTable() {
	return (
		<Suspense fallback={<PendingItems />}>
			<ItemsTableContent />
		</Suspense>
	)
}

function Items() {
	return (
		<div className='flex flex-col gap-6'>
			<div className='flex items-center justify-between'>
				<div>
					<h1 className='text-2xl font-bold tracking-tight'>Items</h1>
					<p className='text-muted-foreground'>Create and manage your items</p>
				</div>
				<AddItem />
			</div>
			<ItemsTable />
		</div>
	)
}
