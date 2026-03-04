import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Pencil } from 'lucide-react'
import { useState } from 'react'
import { z } from 'zod'

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
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { type ItemPublic, ItemsService } from '@/lib/client'
import { handleError } from '@/lib/client-utils'
import useCustomToast from '@/lib/hooks/useCustomToast'

const formSchema = z.object({
	title: z.string().min(1, { message: 'Title is required' }),
	description: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

interface EditItemProps {
	item: ItemPublic
	onSuccess: () => void
}

const EditItem = ({ item, onSuccess }: EditItemProps) => {
	const [isOpen, setIsOpen] = useState(false)
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()

	const form = useForm({
		defaultValues: {
			title: item.title,
			description: item.description ?? '',
		} as FormData,
		validators: {
			onChange: formSchema,
		},
		onSubmit: async ({ value }) => {
			mutation.mutate(value)
		},
	})

	const mutation = useMutation({
		mutationFn: (data: FormData) =>
			ItemsService.itemsUpdateItem({ path: { id: item.id }, body: data }),
		onSuccess: () => {
			showSuccessToast('Item updated successfully')
			setIsOpen(false)
			onSuccess()
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			queryClient.invalidateQueries({ queryKey: ['items'] })
		},
	})

	return (
		<Dialog open={isOpen} onOpenChange={setIsOpen}>
			<DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
				<Pencil />
				Edit Item
			</DropdownMenuItem>
			<DialogContent className='sm:max-w-md'>
				<form
					onSubmit={(e) => {
						e.preventDefault()
						e.stopPropagation()
						form.handleSubmit()
					}}
				>
					<DialogHeader>
						<DialogTitle>Edit Item</DialogTitle>
						<DialogDescription>Update the item details below.</DialogDescription>
					</DialogHeader>
					<div className='grid gap-4 py-4'>
						<form.Field
							name='title'
							children={(field) => (
								<Field>
									<FieldLabel htmlFor={field.name}>
										Title <span className='text-destructive'>*</span>
									</FieldLabel>
									<Input
										id={field.name}
										name={field.name}
										placeholder='Title'
										type='text'
										value={field.state.value}
										onBlur={field.handleBlur}
										onChange={(e) => field.handleChange(e.target.value)}
									/>
									{field.state.meta.isTouched && !field.state.meta.isValid && (
										<FieldError>
											{field.state.meta.errors.map((err) => err?.message ?? '').join(', ')}
										</FieldError>
									)}
								</Field>
							)}
						/>

						<form.Field
							name='description'
							children={(field) => (
								<Field>
									<FieldLabel htmlFor={field.name}>Description</FieldLabel>
									<Input
										id={field.name}
										name={field.name}
										placeholder='Description'
										type='text'
										value={field.state.value ?? ''}
										onBlur={field.handleBlur}
										onChange={(e) => field.handleChange(e.target.value)}
									/>
									{field.state.meta.isTouched && !field.state.meta.isValid && (
										<FieldError>
											{field.state.meta.errors.map((err) => err?.message ?? '').join(', ')}
										</FieldError>
									)}
								</Field>
							)}
						/>
					</div>

					<DialogFooter>
						<DialogClose render={<Button variant='outline' disabled={mutation.isPending} />}>
							Cancel
						</DialogClose>
						<form.Subscribe
							selector={(state) => [state.canSubmit, state.isSubmitting]}
							children={([canSubmit, isSubmitting]) => (
								<Button type='submit' disabled={!canSubmit || mutation.isPending}>
									{(isSubmitting || mutation.isPending) && <Spinner className='mr-2' />}
									Save
								</Button>
							)}
						/>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	)
}

export default EditItem
