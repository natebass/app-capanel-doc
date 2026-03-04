import { Link } from '@tanstack/react-router'
import { FaBars } from 'react-icons/fa'

import { buttonVariants } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import useAuth from '@/lib/hooks/useAuth'
import { cn } from '@/lib/utils'

export default function MobileButton() {
	const { user: currentUser } = useAuth()

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
					<DropdownMenuItem className='text-base p-3 tracking-wide' render={<Link to='/login' />}>
						Sign Out
					</DropdownMenuItem>
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
