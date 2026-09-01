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
import { itemsDeleteItemMutation, itemsReadItemsQueryKey } from '@/lib/client'
import { handleError } from '@/lib/client-utils'
import useCustomToast from '@/routes/-hooks/hooks/useCustomToast'

interface DeleteItemProps {
	id: string
	onSuccess: () => void
}

const DeleteItem = ({ id, onSuccess }: DeleteItemProps) => {
	const [isOpen, setIsOpen] = useState(false)
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()

	const mutation = useMutation({
		...itemsDeleteItemMutation(),
		onSuccess: () => {
			showSuccessToast('The item was deleted successfully')
			setIsOpen(false)
			onSuccess()
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			void queryClient.invalidateQueries({ queryKey: itemsReadItemsQueryKey() })
		},
	})

	const handleDelete = (e: React.FormEvent) => {
		e.preventDefault()
		mutation.mutate({ path: { id } })
	}

	return (
		<Dialog open={isOpen} onOpenChange={setIsOpen}>
			<DropdownMenuItem
				variant='destructive'
				onSelect={(e) => e.preventDefault()}
				onClick={() => setIsOpen(true)}
			>
				<HugeiconsIcon icon={Delete02Icon} />
				Delete Item
			</DropdownMenuItem>
			<DialogContent className='sm:max-w-md'>
				<form onSubmit={handleDelete}>
					<DialogHeader>
						<DialogTitle>Delete Item</DialogTitle>
						<DialogDescription>
							This item will be permanently deleted. Are you sure? You will not be able to undo this
							action.
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

export default DeleteItem
