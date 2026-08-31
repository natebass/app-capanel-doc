/**
 * One priority in full: the self-ratings, then what the agency wrote.
 *
 * The narratives are the reason this data is worth showing, and they are the
 * agency's own words rather than an assessment of them — so they are presented
 * as a quotation, with their paragraph breaks intact, and attributed to the
 * board meeting that received them.
 */
import { useQuery } from '@tanstack/react-query'

import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from '@/components/ui/accordion'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { humanizeField, localIndicatorDetailQuery } from '@/lib/services/localIndicators'

/** The state publishes these self-ratings on a 1-5 scale. */
const SCALE_MAX = 5

function RatingRow({ field, value }: { field: string; value: number }) {
	const clamped = Math.max(0, Math.min(value, SCALE_MAX))
	return (
		<div className='flex items-center justify-between gap-4 py-1.5'>
			<span className='text-sm'>{humanizeField(field)}</span>
			<span className='flex items-center gap-2'>
				<span className='flex gap-0.5' aria-hidden>
					{Array.from({ length: SCALE_MAX }, (_, i) => (
						<span
							key={i}
							className={
								i < clamped ? 'h-2 w-4 rounded-sm bg-foreground/70' : 'h-2 w-4 rounded-sm bg-muted'
							}
						/>
					))}
				</span>
				<span className='w-10 text-right text-sm tabular-nums text-muted-foreground'>
					{value} / {SCALE_MAX}
				</span>
			</span>
		</div>
	)
}

export function PriorityDetail({
	cds,
	year,
	priority,
}: {
	cds: string
	year: number
	priority: number
}) {
	const { data, isPending, error } = useQuery(localIndicatorDetailQuery(cds, year, priority))

	if (isPending) return <Skeleton className='h-64 w-full' />
	if (error) return <p className='text-sm text-destructive'>{error.message}</p>
	if (!data) return null

	const ratings = Object.entries(data.ratings ?? {})
	const narratives = data.narratives ?? []

	return (
		<div className='space-y-6'>
			{data.description ? (
				<p className='text-sm text-muted-foreground'>{data.description}</p>
			) : null}

			{data.performance === null ? (
				<Alert>
					<AlertDescription>
						This agency reported nothing for this priority in {year - 1}–{String(year).slice(2)}.
						{data.countyOfficeOnly ? ' It is reported only by county offices of education.' : ''}
					</AlertDescription>
				</Alert>
			) : null}

			{ratings.length > 0 ? (
				<section className='space-y-1'>
					<h4 className='text-sm font-medium'>Self-ratings</h4>
					<p className='text-xs text-muted-foreground'>
						Rated by the agency itself on the state&rsquo;s 1&ndash;5 scale.
					</p>
					<div className='divide-y rounded-md border px-3 py-1'>
						{ratings.map(([field, value]) => (
							<RatingRow key={field} field={field} value={value} />
						))}
					</div>
				</section>
			) : null}

			{narratives.length > 0 ? (
				<section className='space-y-2'>
					<h4 className='text-sm font-medium'>In the agency&rsquo;s own words</h4>
					<Accordion className='rounded-md border'>
						{narratives.map((narrative) => (
							<AccordionItem key={narrative.field} value={narrative.field}>
								<AccordionTrigger className='px-3 text-sm'>
									{humanizeField(narrative.field)}
								</AccordionTrigger>
								<AccordionContent className='px-3'>
									{/* whitespace-pre-line keeps the paragraph breaks the
									    state's own text export throws away. */}
									<p className='whitespace-pre-line text-sm leading-relaxed text-muted-foreground'>
										{narrative.text}
									</p>
								</AccordionContent>
							</AccordionItem>
						))}
					</Accordion>
				</section>
			) : null}

			{data.additionalInfo ? (
				<section className='space-y-1'>
					<h4 className='text-sm font-medium'>Additional information</h4>
					<p className='whitespace-pre-line text-sm leading-relaxed text-muted-foreground'>
						{data.additionalInfo}
					</p>
				</section>
			) : null}
		</div>
	)
}
