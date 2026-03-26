import { Settings02Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { Link } from '@tanstack/react-router'

import { buttonVariants } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils.ts'
import useAuth from '@/routes/-hooks/hooks/useAuth.ts'

export default function SettingsButton() {
	const { user: currentUser, logout } = useAuth()

	return (
		<div className='ml-1'>
			<DropdownMenu>
				<DropdownMenuTrigger className={cn(buttonVariants({ variant: 'outline' }))}>
					<HugeiconsIcon icon={Settings02Icon} />
				</DropdownMenuTrigger>
				<DropdownMenuContent>
					{currentUser ? (
						<>
							<DropdownMenuItem
								className='text-base p-3 tracking-wide'
								render={<Link to='/user' />}
							>
								My Account
							</DropdownMenuItem>
							<DropdownMenuItem className='text-base p-3 tracking-wide' onClick={logout}>
								Sign Out
							</DropdownMenuItem>
						</>
					) : (
						<>
							<DropdownMenuItem
								className='text-base p-3 tracking-wide'
								render={<Link to='/login' />}
							>
								Sign In
							</DropdownMenuItem>
							<DropdownMenuItem
								className='text-base p-3 tracking-wide'
								render={<Link to='/sign-up' />}
							>
								Sign Up
							</DropdownMenuItem>
						</>
					)}
				</DropdownMenuContent>
			</DropdownMenu>
		</div>
	)
}
