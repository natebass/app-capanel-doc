import { useSuspenseQuery } from '@tanstack/react-query'
import { createFileRoute, redirect } from '@tanstack/react-router'
import { Suspense } from 'react'

import { columns, type UserTableData } from '@/components/admin/columns'
import { DataTable } from '@/components/common/DataTable'
import PendingUsers from '@/components/common/pending/PendingUsers'
import AddUser from '@/components/form/AddUser'
import { type UserPublic, UsersService, usersReadUsersOptions } from '@/lib/client'
import useAuth from '@/routes/-hooks/hooks/useAuth'

export const Route = createFileRoute('/user/admin')({
	component: Admin,
	beforeLoad: async () => {
		const response = await UsersService.usersReadUserMe({})
		if (!response.data?.isSuperuser) {
			throw redirect({
				to: '/',
			})
		}
	},
	head: () => ({
		meta: [
			{
				title: 'admin - FastAPI Cloud',
			},
		],
	}),
})

function UsersTableContent() {
	const { user: currentUser } = useAuth()
	const { data: users } = useSuspenseQuery(
		usersReadUsersOptions({ query: { skip: 0, limit: 100 } }),
	)

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
