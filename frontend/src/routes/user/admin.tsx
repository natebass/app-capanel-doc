import { useSuspenseQuery } from '@tanstack/react-query'
import { createFileRoute, redirect } from '@tanstack/react-router'
import { Suspense } from 'react'

import AddUser from '@/components/Admin/AddUser'
import { columns, type UserTableData } from '@/components/Admin/columns'
import { DataTable } from '@/components/Common/DataTable'
import PendingUsers from '@/components/Pending/PendingUsers'
import { type UserPublic, UsersService } from '@/lib/client'
import useAuth from '@/lib/hooks/useAuth'

function getUsersQueryOptions() {
	return {
		queryFn: async () => {
			const response = await UsersService.usersReadUsers({ query: { skip: 0, limit: 100 } })
			if (response.error || !response.data) {
				throw response.error ?? new Error('Failed to fetch users')
			}
			return response.data
		},
		queryKey: ['users'],
	}
}

export const Route = createFileRoute('/user/admin')({
	component: Admin,
	beforeLoad: async () => {
		const response = await UsersService.usersReadUserMe({})
		if (!response.data?.is_superuser) {
			throw redirect({
				to: '/',
			})
		}
	},
	head: () => ({
		meta: [
			{
				title: 'Admin - FastAPI Cloud',
			},
		],
	}),
})

function UsersTableContent() {
	const { user: currentUser } = useAuth()
	const { data: users } = useSuspenseQuery(getUsersQueryOptions())

	const tableData: UserTableData[] = users.data.map((user: UserPublic) => ({
		...user,
		isCurrentUser: currentUser?.id === user.id,
	}))

	return <DataTable columns={columns} data={tableData} />
}

function UsersTable() {
	return (
		<Suspense fallback={<PendingUsers />}>
			<UsersTableContent />
		</Suspense>
	)
}

function Admin() {
	return (
		<div className='flex flex-col gap-6'>
			<div className='flex items-center justify-between'>
				<div>
					<h1 className='text-2xl font-bold tracking-tight'>Users</h1>
					<p className='text-muted-foreground'>Manage user accounts and permissions</p>
				</div>
				<AddUser />
			</div>
			<UsersTable />
		</div>
	)
}
