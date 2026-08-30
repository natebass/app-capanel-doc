/**
 * A distribution as one stacked bar, lowest level on the left.
 *
 * Deliberately not a pie: the comparison people actually make is between rows —
 * this school against its district, one student group against another — and
 * bars stacked to a common baseline make that comparison possible at a glance.
 */
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import type { LevelResult } from '@/lib/client'
import { formatCount, formatPercent, hasDistribution, levelColor, toNumber } from '@/lib/results'
import { cn } from '@/lib/utils'

type AchievementBarProps = {
	levels: readonly LevelResult[]
	/** Marks where the state counts a student as meeting the standard. */
	proficientFromLevel?: number | null
	className?: string
	height?: 'sm' | 'md'
}

export function AchievementBar({
	levels,
	proficientFromLevel,
	className,
	height = 'md',
}: AchievementBarProps) {
	const barHeight = height === 'sm' ? 'h-2' : 'h-4'

	if (!hasDistribution(levels)) {
		return (
			<div
				className={cn('w-full rounded-full bg-achievement-empty', barHeight, className)}
				aria-hidden
			/>
		)
	}

	// The bar is a picture of the numbers; assistive technology is given the
	// numbers themselves rather than a description of the picture.
	const summary = levels.map((level) => `${level.name}: ${formatPercent(level.pct)}`).join(', ')

	return (
		<div className={cn('w-full', className)}>
			<span className='sr-only'>{summary}</span>
			<div className={cn('flex w-full overflow-hidden rounded-full', barHeight)} aria-hidden>
				{levels.map((level) => {
					const pct = toNumber(level.pct) ?? 0
					if (pct <= 0) return null
					const meetsStandard =
						proficientFromLevel != null && level.levelNumber >= proficientFromLevel
					return (
						<Tooltip key={level.levelNumber}>
							{/* The trigger is the segment itself; wrapping it in one would
							    size the segment against the wrapper rather than the bar. */}
							<TooltipTrigger
								className='h-full transition-opacity hover:opacity-80'
								style={{
									width: `${pct}%`,
									backgroundColor: levelColor(level.levelNumber, levels.length),
								}}
							/>
							<TooltipContent>
								<div className='font-medium'>{level.name}</div>
								<div className='text-xs'>
									{formatPercent(level.pct)} · {formatCount(level.count)} students
									{meetsStandard ? ' · meets the standard' : ''}
								</div>
							</TooltipContent>
						</Tooltip>
					)
				})}
			</div>
		</div>
	)
}

/** The key for a distribution, shown once per report rather than per bar. */
export function AchievementLegend({
	levels,
	className,
}: {
	levels: readonly { levelNumber: number; name: string }[]
	className?: string
}) {
	return (
		<ul className={cn('flex flex-wrap items-center gap-x-4 gap-y-1 text-xs', className)}>
			{levels.map((level) => (
				<li key={level.levelNumber} className='flex items-center gap-1.5'>
					<span
						className='size-2.5 shrink-0 rounded-sm'
						style={{ backgroundColor: levelColor(level.levelNumber, levels.length) }}
					/>
					<span className='text-muted-foreground'>{level.name}</span>
				</li>
			))}
		</ul>
	)
}
