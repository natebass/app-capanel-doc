/**
 * Who attends — the Census Day enrolment count, beside the performance figures.
 *
 * The groups deliberately overlap: a student can be counted as Hispanic, an
 * English learner and socioeconomically disadvantaged at once, so the bars are
 * each drawn against the whole and the note says the rates do not sum to 100.
 * Stacking them would be a lie.
 */
import { useQuery } from '@tanstack/react-query'

import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { toNumber } from '@/lib/results'
import { enrollmentQuery } from '@/lib/services/accountability'

export function CompositionPanel({ cds, year }: { cds: string; year: number }) {
	const { data, isPending, error } = useQuery(enrollmentQuery(cds, year))

	if (isPending) return <Skeleton className='h-40 w-full' />
	if (error) return null
	if (!data || data.groups.length === 0) return null

	return (
		<section className='space-y-4'>
			<header className='space-y-1'>
				<h2 className='text-lg font-semibold tracking-tight'>Who attends</h2>
				<p className='text-sm text-muted-foreground'>
					{data.totalEnrollment?.toLocaleString() ?? '—'} students enrolled on Census Day, the first
					Wednesday in October. Groups overlap, so the shares do not add up to 100%.
				</p>
			</header>

			<Card>
				<CardContent className='space-y-2 pt-6'>
					{data.groups.map((group) => {
						const rate = toNumber(group.rate) ?? 0
						return (
							<div key={group.studentGroupCode} className='flex items-center gap-3'>
								<span className='w-56 shrink-0 truncate text-sm' title={group.name}>
									{group.name}
								</span>
								<span className='relative h-4 flex-1 overflow-hidden rounded-sm bg-muted'>
									<span
										className='absolute inset-y-0 left-0 rounded-sm bg-foreground/60'
										style={{ width: `${Math.min(rate, 100)}%` }}
									/>
								</span>
								<span className='w-16 shrink-0 text-right text-sm tabular-nums'>
									{rate.toFixed(1)}%
								</span>
								<span className='w-20 shrink-0 text-right text-xs tabular-nums text-muted-foreground'>
									{group.subgroupTotal?.toLocaleString() ?? '—'}
								</span>
							</div>
						)
					})}
				</CardContent>
			</Card>
		</section>
	)
}
