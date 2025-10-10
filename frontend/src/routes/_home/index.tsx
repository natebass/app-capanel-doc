import { Avatar, Button, Card, For, Stack } from '@chakra-ui/react';
import { createFileRoute, Link } from '@tanstack/react-router';

export const Route = createFileRoute('/_home/')({
	component: HomePage,
});

function HomePage() {
	return (
		<main className='text-element-text-primary w-full flex flex-col items-center pt-16'>
			<div className='flex max-w-6xl px-6 lg:px-0'>
				<div className='flex-1 xl:flex-5/12 flex flex-col justify-center items-center text-center gap-4'>
					<h1 className='text-5xl font-urbanist text-echart-text-primary font-bold'>
						Student information dashboard panel.
					</h1>
					<p className='text-lg  text-element-text-regular font-urbanist font-medium'>
						Discover standards based on California's Accountability System.
					</p>
					<Button className='tracking-wider' mt={4} asChild>
						<Link to='/dashboard'>Search for a school or district</Link>
					</Button>
					<Button className='tracking-wider' asChild>
						<Link to='/dashboard'>View state-wide</Link>
					</Button>
				</div>
				<div className='flex-1 xl:flex-7/12 ps-8'>
					<img
						src='/pic/d.png'
						alt='Collage of three dashboard features.'
						height={440}
						width={440}
					/>
				</div>
			</div>
			<h2 className='mt-24 text-center text-3xl font-bold text-element-text-regular font-urbanist'>
				About the data
			</h2>
			<p className='mt-8 text-center max-w-lg font-urbanist text-lg'>
				We use the standards of California's Accountability System. The data is
				sourced from reports published by the California Department of Education
				https://www.cde.ca.gov/ds/.
			</p>
			<h2 className='mt-24 text-center text-3xl font-bold text-element-text-regular font-urbanist'>
				Features
			</h2>
			<div className='flex mt-8'>
				<Stack gap='4' direction='row' wrap='wrap'>
					<For each={['subtle', 'outline', 'elevated']}>
						{(variant) => (
							<Card.Root width='320px' variant={variant} key={variant}>
								<Card.Body gap='2'>
									<Avatar.Root size='lg' shape='rounded'>
										<Avatar.Image src='https://picsum.photos/200/300' />
										<Avatar.Fallback name='Nue Camp' />
									</Avatar.Root>
									<Card.Title mb='2'>Nue Camp</Card.Title>
									<Card.Description>
										This is the card body. Lorem ipsum dolor sit amet,
										consectetur adipiscing elit.
									</Card.Description>
								</Card.Body>
								<Card.Footer justifyContent='flex-end'>
									<Button variant='outline'>Learn more</Button>
									<Button>Try it out</Button>
								</Card.Footer>
							</Card.Root>
						)}
					</For>
				</Stack>
			</div>
		</main>
	);
}
