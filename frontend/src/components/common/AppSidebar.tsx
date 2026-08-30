import {
	Briefcase01Icon,
	Home01Icon,
	Logout01Icon,
	ScrollVerticalIcon,
	Settings03Icon,
	UserGroupIcon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { Link as RouterLink, useRouterState } from '@tanstack/react-router'

import { SidebarAppearance } from '@/components/common/Appearance'
import { Logo } from '@/components/common/Logo'
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
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarGroup,
	SidebarGroupContent,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	useSidebar,
} from '@/components/ui/sidebar'
import { getInitials } from '@/lib/client-utils.ts'
import useAuth from '@/routes/-hooks/hooks/useAuth.ts'

interface UserInfoProps {
	fullName?: string
	email?: string
}

export type Item = {
	icon: any
	title: string
	path: string
}

interface MainProps {
	items: Item[]
}

const baseItems: Item[] = [
	{ icon: Home01Icon, title: 'Dashboard', path: '/user/' },
	{ icon: Briefcase01Icon, title: 'Items', path: '/user/items' },
	{ icon: Settings03Icon, title: 'Settings', path: '/user/settings' },
]

export default function AppSidebar() {
	const { user: currentUser } = useAuth()

	const items = currentUser?.isSuperuser
		? [...baseItems, { icon: UserGroupIcon, title: 'Admin', path: '/user/admin' }]
		: baseItems

	return (
		<Sidebar collapsible='icon'>
			<SidebarHeader className='px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center'>
				<Logo variant='responsive' />
			</SidebarHeader>
			<SidebarContent>
				<Main items={items} />
			</SidebarContent>
			<SidebarFooter>
				<SidebarAppearance />
				<User user={currentUser} />
			</SidebarFooter>
		</Sidebar>
	)
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

function User({ user }: { user: any }) {
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
						<UserInfo fullName={user?.fullName} email={user?.email} />
						<HugeiconsIcon
							icon={ScrollVerticalIcon}
							className='ml-auto size-4 text-muted-foreground'
						/>
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
							<UserInfo fullName={user?.fullName} email={user?.email} />
						</DropdownMenuLabel>

						<DropdownMenuSeparator />

						{/* Use 'render' prop for routing components in Base UI to avoid nesting issues */}
						<DropdownMenuItem render={<RouterLink to='/user/settings' />} onClick={handleMenuClick}>
							<HugeiconsIcon icon={Settings03Icon} />
							User Settings
						</DropdownMenuItem>

						<DropdownMenuItem onClick={handleLogout}>
							<HugeiconsIcon icon={Logout01Icon} />
							Log Out
						</DropdownMenuItem>
					</DropdownMenuContent>
				</DropdownMenu>
			</SidebarMenuItem>
		</SidebarMenu>
	)
}

function Main({ items }: MainProps) {
	const { isMobile, setOpenMobile } = useSidebar()
	const router = useRouterState()
	const currentPath = router.location.pathname

	const handleMenuClick = () => {
		if (isMobile) {
			setOpenMobile(false)
		}
	}

	return (
		<SidebarGroup>
			<SidebarGroupContent>
				<SidebarMenu>
					{items.map((item) => {
						const isActive =
							item.path === '/user/'
								? currentPath === '/user' || currentPath === '/user/'
								: currentPath === item.path || currentPath.startsWith(`${item.path}/`)

						return (
							<SidebarMenuItem key={item.title}>
								<SidebarMenuButton
									tooltip={item.title}
									isActive={isActive}
									// Base UI uses 'render' to merge functionality onto custom components
									render={<RouterLink to={item.path} onClick={handleMenuClick} />}
								>
									<HugeiconsIcon icon={item.icon} />
									<span>{item.title}</span>
								</SidebarMenuButton>
							</SidebarMenuItem>
						)
					})}
				</SidebarMenu>
			</SidebarGroupContent>
		</SidebarGroup>
	)
}
