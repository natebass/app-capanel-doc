import { PlusSignIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
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
	DialogTrigger,
} from '@/components/ui/dialog'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { type ItemCreate, ItemsService } from '@/lib/client'
import { handleError } from '@/lib/client-utils'
import useCustomToast from '@/routes/-hooks/hooks/useCustomToast'

const formSchema = z.object({
	title: z.string().min(1, { message: 'Title is required' }),
	description: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

const AddItem = () => {
	const [isOpen, setIsOpen] = useState(false)
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()

	const form = useForm({
		defaultValues: {
			title: '',
			description: '',
		} as FormData,
		validators: {
			onChange: formSchema,
		},
		onSubmit: async ({ value }) => {
			mutation.mutate(value as ItemCreate)
		},
	})

	const mutation = useMutation({
		mutationFn: (data: ItemCreate) => ItemsService.itemsCreateItem({ body: data }),
		onSuccess: () => {
			showSuccessToast('Item created successfully')
			form.reset()
			setIsOpen(false)
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			void queryClient.invalidateQueries({ queryKey: ['items'] })
		},
	})

	return (
		<Dialog open={isOpen} onOpenChange={setIsOpen}>
			<DialogTrigger render={<Button className='my-4' />}>
				<HugeiconsIcon icon={PlusSignIcon} className='mr-2' />
				Add Item
			</DialogTrigger>
			<DialogContent className='sm:max-w-md'>
				<DialogHeader>
					<DialogTitle>Add Item</DialogTitle>
					<DialogDescription>Fill in the details to add a new item.</DialogDescription>
				</DialogHeader>
				<form
					onSubmit={(e) => {
						e.preventDefault()
						e.stopPropagation()
						void form.handleSubmit()
					}}
				>
					<div className='grid gap-4 py-4'>
						<form.Field name='title'>
							{(field) => (
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
						</form.Field>

						<form.Field name='description'>
							{(field) => (
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
						</form.Field>
					</div>

					<DialogFooter>
						<DialogClose render={<Button variant='outline' disabled={mutation.isPending} />}>
							Cancel
						</DialogClose>
						<form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
							{([canSubmit, isSubmitting]) => (
								<Button type='submit' disabled={!canSubmit || mutation.isPending}>
									{(isSubmitting || mutation.isPending) && <Spinner className='mr-2' />}
									Save
								</Button>
							)}
						</form.Subscribe>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	)
}

export default AddItem
