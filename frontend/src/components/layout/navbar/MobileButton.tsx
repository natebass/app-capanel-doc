import { Link } from '@tanstack/react-router'
import { FaBars } from 'react-icons/fa'

import { buttonVariants } from '@/components/ui/button.tsx'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu.tsx'
import useAuth from '@/lib/hooks/useAuth.ts'
import { cn } from '@/lib/utils.ts'

export default function MobileButton() {
	const { user: currentUser, logout } = useAuth()

	return (
		<DropdownMenu>
			<DropdownMenuTrigger
				className={cn('min-[1180px]:hidden', buttonVariants({ variant: 'outline' }))}
			>
				<FaBars />
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
