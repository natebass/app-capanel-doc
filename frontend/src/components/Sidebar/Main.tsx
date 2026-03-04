import { Link as RouterLink, useRouterState } from '@tanstack/react-router'
import type { LucideIcon } from 'lucide-react'

import {
	SidebarGroup,
	SidebarGroupContent,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	useSidebar,
} from '@/components/ui/sidebar'

export type Item = {
	icon: LucideIcon
	title: string
	path: string
}

interface MainProps {
	items: Item[]
}

export function Main({ items }: MainProps) {
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
						const isActive = currentPath === item.path

						return (
							<SidebarMenuItem key={item.title}>
								<SidebarMenuButton
									tooltip={item.title}
									isActive={isActive}
									// Base UI uses 'render' to merge functionality onto custom components
									render={<RouterLink to={item.path} onClick={handleMenuClick} />}
								>
									<item.icon />
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
