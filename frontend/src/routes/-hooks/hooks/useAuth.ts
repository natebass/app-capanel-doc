import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import {
	loginLoginAccessTokenMutation,
	usersReadUserMeOptions,
	usersReadUserMeQueryKey,
	usersReadUsersQueryKey,
	usersRegisterUserMutation,
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

	const { data: user } = useQuery({
		...usersReadUserMeOptions(),
		enabled: isLoggedIn(),
	})

	const signUpMutation = useMutation({
		...usersRegisterUserMutation(),
		onSuccess: () => {
			void navigate({ to: '/login' })
		},
		onError: handleError.bind(showErrorToast),
		onSettled: () => {
			void queryClient.invalidateQueries({ queryKey: usersReadUsersQueryKey() })
		},
	})

	const loginMutation = useMutation({
		...loginLoginAccessTokenMutation(),
		onSuccess: (token) => {
			localStorage.setItem('access_token', token.access_token)
			void queryClient.invalidateQueries({ queryKey: usersReadUserMeQueryKey() })
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
