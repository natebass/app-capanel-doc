/**
 * Every student group's result for one test, grouped by category.
 *
 * The gap against All Students is the number people are actually looking for,
 * so it is computed here rather than left to the reader.
 */
import { useQuery } from '@tanstack/react-query'

import { AchievementBar } from '@/components/results/AchievementBar'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table'
import type { StudentGroupResult } from '@/lib/client'
import { formatCount, formatPercent, hasDistribution, toNumber } from '@/lib/results'
import { type ReportSelection, studentGroupsQuery } from '@/lib/services/assessments'

function GapCell({ group, baseline }: { group: StudentGroupResult; baseline: number | null }) {
	const value = toNumber(group.metOrAbovePct)
	if (value === null || baseline === null) return <span className='text-muted-foreground'>—</span>
	const gap = value - baseline
	if (Math.abs(gap) < 0.05) return <span className='text-muted-foreground'>even</span>
	return (
		<span className='tabular-nums'>
			{gap > 0 ? '+' : ''}
			{gap.toFixed(1)}
		</span>
	)
}

export function StudentGroupTable({
	selection,
	testId,
}: {
	selection: ReportSelection
	testId: number
}) {
	const { data, isPending, error } = useQuery(studentGroupsQuery(selection, testId))

	if (isPending) return <Skeleton className='h-72 w-full' />
	if (error) return <p className='text-sm text-destructive'>{error.message}</p>
	if (!data || data.groups.length === 0) {
		return <p className='text-sm text-muted-foreground'>No student group results were reported.</p>
	}

	const baseline = toNumber(data.allStudents?.metOrAbovePct)
	const categories = [...new Set(data.groups.map((group) => group.category))]

	return (
		<div className='overflow-x-auto'>
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead className='min-w-56'>Student group</TableHead>
						<TableHead className='min-w-40'>Distribution</TableHead>
						<TableHead className='text-right'>Met or above</TableHead>
						<TableHead className='text-right'>vs. all students</TableHead>
						<TableHead className='text-right'>Tested</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					{categories.map((category) => (
						<>
							<TableRow key={`heading-${category}`} className='bg-muted/50 hover:bg-muted/50'>
								<TableCell
									colSpan={5}
									className='py-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground'
								>
									{category}
								</TableCell>
							</TableRow>
							{data.groups
								.filter((group) => group.category === category)
								.map((group) => (
									<TableRow key={`${category}-${group.studentGroupId}`}>
										<TableCell className='font-medium'>{group.name}</TableCell>
										<TableCell>
											{hasDistribution(group.levels) ? (
												<AchievementBar levels={group.levels} height='sm' />
											) : group.suppressed ? (
												<Badge variant='outline'>Withheld</Badge>
											) : (
												<span className='text-muted-foreground'>—</span>
											)}
										</TableCell>
										<TableCell className='text-right tabular-nums'>
											{formatPercent(group.metOrAbovePct)}
										</TableCell>
										<TableCell className='text-right'>
											<GapCell group={group} baseline={baseline} />
										</TableCell>
										<TableCell className='text-right tabular-nums'>
											{formatCount(group.studentsTested)}
										</TableCell>
									</TableRow>
								))}
						</>
					))}
				</TableBody>
			</Table>
			<p className='mt-3 text-xs text-muted-foreground'>
				Results are withheld for any group with fewer than 11 students tested.
			</p>
		</div>
	)
}
