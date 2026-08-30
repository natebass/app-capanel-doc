/**
 * The same figure across every year the state reported it.
 *
 * The line is deliberately broken rather than interpolated where a year is
 * missing: 2019–20 has no results at all because testing was suspended, and
 * drawing through the gap would invent a trend.
 */
import { useQuery } from '@tanstack/react-query'
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from 'recharts'

import { Alert, AlertDescription } from '@/components/ui/alert'
import {
	ChartContainer,
	ChartTooltip,
	ChartTooltipContent,
	type ChartConfig,
} from '@/components/ui/chart'
import { Skeleton } from '@/components/ui/skeleton'
import { toNumber } from '@/lib/results'
import { type ReportSelection, trendQuery } from '@/lib/services/assessments'

const config = {
	metOrAbovePct: { label: 'Met or exceeded', color: 'var(--achievement-4)' },
} satisfies ChartConfig

export function TrendChart({ selection, testId }: { selection: ReportSelection; testId: number }) {
	const { data, isPending, error } = useQuery(trendQuery(selection, testId))

	if (isPending) return <Skeleton className='h-64 w-full' />
	if (error) return <p className='text-sm text-destructive'>{error.message}</p>
	if (!data || data.points.length === 0) {
		return <p className='text-sm text-muted-foreground'>No results have been reported over time.</p>
	}

	const points = data.points.map((point) => ({
		year: `${point.testYear - 1}–${String(point.testYear).slice(2)}`,
		metOrAbovePct: toNumber(point.metOrAbovePct),
		studentsTested: point.studentsTested,
	}))

	return (
		<div className='space-y-3'>
			{data.scaleBreakNote ? (
				<Alert>
					<AlertDescription>{data.scaleBreakNote}</AlertDescription>
				</Alert>
			) : null}
			<ChartContainer config={config} className='h-64 w-full'>
				<LineChart data={points} margin={{ left: 4, right: 8, top: 8 }}>
					<CartesianGrid vertical={false} />
					<XAxis dataKey='year' tickLine={false} axisLine={false} tickMargin={8} />
					<YAxis
						tickLine={false}
						axisLine={false}
						tickMargin={8}
						domain={[0, 100]}
						tickFormatter={(value: number) => `${value}%`}
					/>
					<ChartTooltip content={<ChartTooltipContent />} />
					<Line
						dataKey='metOrAbovePct'
						type='monotone'
						stroke='var(--color-metOrAbovePct)'
						strokeWidth={2}
						dot={{ r: 3 }}
						connectNulls={false}
					/>
				</LineChart>
			</ChartContainer>
			<p className='text-xs text-muted-foreground'>
				Testing was suspended statewide in 2019–20, so that year has no results.
			</p>
		</div>
	)
}
