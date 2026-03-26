import { Gauge } from '@/components/dashboard/gauge'
import type { IndicatorSummary } from '@/lib/client'
import { COLOR_LEVELS, type IndicatorCode, INDICATORS } from '@/lib/constants/indicators'
import { cn } from '@/lib/utils'
import { useEquityReport } from '@/routes/-hooks/hooks/useDashboardData'

export type ColorKey = 'red' | 'orange' | 'yellow' | 'green' | 'blue'

interface IndicatorCardProps {
	indicator: IndicatorSummary
	onClick?: () => void
	onColorClick?: (color: ColorKey) => void
	compact?: boolean
	cds?: string
	reportingyear?: string
}

export function IndicatorCard({
	indicator,
	onClick,
	onColorClick,
	compact = false,
	cds,
	reportingyear,
}: IndicatorCardProps) {
	const config = INDICATORS[indicator.indicator as IndicatorCode]
	const performanceLevel = (indicator.statuslevel ?? 0) as 0 | 1 | 2 | 3 | 4 | 5
	const { data: equityData } = useEquityReport(
		cds ?? null,
		indicator.indicator,
		reportingyear ?? '2025',
	)

	if (!config) return null

	const hasData = indicator.currstatus !== null || indicator.statuslevel !== null
	const colorCounts = equityData?.color_counts
	const total = colorCounts
		? colorCounts.red +
			colorCounts.orange +
			colorCounts.yellow +
			colorCounts.green +
			colorCounts.blue
		: 0

	const segments = colorCounts
		? [
				{
					key: 'red' as ColorKey,
					count: colorCounts.red,
					color: COLOR_LEVELS[1].color,
					textColor: 'white',
				},
				{
					key: 'orange' as ColorKey,
					count: colorCounts.orange,
					color: COLOR_LEVELS[2].color,
					textColor: 'white',
				},
				{
					key: 'yellow' as ColorKey,
					count: colorCounts.yellow,
					color: COLOR_LEVELS[3].color,
					textColor: 'black',
				},
				{
					key: 'green' as ColorKey,
					count: colorCounts.green,
					color: COLOR_LEVELS[4].color,
					textColor: 'white',
				},
				{
					key: 'blue' as ColorKey,
					count: colorCounts.blue,
					color: COLOR_LEVELS[5].color,
					textColor: 'white',
				},
			].filter((s) => s.count > 0)
		: []

	const handleColorClick = (e: React.MouseEvent, colorKey: ColorKey) => {
		e.stopPropagation()
		onColorClick?.(colorKey)
	}

	return (
		<button
			type='button'
			className={cn(
				'bg-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring text-left w-full block',
				!hasData && 'opacity-60',
			)}
			onClick={onClick}
			aria-label={`${config.shortLabel} indicator`}
		>
			<div className='font-semibold'>{config.shortLabel}</div>
			<Gauge value={performanceLevel} size={compact ? 120 : 140} />
			{total > 0 && (
				<div className='flex justify-center gap-1'>
					{segments.map((segment) => (
						<button
							type='button'
							key={segment.key}
							className='flex flex-col gap-1 px-2 py-2.5 hover:bg-muted hover:text-foreground dark:hover:bg-muted/50 cursor-pointer rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring'
							onClick={(e) => handleColorClick(e, segment.key)}
							aria-label={`${segment.key} status: ${segment.count} groups`}
						>
							<div className='w-full h-2 mb-1 rounded' style={{ backgroundColor: segment.color }} />
							<div
								className='mx-1 flex h-6 w-6 items-center justify-center rounded-full text-sm font-bold'
								style={{ backgroundColor: segment.color, color: segment.textColor }}
							>
								{segment.count}
							</div>
						</button>
					))}
				</div>
			)}
		</button>
	)
}

export function IndicatorCardSkeleton({ compact = false }: { compact?: boolean }) {
	return (
		<div>
			<div className='flex flex-col items-center gap-2'>
				<div className='h-4 w-16 animate-pulse rounded bg-muted/40' />
				<div
					className='animate-pulse rounded-t-full bg-muted/40'
					style={{ width: compact ? 100 : 140, height: compact ? 65 : 91 }}
				/>
				<div className='h-6 w-12 animate-pulse rounded bg-muted/40' />
				<div className='h-3 w-20 animate-pulse rounded bg-muted/40' />
			</div>
		</div>
	)
}
