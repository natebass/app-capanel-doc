import { Delete02Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
	Dialog,
	DialogClose,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog'
import { DropdownMenuItem } from '@/components/ui/dropdown-menu'
import { Spinner } from '@/components/ui/spinner'
import { UsersService } from '@/lib/client'
import { handleError } from '@/lib/client-utils'
import useCustomToast from '@/routes/-hooks/hooks/useCustomToast'

interface DeleteUserProps {
	id: string
	onSuccess: () => void
}

const DeleteUser = ({ id, onSuccess }: DeleteUserProps) => {
	const [isOpen, setIsOpen] = useState(false)
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()

	const mutation = useMutation({
		mutationFn: () => UsersService.usersDeleteUser({ path: { user_id: id } }),
		onSuccess: () => {
			showSuccessToast('The user was deleted successfully')
			setIsOpen(false)
			onSuccess()
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			queryClient.invalidateQueries({ queryKey: ['users'] })
		},
	})

	const handleDelete = (e: React.FormEvent) => {
		e.preventDefault()
		mutation.mutate()
	}

	return (
		<Dialog open={isOpen} onOpenChange={setIsOpen}>
			<DropdownMenuItem
				variant='destructive'
				onSelect={(e) => e.preventDefault()}
				onClick={() => setIsOpen(true)}
			>
				<HugeiconsIcon icon={Delete02Icon} />
				Delete User
			</DropdownMenuItem>
			<DialogContent className='sm:max-w-md'>
				<form onSubmit={handleDelete}>
					<DialogHeader>
						<DialogTitle>Delete User</DialogTitle>
						<DialogDescription>
							All items associated with this user will also be <strong>permanently deleted.</strong>{' '}
							Are you sure? You will not be able to undo this action.
						</DialogDescription>
					</DialogHeader>

					<DialogFooter className='mt-4'>
						<DialogClose render={<Button variant='outline' disabled={mutation.isPending} />}>
							Cancel
						</DialogClose>
						<Button variant='destructive' type='submit' disabled={mutation.isPending}>
							{mutation.isPending && <Spinner className='mr-2' />}
							Delete
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	)
}

export default DeleteUser
