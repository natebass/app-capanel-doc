import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { UsersService, type UserUpdateMe } from '@/lib/client'
import { handleError } from '@/lib/client-utils.ts'
import useAuth from '@/lib/hooks/useAuth.ts'
import useCustomToast from '@/lib/hooks/useCustomToast.ts'
import { cn } from '@/lib/utils.ts'

const formSchema = z.object({
	full_name: z.string().max(30).optional(),
	email: z.string().email({ message: 'Invalid email address' }),
})

type FormData = z.infer<typeof formSchema>

const UserInformation = () => {
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()
	const [editMode, setEditMode] = useState(false)
	const { user: currentUser } = useAuth()

	const form = useForm({
		defaultValues: {
			full_name: currentUser?.full_name ?? '',
			email: currentUser?.email ?? '',
		} as FormData,
		validators: {
			onChange: formSchema,
		},
		onSubmit: async ({ value }) => {
			const updateData: UserUpdateMe = {}

			if (value.full_name !== currentUser?.full_name) {
				updateData.full_name = value.full_name
			}
			if (value.email !== currentUser?.email) {
				updateData.email = value.email
			}

			mutation.mutate(updateData)
		},
	})

	const toggleEditMode = () => {
		setEditMode(!editMode)
	}

	const mutation = useMutation({
		mutationFn: (data: UserUpdateMe) => UsersService.usersUpdateUserMe({ body: data }),
		onSuccess: () => {
			showSuccessToast('User updated successfully')
			toggleEditMode()
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			queryClient.invalidateQueries({ queryKey: ['currentUser'] })
		},
	})

	const onCancel = () => {
		form.reset()
		toggleEditMode()
	}

	return (
		<div className='max-w-md'>
			<h3 className='text-lg font-semibold py-4'>User Information</h3>
			<form
				onSubmit={(e) => {
					e.preventDefault()
					e.stopPropagation()
					form.handleSubmit()
				}}
				className='flex flex-col gap-4'
			>
				<form.Field name='full_name'>
					{(field) =>
						editMode ? (
							<Field>
								<FieldLabel htmlFor={field.name}>Full name</FieldLabel>
								<Input
									id={field.name}
									name={field.name}
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
						) : (
							<Field>
								<FieldLabel>Full name</FieldLabel>
								<p
									className={cn(
										'py-2 truncate max-w-sm',
										!field.state.value && 'text-muted-foreground',
									)}
								>
									{field.state.value || 'N/A'}
								</p>
							</Field>
						)
					}
				</form.Field>

				<form.Field name='email'>
					{(field) =>
						editMode ? (
							<Field>
								<FieldLabel htmlFor={field.name}>Email</FieldLabel>
								<Input
									id={field.name}
									name={field.name}
									type='email'
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
						) : (
							<Field>
								<FieldLabel>Email</FieldLabel>
								<p className='py-2 truncate max-w-sm'>{field.state.value}</p>
							</Field>
						)
					}
				</form.Field>

				<div className='flex gap-3'>
					{editMode ? (
						<>
							<form.Subscribe
								selector={(state) => [state.canSubmit, state.isSubmitting, state.isDirty]}
							>
								{([canSubmit, isSubmitting, isDirty]) => (
									<Button type='submit' disabled={!canSubmit || !isDirty || mutation.isPending}>
										{(isSubmitting || mutation.isPending) && <Spinner className='mr-2' />}
										Save
									</Button>
								)}
							</form.Subscribe>
							<Button
								type='button'
								variant='outline'
								onClick={onCancel}
								disabled={mutation.isPending}
							>
								Cancel
							</Button>
						</>
					) : (
						<Button type='button' onClick={toggleEditMode}>
							Edit
						</Button>
					)}
				</div>
			</form>
		</div>
	)
}

export default UserInformation
