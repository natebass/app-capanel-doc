/**
 * The local half of the Dashboard, beneath the state half.
 *
 * The state measures seven indicators and assigns each a colour. The seven
 * LCFF priorities here are not measured by anyone: each local educational
 * agency assesses itself and reports the result to its own governing board at
 * a public meeting. The section says so plainly, because a reader who assumes
 * these are state findings will misread every one of them.
 *
 * Local indicators are reported by the LEA, so a school shows its district's
 * report and the header says whose it is.
 */
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { PriorityCard } from '@/components/local-indicators/PriorityCard'
import { PriorityDetail } from '@/components/local-indicators/PriorityDetail'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { localIndicatorsQuery } from '@/lib/services/localIndicators'

export function LocalMeasures({ cds, year }: { cds: string; year: number }) {
	const { data, isPending, error } = useQuery(localIndicatorsQuery(cds, year))
	const [selected, setSelected] = useState<number | null>(null)

	if (isPending) return <Skeleton className='h-48 w-full' />
	if (error) {
		return (
			<Alert variant='destructive'>
				<AlertTitle>No local measures</AlertTitle>
				<AlertDescription>{error.message}</AlertDescription>
			</Alert>
		)
	}
	if (!data) return null

	const reportedElsewhere = data.reportedBy.cdsCode !== data.entity.cdsCode
	const active = selected ?? data.priorities.find((p) => p.performance !== null)?.priorityNumber

	return (
		<section className='space-y-4'>
			<header className='space-y-1'>
				<h2 className='text-lg font-semibold tracking-tight'>Local measures</h2>
				<p className='text-sm text-muted-foreground'>
					Self-assessed by{' '}
					<strong className='font-medium text-foreground'>{data.reportedBy.displayName}</strong>{' '}
					against the state&rsquo;s funding priorities, and reported to its governing board. These
					are not measured by the state and carry no performance colour.
				</p>
			</header>

			{reportedElsewhere ? (
				<Alert>
					<AlertDescription>
						Local measures are reported by the school district, not by individual schools, so these
						are {data.reportedBy.displayName}&rsquo;s answers for every school it runs.
					</AlertDescription>
				</Alert>
			) : null}

			<div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
				{data.priorities.map((priority) => (
					<PriorityCard
						key={priority.priorityNumber}
						summary={priority}
						selected={priority.priorityNumber === active}
						onSelect={setSelected}
					/>
				))}
			</div>

			{active ? (
				<Card>
					<CardHeader>
						<CardTitle className='text-base'>
							{data.priorities.find((p) => p.priorityNumber === active)?.name}
						</CardTitle>
					</CardHeader>
					<CardContent>
						<PriorityDetail cds={data.reportedBy.cdsCode} year={year} priority={active} />
					</CardContent>
				</Card>
			) : null}
		</section>
	)
}
