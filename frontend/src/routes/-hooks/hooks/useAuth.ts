import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import {
	type BodyLoginLoginAccessToken as AccessToken,
	LoginService,
	type UserPublic,
	type UserRegister,
	UsersService,
} from '@/lib/client'
import { handleError } from '@/lib/client-utils.ts'

import useCustomToast from './useCustomToast'

const isLoggedIn = () => {
	// Check if we are in a browser environment. Can be removed if we enable server side rendering.
	if (typeof window === 'undefined') return false
	return localStorage.getItem('access_token') !== null
}

const useAuth = () => {
	const navigate = useNavigate()
	const queryClient = useQueryClient()
	const { showErrorToast } = useCustomToast()

	const { data: user } = useQuery<UserPublic | null, Error>({
		queryKey: ['currentUser'],
		queryFn: async () => {
			const response = await UsersService.usersReadUserMe({})
			return response.data ?? null
		},
		enabled: isLoggedIn(),
	})

	const signUpMutation = useMutation({
		mutationFn: (data: UserRegister) => UsersService.usersRegisterUser({ body: data }),
		onSuccess: () => {
			void navigate({ to: '/login' })
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			void queryClient.invalidateQueries({ queryKey: ['users'] })
		},
	})

	const login = async (data: AccessToken) => {
		const response = await LoginService.loginLoginAccessToken({
			body: data,
		})
		if (response.error || !response.data) {
			throw response.error ?? new Error('Login failed')
		}
		localStorage.setItem('access_token', response.data.access_token)
	}

	const loginMutation = useMutation({
		mutationFn: login,
		onSuccess: async () => {
			void queryClient.invalidateQueries({ queryKey: ['currentUser'] })
			void navigate({ to: '/' })
		},
		onError: handleError.bind(showErrorToast),
	})

	const logout = () => {
		localStorage.removeItem('access_token')
		void navigate({ to: '/login' })
	}

	return {
		signUpMutation,
		loginMutation,
		logout,
		user,
	}
}

export { isLoggedIn }
export default useAuth
