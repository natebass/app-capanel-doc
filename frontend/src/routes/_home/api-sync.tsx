import { Card } from '@chakra-ui/react';
import { createFileRoute, Link } from '@tanstack/react-router';
import SearchHomepageForm from '../../components/ui/form/home-search-form';

export const Route = createFileRoute('/_home/api-sync')({
	component: RouteComponent,
});

function RouteComponent() {
	return (
		<div className=' flex container mx-auto flex-col xl:flex-row'>
			<div className='flex-1'>
				<header className='rounded-3xl'>
					<div className='mt-2 p-14'>
						<h2 className='text-3xl pb-12 font-medium font-roboto text-[#1c1b1d] '>
							Search for a school to find information.
						</h2>
						<SearchHomepageForm />
					</div>
				</header>
			</div>
			<div className='flex-1'>
				<section className='mt-2 p-14 flex flex-col xl:ps-24'>
					<Card.Root>
						<Card.Header>Discover school standards.</Card.Header>
						<Card.Body>
							<ul className=' list-disc  '>
								<li className='pt-12 text-lg'>
									Search for a school, district or{' '}
									<Link
										className='text-element-primary underline'
										to='/dashboard'
									>
										{' '}
										view the California state-wide standards.
									</Link>
								</li>
							</ul>
						</Card.Body>
						<Card.Footer />
					</Card.Root>
				</section>
			</div>
		</div>
	);
}
