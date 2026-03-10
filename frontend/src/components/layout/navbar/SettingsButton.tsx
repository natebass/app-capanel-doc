import { Link } from '@tanstack/react-router'
import { FaGear } from 'react-icons/fa6'

import { buttonVariants } from '@/components/ui/button.tsx'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu.tsx'
import useAuth from '@/lib/hooks/useAuth.ts'
import { cn } from '@/lib/utils.ts'

export default function SettingsButton() {
	const { user: currentUser, logout } = useAuth()

	return (
		<div className='ml-1'>
			<DropdownMenu>
				<DropdownMenuTrigger className={cn(buttonVariants({ variant: 'outline' }))}>
					<FaGear />
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
