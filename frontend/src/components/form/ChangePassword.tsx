import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'

import { PasswordInput } from '@/components/password-input'
import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Spinner } from '@/components/ui/spinner'
import { type UpdatePassword, UsersService } from '@/lib/client'
import { handleError } from '@/lib/client-utils.ts'
import useCustomToast from '@/lib/hooks/useCustomToast.ts'

const formSchema = z
	.object({
		current_password: z
			.string()
			.min(1, { message: 'Password is required' })
			.min(8, { message: 'Password must be at least 8 characters' }),
		new_password: z
			.string()
			.min(1, { message: 'Password is required' })
			.min(8, { message: 'Password must be at least 8 characters' }),
		confirm_password: z.string().min(1, { message: 'Password confirmation is required' }),
	})
	.refine((data) => data.new_password === data.confirm_password, {
		message: "The passwords don't match",
		path: ['confirm_password'],
	})

type FormData = z.infer<typeof formSchema>

const ChangePassword = () => {
	const { showSuccessToast, showErrorToast } = useCustomToast()
	const queryClient = useQueryClient()

	const form = useForm({
		defaultValues: {
			current_password: '',
			new_password: '',
			confirm_password: '',
		} as FormData,
		validators: {
			onChange: formSchema,
		},
		onSubmit: async ({ value }) => {
			const { confirm_password: _, ...submitData } = value
			mutation.mutate(submitData as UpdatePassword)
		},
	})

	const mutation = useMutation({
		mutationFn: (data: UpdatePassword) => UsersService.usersUpdatePasswordMe({ body: data }),
		onSuccess: () => {
			showSuccessToast('Password updated successfully')
			form.reset()
			queryClient.invalidateQueries({ queryKey: ['currentUser'] })
		},
		onError: handleError.bind(showErrorToast),
	})

	return (
		<div className='max-w-md'>
			<h3 className='text-lg font-semibold py-4'>Change Password</h3>
			<form
				onSubmit={(e) => {
					e.preventDefault()
					e.stopPropagation()
					form.handleSubmit()
				}}
				className='flex flex-col gap-4'
			>
				<form.Field name='current_password'>
					{(field) => (
						<Field>
							<FieldLabel htmlFor={field.name}>Current Password</FieldLabel>
							<PasswordInput
								id={field.name}
								name={field.name}
								data-testid='current-password-input'
								placeholder='Current Password'
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

				<form.Field name='new_password'>
					{(field) => (
						<Field>
							<FieldLabel htmlFor={field.name}>New Password</FieldLabel>
							<PasswordInput
								id={field.name}
								name={field.name}
								data-testid='new-password-input'
								placeholder='New Password'
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

				<form.Field name='confirm_password'>
					{(field) => (
						<Field>
							<FieldLabel htmlFor={field.name}>Confirm Password</FieldLabel>
							<PasswordInput
								id={field.name}
								name={field.name}
								data-testid='confirm-password-input'
								placeholder='Confirm Password'
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

				<form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
					{([canSubmit, isSubmitting]) => (
						<Button
							type='submit'
							className='self-start'
							disabled={!canSubmit || mutation.isPending}
						>
							{(isSubmitting || mutation.isPending) && <Spinner className='mr-2' />}
							Update Password
						</Button>
					)}
				</form.Subscribe>
			</form>
		</div>
	)
}

export default ChangePassword
