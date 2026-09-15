/**
 * The local half of the Dashboard, before the agency's own answers arrive.
 *
 * Lives beside {@link LocalMeasures} rather than with the accountability
 * placeholders so this component, and the route that owns it, stay in one
 * bundle: importing across that boundary pulled the accountability catalogue
 * snapshot into the shared chunk, where every page paid to parse it.
 *
 * The priority names are not known here, so these cards are unnamed — but
 * their count, their left border and their grid match the loaded ones, which
 * is what stops the page reflowing beneath them.
 */
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useAfterFirstPaint } from '@/hooks/useAfterFirstPaint'

export function LocalMeasuresPlaceholder({ count = 8 }: { count?: number }) {
	// Bottom of a long report: the cards are never on screen at first paint, so
	// they wait a frame rather than delaying what is.
	const painted = useAfterFirstPaint()

	return (
		<section className='space-y-4'>
			<header className='space-y-1'>
				<h2 className='text-lg font-semibold tracking-tight'>Local measures</h2>
				<p className='text-sm text-muted-foreground'>
					Self-assessed against the state&rsquo;s funding priorities and reported to a governing
					board. These are not measured by the state and carry no performance colour.
				</p>
			</header>
			<div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4' aria-hidden>
				{Array.from({ length: painted ? count : 0 }, (_, index) => (
					<Card key={index} className='border-l-4 border-l-muted opacity-70'>
						<CardContent className='space-y-2 pt-4'>
							<div className='flex items-start justify-between gap-2'>
								<Skeleton className='h-4 w-28 rounded-md' />
								<Skeleton className='h-3 w-14 shrink-0 rounded-md' />
							</div>
							<Skeleton className='h-5 w-20 rounded-md' />
						</CardContent>
					</Card>
				))}
			</div>
		</section>
	)
}
