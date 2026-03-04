import { Link as RouterLink } from '@tanstack/react-router'
import { ChevronsUpDown, LogOut, Settings } from 'lucide-react'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	useSidebar,
} from '@/components/ui/sidebar'
import { getInitials } from '@/lib/client-utils.ts'
import useAuth from '@/lib/hooks/useAuth.ts'

interface UserInfoProps {
	fullName?: string
	email?: string
}

function UserInfo({ fullName, email }: UserInfoProps) {
	return (
		<div className='flex items-center gap-2.5 w-full min-w-0'>
			<Avatar className='size-8'>
				<AvatarFallback className='bg-zinc-600 text-white'>
					{getInitials(fullName || 'User')}
				</AvatarFallback>
			</Avatar>
			<div className='flex flex-col items-start min-w-0'>
				<p className='text-sm font-medium truncate w-full'>{fullName}</p>
				<p className='text-xs text-muted-foreground truncate w-full'>{email}</p>
			</div>
		</div>
	)
}

export function User({ user }: { user: any }) {
	const { logout } = useAuth()
	const { isMobile, setOpenMobile } = useSidebar()

	if (!user) return null

	const handleMenuClick = () => {
		if (isMobile) {
			setOpenMobile(false)
		}
	}
	const handleLogout = async () => {
		logout()
	}

	return (
		<SidebarMenu>
			<SidebarMenuItem>
				<DropdownMenu>
					<DropdownMenuTrigger
						render={
							<SidebarMenuButton
								size='lg'
								data-testid='user-menu'
								className='data-[state=open]:bg-sidebar-accent'
							/>
						}
					>
						<UserInfo fullName={user?.full_name} email={user?.email} />
						<ChevronsUpDown className='ml-auto size-4 text-muted-foreground' />
					</DropdownMenuTrigger>

					<DropdownMenuContent
						className='min-w-56 rounded-lg'
						// Base UI uses 'position' and 'alignment' or 'side'
						// Note: Base UI uses sideOffset via the 'offset' prop
						side={isMobile ? 'bottom' : 'right'}
						align='end'
						sideOffset={4}
					>
						<DropdownMenuLabel className='p-0 font-normal'>
							<UserInfo fullName={user?.full_name} email={user?.email} />
						</DropdownMenuLabel>

						<DropdownMenuSeparator />

						{/* Use 'render' prop for routing components in Base UI to avoid nesting issues */}
						<DropdownMenuItem render={<RouterLink to='/user/settings' />} onClick={handleMenuClick}>
							<Settings />
							User Settings
						</DropdownMenuItem>

						<DropdownMenuItem onClick={handleLogout}>
							<LogOut />
							Log Out
						</DropdownMenuItem>
					</DropdownMenuContent>
				</DropdownMenu>
			</SidebarMenuItem>
		</SidebarMenu>
	)
}
