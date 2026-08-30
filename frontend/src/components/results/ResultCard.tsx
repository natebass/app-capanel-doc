import { AchievementBar, AchievementLegend } from '@/components/results/AchievementBar'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
/**
 * One test's headline result, with its distribution and how it compares with
 * the district, county and state.
 */
import type { AssessmentPublic, EntityResults, ResultSummary } from '@/lib/client'
import {
	formatCount,
	formatPercent,
	formatScore,
	hasDistribution,
	missingReason,
} from '@/lib/results'

function Metric({ label, value, hint }: { label: string; value: string; hint?: string }) {
	const body = (
		<div className='space-y-0.5'>
			<div className='text-xs text-muted-foreground'>{label}</div>
			<div className='font-medium tabular-nums'>{value}</div>
		</div>
	)
	if (!hint) return body
	return (
		<Tooltip>
			<TooltipTrigger render={<div className='cursor-help' />}>{body}</TooltipTrigger>
			<TooltipContent className='max-w-72'>{hint}</TooltipContent>
		</Tooltip>
	)
}

export function ResultCard({
	result,
	assessment,
	comparisons,
	onSelect,
	selected,
}: {
	result: ResultSummary
	assessment: AssessmentPublic | undefined
	comparisons: readonly EntityResults[]
	onSelect: () => void
	selected: boolean
}) {
	const scheme = assessment?.levelScheme
	const reported = hasDistribution(result.levels)

	return (
		<Card
			className={selected ? 'ring-2 ring-primary' : undefined}
			data-testid={`result-card-${result.testId}`}
		>
			<CardHeader>
				<div className='flex flex-wrap items-start justify-between gap-2'>
					<div>
						<CardTitle className='text-base'>{result.testName}</CardTitle>
						<CardDescription>{result.subject}</CardDescription>
					</div>
					<div className='flex flex-wrap items-center gap-1'>
						{result.derivedFromChildren ? (
							<Tooltip>
								<TooltipTrigger render={<Badge variant='outline' />}>Recalculated</TooltipTrigger>
								<TooltipContent className='max-w-72'>
									The research files publish one aggregate covering every school, so this
									charter-filtered figure is summed from the school rows. Counts are exact; the mean
									scale score is weighted by tests with valid scores.
								</TooltipContent>
							</Tooltip>
						) : null}
						{result.suppressed ? <Badge variant='outline'>Withheld</Badge> : null}
					</div>
				</div>
			</CardHeader>
			<CardContent className='space-y-4'>
				{reported ? (
					<>
						<div className='flex items-baseline gap-2'>
							<span className='text-3xl font-semibold tabular-nums'>
								{formatPercent(result.metOrAbovePct)}
							</span>
							<Tooltip>
								<TooltipTrigger
									render={
										<span className='cursor-help text-sm text-muted-foreground underline decoration-dotted' />
									}
								>
									met or exceeded the standard
									{result.metOrAboveSource === 'derived' ? ' (derived)' : ''}
								</TooltipTrigger>
								<TooltipContent className='max-w-72'>
									{result.metOrAboveSource === 'derived'
										? 'The state does not publish a combined figure for this test, so it is summed from the levels at or above the state’s proficiency cut.'
										: 'Published by the state.'}
								</TooltipContent>
							</Tooltip>
						</div>

						<AchievementBar
							levels={result.levels}
							proficientFromLevel={scheme?.proficientFromLevel}
						/>
						<AchievementLegend levels={result.levels} />

						<div className='grid grid-cols-2 gap-4 border-t pt-3 sm:grid-cols-4'>
							<Metric label='Enrolled' value={formatCount(result.studentsEnrolled)} />
							<Metric label='Tested' value={formatCount(result.studentsTested)} />
							<Metric
								label='Participation'
								value={formatPercent(result.participationRate)}
								hint='Students tested as a share of students enrolled.'
							/>
							<Metric
								label='Mean scale score'
								value={formatScore(result.meanScaleScore)}
								hint={
									result.meanScaleScore === null
										? 'Scale scores are set per grade and are not comparable across grades, so the state publishes no mean on an all-grades row.'
										: undefined
								}
							/>
						</div>

						{comparisons.length > 0 ? (
							<div className='space-y-2 border-t pt-3'>
								<div className='text-xs font-medium text-muted-foreground'>Compared with</div>
								{comparisons.map((comparison) => {
									const peer = comparison.results.find((item) => item.testId === result.testId)
									if (!peer) return null
									return (
										<div
											key={comparison.entity.cdsCode}
											className='grid grid-cols-[1fr_auto] items-center gap-x-3 gap-y-1'
										>
											<span className='truncate text-sm'>{comparison.entity.displayName}</span>
											<span className='text-sm tabular-nums text-muted-foreground'>
												{formatPercent(peer.metOrAbovePct)}
											</span>
											<AchievementBar
												levels={peer.levels}
												proficientFromLevel={scheme?.proficientFromLevel}
												height='sm'
												className='col-span-2'
											/>
										</div>
									)
								})}
							</div>
						) : null}
					</>
				) : (
					<p className='text-sm text-muted-foreground'>
						{missingReason(result.suppressed ?? false)}
					</p>
				)}

				<button
					type='button'
					onClick={onSelect}
					className='text-sm font-medium text-primary underline-offset-4 hover:underline'
				>
					{selected ? 'Showing details below' : 'Show details'}
				</button>
			</CardContent>
		</Card>
	)
}
