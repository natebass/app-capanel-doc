import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { useState } from 'react'
import { z } from 'zod'

import { Button } from '@/components/ui/button.tsx'
import { Checkbox } from '@/components/ui/checkbox.tsx'
import {
	Dialog,
	DialogClose,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from '@/components/ui/dialog.tsx'
import { Field, FieldError, FieldLabel } from '@/components/ui/field.tsx'
import { Input } from '@/components/ui/input.tsx'
import { PasswordInput } from '@/components/ui/password-input.tsx'
import { Spinner } from '@/components/ui/spinner.tsx'
import { type UserCreate, UsersService } from '@/lib/client'
import { handleError } from '@/lib/client-utils.ts'
import useCustomToast from '@/lib/hooks/useCustomToast.ts'

const formSchema = z
	.object({
		email: z.string().email({ message: 'Invalid email address' }),
		full_name: z.string().optional(),
		password: z
			.string()
			.min(1, { message: 'Password is required' })
			.min(8, { message: 'Password must be at least 8 characters' }),
		confirm_password: z.string().min(1, { message: 'Please confirm your password' }),
		is_superuser: z.boolean(),
		is_active: z.boolean(),
	})
	.refine((data) => data.password === data.confirm_password, {
		message: "The passwords don't match",
		path: ['confirm_password'],
	})

type FormData = z.infer<typeof formSchema>

const AddUser = () => {
	const [isOpen, setIsOpen] = useState(false)
	const queryClient = useQueryClient()
	const { showSuccessToast, showErrorToast } = useCustomToast()

	const form = useForm({
		defaultValues: {
			email: '',
			full_name: '',
			password: '',
			confirm_password: '',
			is_superuser: false,
			is_active: false,
		} as FormData,
		validators: {
			onChange: formSchema,
		},
		onSubmit: async ({ value }) => {
			const { confirm_password: _, ...submitData } = value
			mutation.mutate(submitData as UserCreate)
		},
	})

	const mutation = useMutation({
		mutationFn: (data: UserCreate) => UsersService.usersCreateUser({ body: data }),
		onSuccess: () => {
			showSuccessToast('User created successfully')
			form.reset()
			setIsOpen(false)
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			queryClient.invalidateQueries({ queryKey: ['users'] })
		},
	})

	return (
		<Dialog open={isOpen} onOpenChange={setIsOpen}>
			<DialogTrigger render={<Button className='my-4' />}>
				<Plus className='mr-2' />
				Add User
			</DialogTrigger>
			<DialogContent className='sm:max-w-md'>
				<DialogHeader>
					<DialogTitle>Add User</DialogTitle>
					<DialogDescription>
						Fill in the form below to add a new user to the system.
					</DialogDescription>
				</DialogHeader>
				<form
					onSubmit={(e) => {
						e.preventDefault()
						e.stopPropagation()
						form.handleSubmit()
					}}
				>
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
									<FieldLabel htmlFor={field.name}>
										Set Password <span className='text-destructive'>*</span>
									</FieldLabel>
									<PasswordInput
										id={field.name}
										name={field.name}
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
						/>

						<form.Field
							name='confirm_password'
							children={(field) => (
								<Field>
									<FieldLabel htmlFor={field.name}>
										Confirm Password <span className='text-destructive'>*</span>
									</FieldLabel>
									<PasswordInput
										id={field.name}
										name={field.name}
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

export default AddUser
