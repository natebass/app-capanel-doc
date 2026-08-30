/**
 * One entity's result for every grade a test reports.
 *
 * Unlike the all-grades row, each single grade has a mean scale score, so it
 * is shown here — comparing a grade against itself over time is the only way a
 * scale score is meaningfully comparable.
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
import { formatCount, formatPercent, formatScore, hasDistribution } from '@/lib/results'
import { gradesQuery, type ReportSelection } from '@/lib/services/assessments'

export function GradeTable({
	selection,
	testId,
	onSelectGrade,
}: {
	selection: ReportSelection
	testId: number
	onSelectGrade: (grade: string) => void
}) {
	const { data, isPending, error } = useQuery(gradesQuery(selection, testId))

	if (isPending) return <Skeleton className='h-64 w-full' />
	if (error) return <p className='text-sm text-destructive'>{error.message}</p>
	if (!data || data.grades.length === 0) {
		return <p className='text-sm text-muted-foreground'>No results were reported by grade.</p>
	}

	return (
		<div className='overflow-x-auto'>
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead className='min-w-40'>Grade</TableHead>
						<TableHead className='min-w-40'>Distribution</TableHead>
						<TableHead className='text-right'>Met or above</TableHead>
						<TableHead className='text-right'>Mean scale score</TableHead>
						<TableHead className='text-right'>Tested</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					{data.grades.map((grade) => (
						<TableRow
							key={grade.grade}
							data-state={grade.grade === selection.grade ? 'selected' : undefined}
							className='cursor-pointer'
							onClick={() => onSelectGrade(grade.grade)}
						>
							<TableCell className='font-medium'>{grade.label}</TableCell>
							<TableCell>
								{hasDistribution(grade.levels) ? (
									<AchievementBar levels={grade.levels} height='sm' />
								) : grade.suppressed ? (
									<Badge variant='outline'>Withheld</Badge>
								) : (
									<span className='text-muted-foreground'>—</span>
								)}
							</TableCell>
							<TableCell className='text-right tabular-nums'>
								{formatPercent(grade.metOrAbovePct)}
							</TableCell>
							<TableCell className='text-right tabular-nums'>
								{formatScore(grade.meanScaleScore)}
							</TableCell>
							<TableCell className='text-right tabular-nums'>
								{formatCount(grade.studentsTested)}
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</div>
	)
}
