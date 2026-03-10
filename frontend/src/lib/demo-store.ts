import { Store } from '@tanstack/store'

export type UserRole = 'owner' | 'admin' | 'member'

export type DemoStoreState = {
	firstName: string
	lastName: string
	email: string
	role: UserRole
	isOnline: boolean
	lastSeenAt: string
}

const nowIso = () => new Date().toISOString()

export const store = new Store<DemoStoreState>({
	firstName: 'Jane',
	lastName: 'Smith',
	email: 'jane.smith@example.com',
	role: 'admin',
	isOnline: true,
	lastSeenAt: nowIso(),
})

export const demoStoreActions = {
	setName(firstName: string, lastName: string) {
		store.setState((state) => ({
			...state,
			firstName,
			lastName,
		}))
	},
	setEmail(email: string) {
		store.setState((state) => ({
			...state,
			email,
		}))
	},
	setRole(role: UserRole) {
		store.setState((state) => ({
			...state,
			role,
		}))
	},
	setOnlineStatus(isOnline: boolean) {
		store.setState((state) => ({
			...state,
			isOnline,
			lastSeenAt: nowIso(),
		}))
	},
	touch() {
		store.setState((state) => ({
			...state,
			lastSeenAt: nowIso(),
		}))
	},
	reset() {
		store.setState(() => ({
			firstName: 'Jane',
			lastName: 'Smith',
			email: 'jane.smith@example.com',
			role: 'admin',
			isOnline: true,
			lastSeenAt: nowIso(),
		}))
	},
}
