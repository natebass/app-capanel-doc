import { useForm } from '@tanstack/react-form'
import { createFileRoute, Link as RouterLink, redirect } from '@tanstack/react-router'
import { z } from 'zod'

import { AuthLayout } from '@/components/common/AuthLayout'
import { PasswordInput } from '@/components/password-input'
import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import useAuth, { isLoggedIn } from '@/lib/hooks/useAuth'

const signupSchema = z
	.object({
		email: z.string().email({ message: 'Please enter a valid email address' }),
		full_name: z.string().min(1, { message: 'Full Name is required' }),
		password: z
			.string()
			.min(1, { message: 'Password is required' })
			.min(8, { message: 'Password must be at least 8 characters' }),
		confirm_password: z.string().min(1, { message: 'Password confirmation is required' }),
	})
	.refine((data) => data.password === data.confirm_password, {
		message: "The passwords don't match",
		path: ['confirm_password'],
	})

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
			full_name: '',
			password: '',
			confirm_password: '',
		} as SignupFormValues,
		validators: {
			onChange: signupSchema,
		},
		onSubmit: async ({ value }) => {
			if (signUpMutation.isPending) return
			const { confirm_password: _, ...submitData } = value
			signUpMutation.mutate(submitData)
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
					<h1 className='text-2xl font-bold'>Create an account</h1>
				</div>

				<div className='grid gap-4'>
					<form.Field name='full_name'>
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

export default SignUp
