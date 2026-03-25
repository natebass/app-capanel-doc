import { Link, Outlet } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

export function StatusTemplateLayout() {
	return (
		<div className='min-h-screen bg-gradient-to-b from-background to-muted/30 flex flex-col'>
			<header className='w-full border-b bg-background/80 backdrop-blur-sm'>
				<div className='container mx-auto px-4 py-4 flex items-center justify-between'>
					<Link to='/' className='text-xl font-bold tracking-tight'>
						FastAPI Cloud
					</Link>
					<nav className='flex items-center gap-2'>
						<Button variant='ghost' size='sm' render={<Link to='/' />}>
							Home
						</Button>
						<Button variant='ghost' size='sm' render={<Link to='/status' />}>
							Status
						</Button>
					</nav>
				</div>
			</header>

			<main className='flex-1 flex items-center justify-center p-4'>
				<Outlet />
			</main>

			<footer className='border-t bg-background/80 backdrop-blur-sm'>
				<div className='container mx-auto px-4 py-6'>
					<div className='flex flex-col md:flex-row items-center justify-between gap-4'>
						<p className='text-sm text-muted-foreground'>FastAPI Cloud Status Portal</p>
						<div className='flex items-center gap-4 text-sm text-muted-foreground'>
							<Link to='/status' className='hover:text-foreground transition-colors'>
								System Status
							</Link>
							<Separator orientation='vertical' className='h-4' />
							<a
								href='https://docs.example.com'
								className='hover:text-foreground transition-colors'
							>
								Documentation
							</a>
							<Separator orientation='vertical' className='h-4' />
							<Link to='/' className='hover:text-foreground transition-colors'>
								Support
							</Link>
						</div>
					</div>
				</div>
			</footer>
		</div>
	)
}
