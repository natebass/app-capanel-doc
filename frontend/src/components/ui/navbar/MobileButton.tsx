import { Button, Menu, Portal } from '@chakra-ui/react';
import { useNavigate } from '@tanstack/react-router';
import { FaBars } from 'react-icons/fa';
import useAuth from '../../../hooks/useAuth.ts';

export default function MobileButton(className: { className?: string }) {
	const { user: currentUser } = useAuth();
	const navigate = useNavigate();

	return (
		<div className={`${className} `}>
			<Menu.Root
				navigate={({ value }) => {
					navigate({ to: `/${value}` });
				}}
			>
				<Menu.Trigger asChild>
					<Button variant='outline' size='sm'>
						<FaBars className='h-5 w-5' />
					</Button>
				</Menu.Trigger>
				<Portal>
					<Menu.Positioner>
						<Menu.Content>
							<Menu.Item
								value='home'
								onSelect={() => navigate({ to: '/' })}
								className='text-[1rem] p-3 tracking-wide'
							>
								Home
							</Menu.Item>
							<Menu.Item
								value='dashboard'
								onSelect={() => navigate({ to: '/dashboard' })}
								className='text-[1rem] p-3 tracking-wide'
							>
								Dashboard
							</Menu.Item>
							{currentUser ? (
								<Menu.Item
									value='sign-out'
									onSelect={() => navigate({ to: '/sign-out' })}
									className='text-[1rem] p-3 tracking-wide'
								>
									Sign Out
								</Menu.Item>
							) : (
								<>
									<Menu.Item
										value='login'
										onSelect={() => navigate({ to: '/login' })}
										className='text-[1rem] p-3 tracking-wide'
									>
										Sign In
									</Menu.Item>
									<Menu.Item
										value='sign-up'
										onSelect={() => navigate({ to: '/sign-up' })}
										className='text-[1rem] p-3 tracking-wide'
									>
										Sign Up
									</Menu.Item>
								</>
							)}
						</Menu.Content>
					</Menu.Positioner>
				</Portal>
			</Menu.Root>
		</div>
	);
}
