/**
 * Growth in ELA and mathematics — how far students moved.
 *
 * Deliberately not styled like the indicator cards. Growth carries no
 * performance colour, and the State Board adopted it for information only in
 * July 2025: it is not used for Local Control Funding Formula eligibility. The
 * panel says so, because a school can sit low on the academic indicator and
 * high on growth and a reader needs to know both are true.
 */
import { useQuery } from '@tanstack/react-query'

import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { toNumber } from '@/lib/results'
import { growthQuery } from '@/lib/services/accountability'

/** The five categories, worst to best, for positioning the marker. */
const CATEGORY_COUNT = 5

function CategoryScale({ category }: { category: number | null }) {
	// Decorative: the category name is stated in the text beneath.
	return (
		<div className='flex gap-1' aria-hidden>
			{Array.from({ length: CATEGORY_COUNT }, (_, i) => (
				<span
					key={i}
					className={
						category !== null && i < category
							? 'h-1.5 w-8 rounded-sm bg-foreground/70'
							: 'h-1.5 w-8 rounded-sm bg-muted'
					}
				/>
			))}
		</div>
	)
}

export function GrowthPanel({
	cds,
	year,
	studentGroup,
}: {
	cds: string
	year: number
	studentGroup: string
}) {
	const { data, isPending, error } = useQuery(growthQuery(cds, year, studentGroup))

	if (isPending) return <Skeleton className='h-32 w-full' />
	if (error) return null
	// The state publishes growth for districts and schools only, so there is
	// nothing to show statewide.
	if (!data || data.results.length === 0) return null

	return (
		<section className='space-y-4'>
			<header className='space-y-1'>
				<h2 className='text-lg font-semibold tracking-tight'>Student growth</h2>
				<p className='text-sm text-muted-foreground'>
					How far students moved compared with their own earlier results, rather than where they
					landed.
				</p>
			</header>

			<Alert>
				<AlertDescription>
					Growth is reported for information only. The State Board adopted it in July 2025 and it is
					not part of the accountability system, so it carries no performance colour.
				</AlertDescription>
			</Alert>

			<div className='grid gap-4 sm:grid-cols-2'>
				{data.results.map((result) => {
					const growth = toNumber(result.growth)
					return (
						<Card key={result.subject}>
							<CardContent className='space-y-3 pt-4'>
								<div className='flex items-baseline justify-between gap-2'>
									<h3 className='text-sm font-medium'>
										{result.subject === 'ELA' ? 'English Language Arts/Literacy' : 'Mathematics'}
									</h3>
									<span className='text-2xl font-semibold tabular-nums'>
										{growth === null ? '—' : `${growth > 0 ? '+' : ''}${growth.toFixed(1)}`}
									</span>
								</div>

								<CategoryScale category={result.performanceCategory ?? null} />
								<p className='text-sm'>{result.performanceCategoryName ?? 'No growth category'}</p>

								<dl className='grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-muted-foreground'>
									<dt>Students with a growth score</dt>
									<dd className='text-right tabular-nums'>
										{result.denominator?.toLocaleString() ?? '—'}
									</dd>
									<dt>Improved on last year</dt>
									<dd className='text-right tabular-nums'>
										{result.percentImproved === null
											? '—'
											: `${toNumber(result.percentImproved)?.toFixed(1)}%`}
									</dd>
								</dl>

								{result.estimateMethod === 'NONE' ? (
									<p className='text-xs text-muted-foreground'>{result.estimateMethodName}</p>
								) : null}
							</CardContent>
						</Card>
					)
				})}
			</div>
		</section>
	)
}
