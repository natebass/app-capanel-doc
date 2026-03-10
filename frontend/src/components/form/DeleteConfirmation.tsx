import { useMutation, useQueryClient } from '@tanstack/react-query'

import { Button } from '@/components/ui/button.tsx'
import {
	Dialog,
	DialogClose,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from '@/components/ui/dialog.tsx'
import { Spinner } from '@/components/ui/spinner.tsx'
import { UsersService } from '@/lib/client'
import { handleError } from '@/lib/client-utils.ts'
import useAuth from '@/lib/hooks/useAuth.ts'
import useCustomToast from '@/lib/hooks/useCustomToast.ts'

const DeleteConfirmation = () => {
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()
	const { logout } = useAuth()

	const mutation = useMutation({
		mutationFn: () => UsersService.usersDeleteUserMe(),
		onSuccess: () => {
			showSuccessToast('Your account has been successfully deleted')
			logout()
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			queryClient.invalidateQueries({ queryKey: ['currentUser'] })
		},
	})

	const handleDelete = (e: React.FormEvent) => {
		e.preventDefault()
		mutation.mutate()
	}

	return (
		<Dialog>
			<DialogTrigger render={<Button variant='destructive' className='mt-3' />}>
				Delete Account
			</DialogTrigger>
			<DialogContent>
				<form onSubmit={handleDelete}>
					<DialogHeader>
						<DialogTitle>Confirmation Required</DialogTitle>
						<DialogDescription>
							All your account data will be <strong>permanently deleted.</strong> If you are sure,
							please click <strong>"Confirm"</strong> to proceed. This action cannot be undone.
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

export default DeleteConfirmation
