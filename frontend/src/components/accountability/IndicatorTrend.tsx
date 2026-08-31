/**
 * One indicator's history, with the dot coloured the way the state coloured it.
 *
 * The line breaks across 2019–20 and 2020–21 rather than interpolating: no
 * Dashboard was published for either year, so drawing through the gap would
 * invent two years of accountability that never existed.
 */
import { useQuery } from '@tanstack/react-query'
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from 'recharts'

import { Alert, AlertDescription } from '@/components/ui/alert'
import {
	type ChartConfig,
	ChartContainer,
	ChartTooltip,
	ChartTooltipContent,
} from '@/components/ui/chart'
import { Skeleton } from '@/components/ui/skeleton'
import { toNumber } from '@/lib/results'
import {
	type AccountabilitySelection,
	DASHBOARD_COLORS,
	indicatorTrendQuery,
} from '@/lib/services/accountability'

const config = {
	status: { label: 'Status', color: 'var(--color-chart-1)' },
} satisfies ChartConfig

export function IndicatorTrend({
	selection,
	indicator,
	unit,
}: {
	selection: AccountabilitySelection
	indicator: string
	unit: string
}) {
	const { data, isPending, error } = useQuery(indicatorTrendQuery(selection, indicator))

	if (isPending) return <Skeleton className='h-64 w-full' />
	if (error) return <p className='text-sm text-destructive'>{error.message}</p>
	if (!data || data.points.length === 0) {
		return <p className='text-sm text-muted-foreground'>No history has been reported.</p>
	}

	const byYear = new Map(data.points.map((point) => [point.reportingYear, point]))
	const years = data.points.map((point) => point.reportingYear)
	const span: number[] = []
	for (let year = Math.min(...years); year <= Math.max(...years); year += 1) span.push(year)

	const rows = span.map((year) => {
		const point = byYear.get(year)
		return {
			year: `${year - 1}–${String(year).slice(2)}`,
			// A missing year is null, not zero, so recharts leaves a gap.
			status: point ? toNumber(point.currStatus) : null,
			color: point?.color ?? null,
			colorName: point?.colorName ?? null,
			isProjected: point?.isProjected ?? false,
		}
	})

	const suffix = unit === 'percent' ? '%' : ''

	return (
		<div className='space-y-3'>
			{data.missingYears.length > 0 ? (
				<Alert>
					<AlertDescription>
						No Dashboard was published for{' '}
						{data.missingYears.map((year) => `${year - 1}–${String(year).slice(2)}`).join(' or ')},
						so the line is broken rather than drawn through.
					</AlertDescription>
				</Alert>
			) : null}
			<ChartContainer config={config} className='h-64 w-full'>
				<LineChart data={rows} margin={{ left: 4, right: 8, top: 8 }}>
					<CartesianGrid vertical={false} />
					<XAxis dataKey='year' tickLine={false} axisLine={false} tickMargin={8} />
					<YAxis
						tickLine={false}
						axisLine={false}
						tickMargin={8}
						tickFormatter={(value: number) => `${value}${suffix}`}
					/>
					<ChartTooltip content={<ChartTooltipContent />} />
					<Line
						dataKey='status'
						type='monotone'
						connectNulls={false}
						strokeWidth={2}
						stroke='var(--color-status)'
						dot={(props: { cx?: number; cy?: number; index?: number; payload?: unknown }) => {
							const row = rows[props.index ?? 0]
							const swatch = row?.color ? DASHBOARD_COLORS[row.color] : undefined
							if (props.cx === undefined || props.cy === undefined || !row) {
								return <g key={props.index} />
							}
							return (
								<circle
									key={props.index}
									cx={props.cx}
									cy={props.cy}
									r={5}
									fill={swatch?.token ?? 'var(--color-muted)'}
									stroke='var(--color-background)'
									strokeWidth={2}
									strokeDasharray={row.isProjected ? '2 2' : undefined}
								/>
							)
						}}
					/>
				</LineChart>
			</ChartContainer>
		</div>
	)
}
