/**
 * One LCFF priority's self-reported result.
 *
 * Deliberately not styled like an {@link IndicatorCard}. The state half of the
 * Dashboard earns a performance colour; this half does not, and using the same
 * five hues would tell the reader something untrue.
 */
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import type { LocalIndicatorSummary } from '@/lib/client'
import { performanceTone } from '@/lib/services/localIndicators'
import { cn } from '@/lib/utils'

const TONE_CLASS: Record<string, string> = {
	met: 'border-l-4 border-l-emerald-600',
	notMet: 'border-l-4 border-l-amber-600',
	notMetTwoYears: 'border-l-4 border-l-red-700',
	none: 'border-l-4 border-l-muted',
}

const TONE_BADGE: Record<string, string> = {
	met: 'bg-emerald-50 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100',
	notMet: 'bg-amber-50 text-amber-900 dark:bg-amber-950 dark:text-amber-100',
	notMetTwoYears: 'bg-red-50 text-red-900 dark:bg-red-950 dark:text-red-100',
	none: 'bg-muted text-muted-foreground',
}

export function PriorityCard({
	summary,
	selected = false,
	onSelect,
}: {
	summary: LocalIndicatorSummary
	selected?: boolean
	onSelect?: (priorityNumber: number) => void
}) {
	const tone = performanceTone(summary.performance)
	const reported = summary.performance !== null

	return (
		<Card
			className={cn(
				TONE_CLASS[tone],
				'transition-colors',
				onSelect && 'cursor-pointer hover:border-foreground/30',
				selected && 'ring-1 ring-foreground/20',
				!reported && 'opacity-70',
			)}
			onClick={onSelect ? () => onSelect(summary.priorityNumber) : undefined}
		>
			<CardContent className='space-y-2 pt-4'>
				<div className='flex items-start justify-between gap-2'>
					<h3 className='text-sm font-medium leading-tight'>{summary.name}</h3>
					<span className='shrink-0 text-xs text-muted-foreground'>
						Priority {summary.priorityNumber}
					</span>
				</div>

				<Badge variant='secondary' className={cn('font-medium', TONE_BADGE[tone])}>
					{summary.performance ?? 'Not reported'}
				</Badge>

				{summary.meetingDate ? (
					<p className='text-xs text-muted-foreground'>
						Reported to the board on{' '}
						{new Date(`${summary.meetingDate}T00:00:00`).toLocaleDateString(undefined, {
							year: 'numeric',
							month: 'long',
							day: 'numeric',
						})}
					</p>
				) : null}

				{!reported && summary.countyOfficeOnly ? (
					<p className='text-xs text-muted-foreground'>
						Reported only by county offices of education.
					</p>
				) : null}
			</CardContent>
		</Card>
	)
}
