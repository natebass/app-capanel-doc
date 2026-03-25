import { MoreVerticalIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { useState } from 'react'

import DeleteItem from '@/components/items/DeleteItem'
import EditItem from '@/components/items/EditItem'
import { Button } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import type { ItemPublic } from '@/lib/client'

interface ItemActionsMenuProps {
	item: ItemPublic
	canManage: boolean
}

export const ItemActionsMenu = ({ item, canManage }: ItemActionsMenuProps) => {
	const [open, setOpen] = useState(false)

	if (!canManage) {
		return null
	}

	return (
		<DropdownMenu open={open} onOpenChange={setOpen}>
			<DropdownMenuTrigger render={<Button variant='ghost' size='icon' />}>
				<HugeiconsIcon icon={MoreVerticalIcon} />
			</DropdownMenuTrigger>
			<DropdownMenuContent align='end'>
				<EditItem item={item} onSuccess={() => setOpen(false)} />
				<DeleteItem id={item.id} onSuccess={() => setOpen(false)} />
			</DropdownMenuContent>
		</DropdownMenu>
	)
}
