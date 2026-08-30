/**
 * The reporting categories beneath a test's overall score.
 *
 * Areas, domains and composites are all "part of the test" but they are not
 * interchangeable — a composite is a roll-up of domains — so they are grouped
 * under their own headings rather than listed flat.
 */
import { useQuery } from '@tanstack/react-query'

import { AchievementBar } from '@/components/results/AchievementBar'
import { Skeleton } from '@/components/ui/skeleton'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import type { SubscoreKind, SubscoreResult } from '@/lib/client'
import { formatCount, formatPercent, formatScore, hasDistribution } from '@/lib/results'
import { type ReportSelection, subscoresQuery } from '@/lib/services/assessments'

const KIND_HEADING: Record<SubscoreKind, string> = {
	area: 'Areas',
	composite_area: 'Composite areas',
	domain: 'Domains',
	composite: 'Composites',
}

const KIND_ORDER: SubscoreKind[] = ['area', 'composite_area', 'domain', 'composite']

function SubscoreRow({ subscore }: { subscore: SubscoreResult }) {
	return (
		<div className='grid grid-cols-[minmax(0,12rem)_1fr_auto] items-center gap-3'>
			<span className='truncate text-sm'>{subscore.name}</span>
			{hasDistribution(subscore.bands) ? (
				<AchievementBar levels={subscore.bands} />
			) : (
				<span className='text-sm text-muted-foreground'>Not reported</span>
			)}
			<span className='text-sm tabular-nums text-muted-foreground'>
				{subscore.meanScaleScore != null ? (
					<Tooltip>
						<TooltipTrigger render={<span className='cursor-help' />}>
							{formatScore(subscore.meanScaleScore)}
						</TooltipTrigger>
						<TooltipContent>Mean scale score</TooltipContent>
					</Tooltip>
				) : (
					formatCount(subscore.total)
				)}
			</span>
		</div>
	)
}

export function SubscorePanel({
	selection,
	testId,
}: {
	selection: ReportSelection
	testId: number
}) {
	const { data, isPending, error } = useQuery(subscoresQuery(selection, testId))

	if (isPending) return <Skeleton className='h-40 w-full' />
	if (error) return <p className='text-sm text-destructive'>{error.message}</p>
	if (!data || data.subscores.length === 0) {
		return (
			<p className='text-sm text-muted-foreground'>
				This test reports no areas or domains for the selected year.
			</p>
		)
	}

	const bands = data.subscores[0]?.bands ?? []

	return (
		<div className='space-y-5'>
			{KIND_ORDER.map((kind) => {
				const items = data.subscores.filter((subscore) => subscore.kind === kind)
				if (items.length === 0) return null
				return (
					<section key={kind} className='space-y-2'>
						<h4 className='text-sm font-medium'>{KIND_HEADING[kind]}</h4>
						{items.map((subscore) => (
							<SubscoreRow key={subscore.code} subscore={subscore} />
						))}
					</section>
				)
			})}
			{bands.length > 0 ? (
				<p className='text-xs text-muted-foreground'>
					Bands run {bands.map((band) => band.name).join(' → ')}. Percentages are the share of
					students in each band; {formatPercent(bands.at(-1)?.pct)} reached the highest band on the
					first category shown.
				</p>
			) : null}
		</div>
	)
}
