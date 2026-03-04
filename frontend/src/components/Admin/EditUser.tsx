import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Pencil } from 'lucide-react'
import { useState } from 'react'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
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
import { PasswordInput } from '@/components/ui/password-input'
import { Spinner } from '@/components/ui/spinner'
import { type UserPublic, UsersService } from '@/lib/client'
import { handleError } from '@/lib/client-utils'
import useCustomToast from '@/lib/hooks/useCustomToast'

const formSchema = z
	.object({
		email: z.string().email({ message: 'Invalid email address' }),
		full_name: z.string().optional(),
		password: z
			.string()
			.min(8, { message: 'Password must be at least 8 characters' })
			.optional()
			.or(z.literal('')),
		confirm_password: z.string().optional(),
		is_superuser: z.boolean().optional(),
		is_active: z.boolean().optional(),
	})
	.refine((data) => !data.password || data.password === data.confirm_password, {
		message: "The passwords don't match",
		path: ['confirm_password'],
	})

type FormData = z.infer<typeof formSchema>

interface EditUserProps {
	user: UserPublic
	onSuccess: () => void
}

const EditUser = ({ user, onSuccess }: EditUserProps) => {
	const [isOpen, setIsOpen] = useState(false)
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()

	const form = useForm({
		defaultValues: {
			email: user.email,
			full_name: user.full_name ?? '',
			password: '',
			confirm_password: '',
			is_superuser: user.is_superuser,
			is_active: user.is_active,
		} as FormData,
		validators: {
			onChange: formSchema,
		},
		onSubmit: async ({ value }) => {
			const { confirm_password: _, password, ...rest } = value
			const submitData = password ? { ...rest, password } : rest
			mutation.mutate(submitData)
		},
	})

	const mutation = useMutation({
		mutationFn: (data: Partial<FormData>) =>
			UsersService.usersUpdateUser({ path: { user_id: user.id }, body: data }),
		onSuccess: () => {
			showSuccessToast('User updated successfully')
			setIsOpen(false)
			onSuccess()
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			queryClient.invalidateQueries({ queryKey: ['users'] })
		},
	})

	return (
		<Dialog open={isOpen} onOpenChange={setIsOpen}>
			<DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
				<Pencil />
				Edit User
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
						<DialogTitle>Edit User</DialogTitle>
						<DialogDescription>Update the user details below.</DialogDescription>
					</DialogHeader>
					<div className='grid gap-4 py-4'>
						<form.Field
							name='email'
							children={(field) => (
								<Field>
									<FieldLabel htmlFor={field.name}>
										Email <span className='text-destructive'>*</span>
									</FieldLabel>
									<Input
										id={field.name}
										name={field.name}
										placeholder='Email'
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
						/>

						<form.Field
							name='full_name'
							children={(field) => (
								<Field>
									<FieldLabel htmlFor={field.name}>Full Name</FieldLabel>
									<Input
										id={field.name}
										name={field.name}
										placeholder='Full name'
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

						<form.Field
							name='password'
							children={(field) => (
								<Field>
									<FieldLabel htmlFor={field.name}>Set Password</FieldLabel>
									<PasswordInput
										id={field.name}
										name={field.name}
										placeholder='Password'
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

						<form.Field
							name='confirm_password'
							children={(field) => (
								<Field>
									<FieldLabel htmlFor={field.name}>Confirm Password</FieldLabel>
									<PasswordInput
										id={field.name}
										name={field.name}
										placeholder='Password'
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

						<form.Field
							name='is_superuser'
							children={(field) => (
								<Field className='flex items-center gap-3'>
									<Checkbox
										id={field.name}
										checked={field.state.value}
										onCheckedChange={(checked) => field.handleChange(checked === true)}
									/>
									<FieldLabel htmlFor={field.name} className='font-normal'>
										Is superuser?
									</FieldLabel>
								</Field>
							)}
						/>

						<form.Field
							name='is_active'
							children={(field) => (
								<Field className='flex items-center gap-3'>
									<Checkbox
										id={field.name}
										checked={field.state.value}
										onCheckedChange={(checked) => field.handleChange(checked === true)}
									/>
									<FieldLabel htmlFor={field.name} className='font-normal'>
										Is active?
									</FieldLabel>
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

export default EditUser
