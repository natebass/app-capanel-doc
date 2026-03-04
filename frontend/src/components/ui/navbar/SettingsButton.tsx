import { Link } from '@tanstack/react-router'
import { FaGear } from 'react-icons/fa6'

import { buttonVariants } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import useAuth from '@/lib/hooks/useAuth'
import { cn } from '@/lib/utils'

export default function SettingsButton() {
	const { user: currentUser } = useAuth()

	return (
		<div className='ml-1'>
			<DropdownMenu>
				<DropdownMenuTrigger className={cn(buttonVariants({ variant: 'outline' }))}>
					<FaGear />
				</DropdownMenuTrigger>
				<DropdownMenuContent>
					{currentUser ? (
						<DropdownMenuItem className='text-base p-3 tracking-wide' render={<Link to='/login' />}>
							Sign Out
						</DropdownMenuItem>
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
