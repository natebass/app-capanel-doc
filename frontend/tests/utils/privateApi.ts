// Note: the `PrivateService` is only available when generating the client
// for local environments
import { PrivateService } from '../../src/lib/client'
import { client } from '../../src/lib/client/client.gen'

client.setConfig({ baseUrl: `${process.env.VITE_API_URL}` })

export const createUser = async ({ email, password }: { email: string; password: string }) => {
	const response = await PrivateService.privateCreateUser({
		body: {
			email,
			password,
			is_verified: true,
			full_name: 'Test User',
		},
	})
	if (response.error || !response.data) {
		throw response.error ?? new Error('Failed to create test user')
	}
	return response.data
}
