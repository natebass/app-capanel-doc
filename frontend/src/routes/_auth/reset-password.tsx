import { useForm } from '@tanstack/react-form'
import { useMutation } from '@tanstack/react-query'
import { createFileRoute, Link as RouterLink, redirect, useNavigate } from '@tanstack/react-router'
import { z } from 'zod'

import { AuthLayout } from '@/components/common/AuthLayout'
import { PasswordInput } from '@/components/password-input'
import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Spinner } from '@/components/ui/spinner'
import { LoginService } from '@/lib/client'
import { handleError } from '@/lib/client-utils'
import { isLoggedIn } from '@/lib/hooks/useAuth'
import useCustomToast from '@/lib/hooks/useCustomToast'

const searchSchema = z.object({
	token: z.coerce.string().catch(''),
})

const resetSchema = z
	.object({
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

type ResetFormValues = z.infer<typeof resetSchema>

export const Route = createFileRoute('/_auth/reset-password')({
	component: ResetPassword,
	validateSearch: searchSchema,
	beforeLoad: async ({ search }) => {
		if (isLoggedIn()) {
			throw redirect({ to: '/' })
		}
		if (!search.token) {
			throw redirect({ to: '/login' })
		}
	},
	head: () => ({
		meta: [{ title: 'Reset Password - FastAPI Cloud' }],
	}),
})

function ResetPassword() {
	const { token } = Route.useSearch()
	const { showSuccessToast, showErrorToast } = useCustomToast()
	const navigate = useNavigate()

	const form = useForm({
		defaultValues: {
			new_password: '',
			confirm_password: '',
		} as ResetFormValues,
		validators: {
			onChange: resetSchema,
		},
		onSubmit: async ({ value }) => {
			mutation.mutate({ new_password: value.new_password, token })
		},
	})

	const mutation = useMutation({
		mutationFn: (data: { new_password: string; token: string }) =>
			LoginService.loginResetPassword({ body: data }),
		onSuccess: () => {
			showSuccessToast('Password updated successfully')
			form.reset()
			navigate({ to: '/login' })
		},
		onError: handleError.bind(showErrorToast),
	})

	return (
		<AuthLayout>
			<form
				onSubmit={(e) => {
					e.preventDefault()
					e.stopPropagation()
					form.handleSubmit()
				}}
				className='flex flex-col gap-6'
			>
				<div className='flex flex-col items-center gap-2 text-center'>
					<h1 className='text-2xl font-bold'>Reset Password</h1>
				</div>

				<div className='grid gap-4'>
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
							<Button type='submit' className='w-full' disabled={!canSubmit || mutation.isPending}>
								{(isSubmitting || mutation.isPending) && <Spinner className='mr-2' />}
								Reset Password
							</Button>
						)}
					</form.Subscribe>
				</div>

				<div className='text-center text-sm'>
					Remember your password?{' '}
					<RouterLink to='/login' className='underline underline-offset-4'>
						Log in
					</RouterLink>
				</div>
			</form>
		</AuthLayout>
	)
}
