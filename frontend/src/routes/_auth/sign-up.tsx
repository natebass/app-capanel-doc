import { useForm } from '@tanstack/react-form'
import { createFileRoute, Link as RouterLink, redirect } from '@tanstack/react-router'
import { z } from 'zod'

import { AuthLayout } from '@/components/common/AuthLayout'
import { PasswordInput } from '@/components/password-input'
import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { zUserRegister } from '@/lib/client'
import { email, password, passwordConfirmation, passwordsMatch } from '@/lib/forms'
import useAuth, { isLoggedIn } from '@/routes/-hooks/hooks/useAuth'

const signupSchema = zUserRegister
	.extend({
		email,
		fullName: z.string().min(1, { error: 'Full Name is required' }).max(255),
		password,
		confirm_password: passwordConfirmation,
	})
	.refine((data) => data.password === data.confirm_password, passwordsMatch)

type SignupFormValues = z.infer<typeof signupSchema>

export const Route = createFileRoute('/_auth/sign-up')({
	component: SignUp,
	beforeLoad: async () => {
		if (isLoggedIn()) {
			throw redirect({ to: '/' })
		}
	},
	head: () => ({
		meta: [{ title: 'Sign Up - FastAPI Cloud' }],
	}),
})

function SignUp() {
	const { signUpMutation } = useAuth()

	const form = useForm({
		defaultValues: {
			email: '',
			fullName: '',
			password: '',
			confirm_password: '',
		} as SignupFormValues,
		validators: {
			onChange: signupSchema,
		},
		onSubmit: async ({ value }) => {
			if (signUpMutation.isPending) return
			const { confirm_password: _, ...submitData } = value
			signUpMutation.mutate({ body: submitData })
		},
	})

	return (
		<AuthLayout>
			<form
				onSubmit={(e) => {
					e.preventDefault()
					e.stopPropagation()
					void form.handleSubmit()
				}}
				className='flex flex-col gap-6'
			>
				<div className='flex flex-col items-center gap-2 text-center'>
					<h1 className='text-2xl font-bold'>Create an account</h1>
				</div>

				<div className='grid gap-4'>
					<form.Field name='fullName'>
						{(field) => (
							<Field>
								<FieldLabel htmlFor={field.name}>Full Name</FieldLabel>
								<Input
									id={field.name}
									name={field.name}
									data-testid='full-name-input'
									placeholder='User'
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

					<form.Field name='email'>
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
								<FieldLabel htmlFor={field.name}>Password</FieldLabel>
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
								className='w-full'
								disabled={!canSubmit || signUpMutation.isPending}
							>
								{(isSubmitting || signUpMutation.isPending) && <Spinner className='mr-2' />}
								Sign Up
							</Button>
						)}
					</form.Subscribe>
				</div>

				<div className='text-center text-sm'>
					Already have an account?{' '}
					<RouterLink to='/login' className='underline underline-offset-4'>
						Log in
					</RouterLink>
				</div>
			</form>
		</AuthLayout>
	)
}
