import { Menu01Icon } from '@hugeicons/core-free-icons'
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

export default function MobileButton() {
	const { user: currentUser, logout } = useAuth()

	return (
		<DropdownMenu>
			<DropdownMenuTrigger
				className={cn('min-[1180px]:hidden', buttonVariants({ variant: 'outline' }))}
			>
				<HugeiconsIcon icon={Menu01Icon} />
			</DropdownMenuTrigger>
			<DropdownMenuContent>
				<DropdownMenuItem className='text-base p-3 tracking-wide' render={<Link to='/' />}>
					Home
				</DropdownMenuItem>
				<DropdownMenuItem className='text-base p-3 tracking-wide' render={<Link to='/dashboard' />}>
					Dashboard
				</DropdownMenuItem>
				{currentUser ? (
					<>
						<DropdownMenuItem className='text-base p-3 tracking-wide' render={<Link to='/user' />}>
							My Account
						</DropdownMenuItem>
						<DropdownMenuItem className='text-base p-3 tracking-wide' onClick={logout}>
							Sign Out
						</DropdownMenuItem>
					</>
				) : (
					<>
						<DropdownMenuItem className='text-base p-3 tracking-wide' render={<Link to='/login' />}>
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
	)
}
