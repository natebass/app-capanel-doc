import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'

import { PasswordInput } from '@/components/password-input'
import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Spinner } from '@/components/ui/spinner'
import { type UpdatePassword, UsersService } from '@/lib/client'
import { handleError } from '@/lib/client-utils.ts'
import useCustomToast from '@/routes/-hooks/hooks/useCustomToast.ts'

const formSchema = z
	.object({
		currentPassword: z
			.string()
			.min(1, { error: 'Password is required' })
			.min(8, { error: 'Password must be at least 8 characters' }),
		newPassword: z
			.string()
			.min(1, { error: 'Password is required' })
			.min(8, { error: 'Password must be at least 8 characters' }),
		confirm_password: z.string().min(1, { error: 'Password confirmation is required' }),
	})
	.refine((data) => data.newPassword === data.confirm_password, {
		error: "The passwords don't match",
		path: ['confirm_password'],
	})

type FormData = z.infer<typeof formSchema>

const ChangePassword = () => {
	const { showSuccessToast, showErrorToast } = useCustomToast()
	const queryClient = useQueryClient()

	const form = useForm({
		defaultValues: {
			currentPassword: '',
			newPassword: '',
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
			void queryClient.invalidateQueries({ queryKey: ['currentUser'] })
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
					void form.handleSubmit()
				}}
				className='flex flex-col gap-4'
			>
				<form.Field name='currentPassword'>
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

				<form.Field name='newPassword'>
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
