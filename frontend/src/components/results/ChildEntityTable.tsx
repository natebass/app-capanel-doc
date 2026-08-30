/**
 * The counties, districts or schools inside the selected entity.
 *
 * This is the "search and compare" view: pick a county and see its districts
 * ranked, pick a district and see its schools.
 */
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table'
import type { EntityPublic } from '@/lib/client'
import { formatCount, formatPercent, formatScore } from '@/lib/results'
import { childResultsQuery, type ReportSelection } from '@/lib/services/assessments'

const CHILD_LABEL: Record<string, string> = {
	county: 'Counties',
	district: 'Districts',
	school: 'Schools',
}

export function ChildEntityTable({
	selection,
	testId,
	onSelectEntity,
}: {
	selection: ReportSelection
	testId: number
	onSelectEntity: (entity: EntityPublic) => void
}) {
	const [descending, setDescending] = useState(true)
	const { data, isPending, error } = useQuery(
		childResultsQuery(selection, testId, { descending, limit: 25 }),
	)

	if (isPending) return <Skeleton className='h-72 w-full' />
	if (error) return <p className='text-sm text-destructive'>{error.message}</p>
	if (!data || data.data.length === 0) {
		return (
			<p className='text-sm text-muted-foreground'>Nothing inside this entity reported results.</p>
		)
	}

	return (
		<div className='space-y-3'>
			<div className='flex flex-wrap items-center justify-between gap-2'>
				<p className='text-sm text-muted-foreground'>
					{CHILD_LABEL[data.childLevel] ?? 'Entities'} inside {data.entity.displayName} — showing{' '}
					{data.data.length} of {formatCount(data.count)}
				</p>
				<Button variant='outline' size='sm' onClick={() => setDescending((value) => !value)}>
					{descending ? 'Highest first' : 'Lowest first'}
				</Button>
			</div>
			<div className='overflow-x-auto'>
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead className='min-w-56'>Name</TableHead>
							<TableHead className='text-right'>Met or above</TableHead>
							<TableHead className='text-right'>Mean scale score</TableHead>
							<TableHead className='text-right'>Tested</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{data.data.map((row) => (
							<TableRow
								key={row.entity.cdsCode}
								className='cursor-pointer'
								onClick={() => onSelectEntity(row.entity)}
							>
								<TableCell>
									<span className='font-medium'>{row.entity.displayName}</span>
									{row.entity.isCharter ? (
										<Badge variant='outline' className='ml-2'>
											Charter
										</Badge>
									) : null}
								</TableCell>
								<TableCell className='text-right tabular-nums'>
									{row.suppressed ? 'Withheld' : formatPercent(row.metOrAbovePct)}
								</TableCell>
								<TableCell className='text-right tabular-nums'>
									{formatScore(row.meanScaleScore)}
								</TableCell>
								<TableCell className='text-right tabular-nums'>
									{formatCount(row.studentsTested)}
								</TableCell>
							</TableRow>
						))}
					</TableBody>
				</Table>
			</div>
		</div>
	)
}
