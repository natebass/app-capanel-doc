/**
 * One indicator's performance colour, the way the Dashboard shows it.
 *
 * The colour is the headline, so it is the largest thing on the card and is
 * never the only signal — the published level names travel with it for anyone
 * who cannot distinguish the five hues.
 */
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import type { IndicatorResult } from '@/lib/client'
import {
	DASHBOARD_COLORS,
	describeChange,
	explainMissingColor,
	formatStatus,
} from '@/lib/services/accountability'
import { cn } from '@/lib/utils'

export function IndicatorCard({
	result,
	unit,
	lowerIsBetter,
	selected = false,
	onSelect,
}: {
	result: IndicatorResult
	unit: string
	lowerIsBetter: boolean
	selected?: boolean
	onSelect?: (indicatorCode: string) => void
}) {
	const swatch = result.color ? DASHBOARD_COLORS[result.color] : undefined
	const change = describeChange(result.change, lowerIsBetter)
	const missingColor = explainMissingColor(result)

	return (
		<Card
			className={cn(
				'relative overflow-hidden transition-colors',
				onSelect && 'cursor-pointer hover:border-foreground/30',
				selected && 'border-foreground/60 ring-1 ring-foreground/20',
			)}
			onClick={onSelect ? () => onSelect(result.indicatorCode) : undefined}
		>
			{/* The colour bar carries the same information as the badge text, so a
          reader who cannot see it loses nothing. */}
			<div
				aria-hidden
				className='h-2 w-full'
				style={{ backgroundColor: swatch?.token ?? 'var(--color-muted)' }}
			/>
			<CardContent className='space-y-3 pt-4'>
				<div className='flex items-start justify-between gap-2'>
					<h3 className='text-sm font-medium leading-tight'>{result.indicatorName}</h3>
					{result.isProjected ? (
						<Badge variant='outline' className='shrink-0 border-dashed'>
							Projected
						</Badge>
					) : null}
				</div>

				<p className='text-2xl font-semibold tabular-nums'>
					{formatStatus(result.currStatus, unit)}
				</p>

				<div className='flex flex-wrap items-center gap-2 text-xs'>
					{swatch ? (
						<span
							className='rounded-full px-2 py-0.5 font-medium'
							style={{ backgroundColor: swatch.token, color: swatch.text }}
						>
							{swatch.name}
						</span>
					) : (
						<span className='rounded-full bg-muted px-2 py-0.5 text-muted-foreground'>
							No colour
						</span>
					)}
					<span
						className={cn(
							'text-muted-foreground',
							change.direction === 'good' && 'text-[var(--color-cde-dashboard-green)]',
							change.direction === 'bad' && 'text-[var(--color-cde-dashboard-red)]',
						)}
					>
						{change.label}
					</span>
				</div>

				{result.studentGroupCode !== 'ALL' ? (
					<p className='text-xs text-muted-foreground'>
						Reported for{' '}
						{result.studentGroupCode === 'EL' ? 'English learners' : result.studentGroupCode} only
					</p>
				) : null}

				{missingColor ? <p className='text-xs text-muted-foreground'>{missingColor}</p> : null}
			</CardContent>
		</Card>
	)
}
