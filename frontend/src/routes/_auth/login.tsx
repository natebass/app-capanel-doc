import { useForm } from '@tanstack/react-form'
import { createFileRoute, Link as RouterLink, redirect } from '@tanstack/react-router'
import { z } from 'zod'

import { AuthLayout } from '@/components/common/AuthLayout'
import { PasswordInput } from '@/components/password-input'
import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import type { BodyLoginLoginAccessToken as AccessToken } from '@/lib/client'
import useAuth, { isLoggedIn } from '@/lib/hooks/useAuth'

const loginSchema = z.object({
	username: z.string().email({ message: 'Please enter a valid email' }),
	password: z
		.string()
		.min(1, { message: 'Password is required' })
		.min(8, { message: 'Password must be at least 8 characters' }),
}) satisfies z.ZodType<AccessToken>

type LoginFormValues = z.infer<typeof loginSchema>

export const Route = createFileRoute('/_auth/login')({
	component: Login,
	beforeLoad: async () => {
		if (isLoggedIn()) {
			throw redirect({ to: '/' })
		}
	},
	head: () => ({
		meta: [{ title: 'Log In - FastAPI Cloud' }],
	}),
})

function Login() {
	const { loginMutation } = useAuth()

	const form = useForm({
		defaultValues: {
			username: '',
			password: '',
		} as LoginFormValues,
		validators: {
			onChange: loginSchema,
		},
		onSubmit: async ({ value }) => {
			if (loginMutation.isPending) return
			loginMutation.mutate(value)
		},
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
					<h1 className='text-2xl font-bold'>Login to your account</h1>
				</div>

				<div className='grid gap-4'>
					<form.Field name='username'>
						{(field) => (
							<Field>
								<FieldLabel htmlFor={field.name}>Email</FieldLabel>
								<Input
									id={field.name}
									name={field.name}
									data-testid='email-input'
									placeholder='user@example.com'
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
						)}
					</form.Field>

					<form.Field name='password'>
						{(field) => (
							<Field>
								<div className='flex items-center'>
									<FieldLabel htmlFor={field.name}>Password</FieldLabel>
									<RouterLink
										to='/recover-password'
										className='ml-auto text-sm underline-offset-4 hover:underline'
									>
										Forgot your password?
									</RouterLink>
								</div>
								<PasswordInput
									id={field.name}
									name={field.name}
									data-testid='password-input'
									placeholder='Password'
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
								className='w-full'
								disabled={!canSubmit || loginMutation.isPending}
							>
								{(isSubmitting || loginMutation.isPending) && <Spinner className='mr-2' />}
								Log In
							</Button>
						)}
					</form.Subscribe>
				</div>

				<div className='text-center text-sm'>
					Don't have an account yet?{' '}
					<RouterLink to='/sign-up' className='underline underline-offset-4'>
						Sign up
					</RouterLink>
				</div>
			</form>
		</AuthLayout>
	)
}
