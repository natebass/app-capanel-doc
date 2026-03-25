import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

export default function CardGrid() {
	const variants = ['subtle', 'outline', 'elevated'] as const

	return (
		<div className='flex flex-row flex-wrap gap-4'>
			{variants.map((variant) => (
				<Card key={variant} className='w-[320px]'>
					<CardHeader className='gap-2'>
						{/* shadcn Avatar implementation */}
						<Avatar className='h-12 w-12 rounded-md'>
							<AvatarImage src='https://picsum.photos/200/300' alt='Nue Camp' />
							<AvatarFallback>NC</AvatarFallback>
						</Avatar>
						<CardTitle className='mt-2'>Nue Camp</CardTitle>
						<CardDescription>
							This is the card body. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
						</CardDescription>
					</CardHeader>

					<CardFooter className='flex justify-end gap-2'>
						<Button variant='outline'>Learn more</Button>
						<Button>Try it out</Button>
					</CardFooter>
				</Card>
			))}
		</div>
	)
}
