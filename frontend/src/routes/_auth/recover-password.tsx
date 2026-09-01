import { useForm } from '@tanstack/react-form'
import { useMutation } from '@tanstack/react-query'
import { createFileRoute, Link as RouterLink, redirect } from '@tanstack/react-router'
import { z } from 'zod'

import { AuthLayout } from '@/components/common/AuthLayout'
import { Button } from '@/components/ui/button'
import { Field, FieldError, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { loginRecoverPasswordMutation } from '@/lib/client'
import { handleError } from '@/lib/client-utils'
import { email } from '@/lib/forms'
import { isLoggedIn } from '@/routes/-hooks/hooks/useAuth'
import useCustomToast from '@/routes/-hooks/hooks/useCustomToast'

const recoverSchema = z.object({ email })

type RecoverFormValues = z.infer<typeof recoverSchema>

export const Route = createFileRoute('/_auth/recover-password')({
	component: RecoverPassword,
	beforeLoad: async () => {
		if (isLoggedIn()) {
			throw redirect({ to: '/' })
		}
	},
	head: () => ({
		meta: [{ title: 'Recover Password - FastAPI Cloud' }],
	}),
})

function RecoverPassword() {
	const { showSuccessToast, showErrorToast } = useCustomToast()

	const form = useForm({
		defaultValues: {
			email: '',
		} as RecoverFormValues,
		validators: {
			onChange: recoverSchema,
		},
		onSubmit: async ({ value }) => {
			if (mutation.isPending) return
			mutation.mutate({ path: { email: value.email } })
		},
	})

	const mutation = useMutation({
		...loginRecoverPasswordMutation(),
		onSuccess: () => {
			showSuccessToast('Password recovery email sent successfully')
			form.reset()
		},
		onError: handleError.bind(showErrorToast),
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
					<h1 className='text-2xl font-bold'>Password Recovery</h1>
				</div>

				<div className='grid gap-4'>
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

					<form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
						{([canSubmit, isSubmitting]) => (
							<Button type='submit' className='w-full' disabled={!canSubmit || mutation.isPending}>
								{(isSubmitting || mutation.isPending) && <Spinner className='mr-2' />}
								Continue
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
