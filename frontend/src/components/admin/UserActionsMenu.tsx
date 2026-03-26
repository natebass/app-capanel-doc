import { MoreVerticalIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import type { UserPublic } from '@/lib/client'
import useAuth from '@/routes/-hooks/hooks/useAuth'

import DeleteUser from './DeleteUser'
import EditUser from './EditUser'

interface UserActionsMenuProps {
	user: UserPublic
}

export const UserActionsMenu = ({ user }: UserActionsMenuProps) => {
	const [open, setOpen] = useState(false)
	const { user: currentUser } = useAuth()

	if (user.id === currentUser?.id) {
		return null
	}

	return (
		<DropdownMenu open={open} onOpenChange={setOpen}>
			<DropdownMenuTrigger render={<Button variant='ghost' size='icon' />}>
				<HugeiconsIcon icon={MoreVerticalIcon} />
			</DropdownMenuTrigger>
			<DropdownMenuContent align='end'>
				<EditUser user={user} onSuccess={() => setOpen(false)} />
				<DeleteUser id={user.id} onSuccess={() => setOpen(false)} />
			</DropdownMenuContent>
		</DropdownMenu>
	)
}
