/**
 * The accountability report — the layer caschooldashboard.org actually shows.
 *
 * Where /dashboard reports what students scored, this reports how the state
 * judged a school: one performance colour per indicator, the student groups
 * beneath it, and the history behind it.
 *
 * Five of the seven indicators here (chronic absenteeism, suspension,
 * graduation, college/career, English learner progress) have no assessment
 * source at all — they come from the state's own Dashboard files.
 *
 * The selection lives in the URL, so any view of this report is a link.
 *
 * On layout. The page is a header, a row of indicators, and one indicator
 * examined — read top to bottom, that is the order the question is actually
 * asked in. The entity, the year and the student group all sit in the header
 * rather than in a filter card, because they are what the heading means, not
 * a separate control panel. Choosing the entity itself has left the page
 * entirely: it lives in the navigation bar, where it is reachable from every
 * report rather than repeated on each one.
 *
 * On loading. The catalogue endpoint is slow and everything else on the page
 * used to wait behind it, so a cold visit spent a quarter of a minute looking
 * at three grey rectangles. Two things changed. The catalogue now arrives as
 * an assumption first (see `accountabilityShape`), which lets every other
 * request leave immediately and lets this page draw its real structure — its
 * indicator names, its filters, its tables, its prose — before a single figure
 * is known. And a wait long enough to look broken now says why it is long,
 * because the long case is a dataset being read for the first time, not a
 * fault. What is never assumed is a measured value: those stay skeletons.
 */
import { AnalyticsUpIcon, Download04Icon, GitCompareIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { useQuery } from '@tanstack/react-query'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useMemo, useState } from 'react'
import { z } from 'zod'

import { CompositionPanel } from '@/components/accountability/CompositionPanel'
import { GrowthPanel } from '@/components/accountability/GrowthPanel'
import { IndicatorCard } from '@/components/accountability/IndicatorCard'
import { IndicatorTrend } from '@/components/accountability/IndicatorTrend'
import {
	INDICATOR_GRID,
	IndicatorGridPlaceholder,
	InformationalGridPlaceholder,
	StudentGroupTablePlaceholder,
} from '@/components/accountability/Placeholders'
import { StudentGroupBreakdown } from '@/components/accountability/StudentGroupBreakdown'
import NavbarD52 from '@/components/common/navbar/navbar-D52'
import { SlowLoadNotice } from '@/components/common/status/SlowLoadNotice'
import { LocalMeasures } from '@/components/local-indicators/LocalMeasures'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ScrollReset from '@/hooks/ScrollReset'
import { useSlowLoad } from '@/hooks/useSlowLoad'
import {
	type AccountabilitySelection,
	ALL_STUDENTS,
	dashboardCatalogQuery,
	formatSchoolYear,
	indicatorGroupsQuery,
	indicatorsQuery,
	STATEWIDE_CDS,
} from '@/lib/services/accountability'
import { assumedCatalog, assumedIndicator } from '@/lib/services/accountabilityShape'
import { entityQuery } from '@/lib/services/assessments'

/**
 * The router parses search values as JSON, so a CDS code that looks like a
 * number comes back as one. It is a code, not a quantity, so it is coerced
 * back to a string here.
 */
const searchSchema = z.object({
	cds: z.coerce.string().length(14).default(STATEWIDE_CDS),
	year: z.coerce.number().int().optional(),
	studentGroup: z.coerce.string().default(ALL_STUDENTS),
	indicator: z.coerce.string().optional(),
})

export const Route = createFileRoute('/accountability/')({
	validateSearch: searchSchema,
	component: AccountabilityPage,
})

/**
 * The examined-indicator panel's height, fixed rather than fitted.
 *
 * Both tabs have to occupy the same box or switching between them would jump
 * the page, and the taller of the two is the trend chart. So the chart sets
 * the height and the student group table — which is arbitrarily long, and
 * would otherwise push the panel past its neighbour in the split — scrolls
 * inside it.
 */
const PANEL_BODY = 'h-[22rem] overflow-y-auto'

function AccountabilityPage() {
	const search = Route.useSearch()
	const navigate = useNavigate({ from: Route.fullPath })

	const catalog = useQuery(dashboardCatalogQuery(search.year))
	const ancestry = useQuery(entityQuery(search.cds))

	/**
	 * Never undefined: the query carries a placeholder, and a catalogue that
	 * failed outright still leaves the page a shape to draw. `assumed` is what
	 * separates the two, and it gates everything that would read as a fact.
	 */
	const reference = catalog.data ?? assumedCatalog()
	const assumed = catalog.isPlaceholderData || catalog.isError

	/**
	 * A year the state never published cannot be shown. The projected year is
	 * one of those: it is served beside the last published year rather than as
	 * a year of its own, so a link that names it resolves to that year here,
	 * the same way the API resolves it.
	 *
	 * While the catalogue is only assumed there is no published list to check
	 * against, so a year named in the URL is taken at its word — the URL is the
	 * better evidence of the two. Once the real catalogue lands it is checked.
	 */
	const year =
		search.year && (assumed || reference.years.includes(search.year))
			? search.year
			: reference.reportingYear
	const selection: AccountabilitySelection = {
		cds: search.cds,
		year,
		studentGroup: search.studentGroup,
	}

	const indicators = useQuery(indicatorsQuery(selection))

	/**
	 * The two tab strips are one question asked twice, so they move together:
	 * the grid's tab says which reading of the indicators is on screen, and the
	 * panel below opens on whatever answers it. Indicators is a report over
	 * time; At Risk is a question about who, so it opens the student groups.
	 * Either strip can still be moved on its own afterwards — this sets the
	 * panel, it does not lock it.
	 */
	const [view, setView] = useState('indicators')
	const [panel, setPanel] = useState('trend')

	function selectView(next: string) {
		setView(next)
		setPanel(next === 'at-risk' ? 'groups' : 'trend')
	}

	const entity = ancestry.data?.entity

	/**
	 * The API sorts results by the catalogue's own order, so the catalogue's
	 * first indicator is the one that will be selected when they arrive. Naming
	 * it now lets the breakdown below fetch alongside the grid rather than
	 * after it; if the entity does not report it, the real results correct the
	 * selection and the breakdown refetches.
	 */
	const selectedIndicator = useMemo(
		() =>
			search.indicator ?? indicators.data?.results[0]?.indicatorCode ?? assumedIndicator(reference),
		[search.indicator, indicators.data, reference],
	)

	const indicatorMeta = reference.indicators.find((item) => item.code === selectedIndicator)

	const groups = useQuery({
		...indicatorGroupsQuery(selection, selectedIndicator ?? ''),
		enabled: Boolean(selectedIndicator),
	})

	/**
	 * One wait, graded, covering both slow endpoints — a reader experiences the
	 * page filling in, not two requests. `isFetching` rather than `isPending`
	 * so a refetch over stale data is graded too: on this page that refetch is
	 * the recache, and it is exactly the case worth explaining.
	 */
	const loadStage = useSlowLoad(catalog.isFetching || indicators.isFetching || groups.isFetching)

	/** Base UI needs the value-to-label mapping to render the closed trigger. */
	const yearItems = useMemo(
		() =>
			reference.years.map((item) => ({
				value: String(item),
				label: formatSchoolYear(item),
			})),
		[reference],
	)

	const groupItems = useMemo(
		() =>
			reference.studentGroups.map((group) => ({
				value: group.code,
				label: group.name,
			})),
		[reference],
	)

	const groupNames = useMemo(
		() => Object.fromEntries(reference.studentGroups.map((group) => [group.code, group.name])),
		[reference],
	)

	const metaFor = (code: string) => reference.indicators.find((item) => item.code === code)

	/** The state publishes some measures alongside the seven without counting
	 *  them; they must not sit in the same grid. */
	const accountabilityResults = (indicators.data?.results ?? []).filter(
		(result) => !metaFor(result.indicatorCode)?.isInformational,
	)
	const informationalResults = (indicators.data?.results ?? []).filter(
		(result) => metaFor(result.indicatorCode)?.isInformational,
	)

	function update(next: Partial<z.infer<typeof searchSchema>>) {
		void navigate({ search: (previous) => ({ ...previous, ...next }) })
	}

	/**
	 * Only the statewide code names itself without a lookup. Anything else has
	 * to be fetched, so its heading is a skeleton rather than a guess — a wrong
	 * school name is worse than no school name.
	 */
	const displayName =
		entity?.displayName ?? (search.cds === STATEWIDE_CDS ? 'State of California' : null)
	/**
	 * The state is every entity's last ancestor, so naming it in the line
	 * distinguishes nothing. What it stood for — that there is a level above
	 * this one to go back to — the button beside the line says better, and
	 * only where there is somewhere to go.
	 */
	const ancestorLine =
		ancestry.data?.ancestors
			.filter((item) => item.cdsCode !== STATEWIDE_CDS)
			.map((item) => item.displayName)
			.join(' · ') ||
		(ancestry.data || search.cds === STATEWIDE_CDS ? 'Statewide accountability' : null)

	/**
	 * Both halves failing means the Dashboard files were never imported, which
	 * is an operator's problem rather than a reader's — so it takes the whole
	 * page and says what to run. A catalogue that fails on its own is reported
	 * in place instead, and the report stands on the guess: waiting on the
	 * slower of the two before deciding would flash this page and then replace
	 * it, and a fresh install is the only case that wants it.
	 */
	if (catalog.isError && indicators.isError) {
		return (
			<div>
				<NavbarD52 />
				<div className='container max-w-7xl mx-auto px-4 py-8'>
					<Alert variant='destructive'>
						<AlertTitle>No accountability data</AlertTitle>
						<AlertDescription>
							{catalog.error.message} Run <code>uv run app/scripts/ingest_dashboard_files.py</code>{' '}
							to load the state's Dashboard files.
						</AlertDescription>
					</Alert>
				</div>
			</div>
		)
	}

	/**
	 * The grid of indicator cards, named once because both tabs draw it. "At
	 * Risk" repeats "Indicators" verbatim until it has a filter of its own.
	 */
	const indicatorGrid = indicators.isPending ? (
		<IndicatorGridPlaceholder indicators={reference.indicators} />
	) : indicators.isError ? (
		<Alert variant='destructive'>
			<AlertDescription>{indicators.error.message}</AlertDescription>
		</Alert>
	) : indicators.data.results.length > 0 ? (
		<section className={INDICATOR_GRID}>
			{accountabilityResults.map((result) => (
				<IndicatorCard
					key={`${result.indicatorCode}-${result.studentGroupCode}`}
					result={result}
					unit={metaFor(result.indicatorCode)?.unit ?? 'percent'}
					lowerIsBetter={metaFor(result.indicatorCode)?.lowerIsBetter ?? false}
					selected={result.indicatorCode === selectedIndicator}
					onSelect={(code) => update({ indicator: code })}
				/>
			))}
		</section>
	) : (
		<Alert>
			<AlertTitle>Nothing reported</AlertTitle>
			<AlertDescription>
				The state reports no indicators for this entity, year and student group.
			</AlertDescription>
		</Alert>
	)

	return (
		<div className='bg-[#f3f4fa]'>
			<ScrollReset />
			<NavbarD52 />
			<div className='container max-w-7xl mx-auto px-4 py-8'>
				<div className='flex flex-col gap-8'>
					{/* Page Header */}
					<div>
						<div className='flex flex-wrap items-center gap-3 mb-2'>
							{displayName ? (
								<h1 className='text-3xl font-bold'>{displayName}</h1>
							) : (
								<Skeleton className='h-9 w-80 max-w-full rounded-md' />
							)}
							{entity?.isCharter ? <Badge variant='outline'>Charter school</Badge> : null}
						</div>
						{/* The filters read as part of the sentence naming the entity,
						    because that is what they are: the rest of what the heading
						    above means. */}
						<div className='flex flex-wrap items-center justify-between gap-y-2'>
							<div className='flex flex-wrap items-center gap-2'>
								{ancestorLine ? (
									<p className='text-muted-foreground text-lg'>{ancestorLine}</p>
								) : (
									<Skeleton className='h-6 w-56 max-w-full rounded-md' />
								)}
							</div>
							<div className='flex flex-wrap items-center gap-2'>
								<Select
									items={yearItems}
									value={String(year)}
									onValueChange={(value) => update({ year: Number(value) })}
								>
									<SelectTrigger id='accountability-year' aria-label='Year' className='w-36'>
										<SelectValue />
									</SelectTrigger>
									<SelectContent>
										{yearItems.map((item) => (
											<SelectItem key={item.value} value={item.value}>
												{item.label}
											</SelectItem>
										))}
									</SelectContent>
								</Select>
								<Select
									items={groupItems}
									value={search.studentGroup}
									onValueChange={(value) => value && update({ studentGroup: value })}
								>
									<SelectTrigger
										id='accountability-group'
										aria-label='Student group'
										className='w-56'
									>
										<SelectValue />
									</SelectTrigger>
									<SelectContent>
										{groupItems.map((item) => (
											<SelectItem key={item.value} value={item.value}>
												{item.label}
											</SelectItem>
										))}
									</SelectContent>
								</Select>
							</div>
						</div>
					</div>

					<SlowLoadNotice stage={loadStage} subject='this accountability report' />

					{catalog.error ? (
						<Alert variant='destructive'>
							<AlertTitle>The filters may be out of date</AlertTitle>
							<AlertDescription>
								{catalog.error.message} The years and student groups above are the ones this browser
								last saw.
							</AlertDescription>
						</Alert>
					) : null}

					{/* Indicator Cards */}
					<Tabs value={view} onValueChange={(value) => selectView(String(value))}>
						<TabsList>
							<TabsTrigger value='indicators'>Indicators</TabsTrigger>
							<TabsTrigger value='at-risk'>At Risk</TabsTrigger>
						</TabsList>
						<TabsContent value='indicators'>{indicatorGrid}</TabsContent>
						<TabsContent value='at-risk'>{indicatorGrid}</TabsContent>
					</Tabs>

					{/* The selected indicator, examined — and the actions that would
					    act on it. */}
					<div className='grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6'>
						<Card className='border'>
							{selectedIndicator && indicatorMeta ? (
								<Tabs value={panel} onValueChange={(value) => setPanel(String(value))}>
									<CardHeader>
										<div className='flex flex-wrap items-center justify-between gap-3'>
											<h2 className='text-lg font-semibold'>{indicatorMeta.name}</h2>
											<TabsList>
												<TabsTrigger value='trend'>Over time</TabsTrigger>
												<TabsTrigger value='groups'>Student groups</TabsTrigger>
											</TabsList>
										</div>
									</CardHeader>
									<CardContent>
										<TabsContent value='groups' className={PANEL_BODY}>
											{groups.isPending ? (
												<StudentGroupTablePlaceholder groups={reference.studentGroups} />
											) : groups.isError ? (
												<p className='text-sm text-destructive'>{groups.error.message}</p>
											) : (
												<StudentGroupBreakdown
													report={groups.data}
													unit={indicatorMeta.unit}
													lowerIsBetter={indicatorMeta.lowerIsBetter}
													groupNames={groupNames}
												/>
											)}
										</TabsContent>
										<TabsContent value='trend' className={PANEL_BODY}>
											<IndicatorTrend
												selection={selection}
												indicator={selectedIndicator}
												unit={indicatorMeta.unit}
											/>
										</TabsContent>
									</CardContent>
								</Tabs>
							) : (
								<>
									<CardHeader>
										<h2 className='text-lg font-semibold'>No indicator selected</h2>
									</CardHeader>
									<CardContent>
										<p className={`${PANEL_BODY} text-sm text-muted-foreground`}>
											Choose an indicator above to see its student groups and its history.
										</p>
									</CardContent>
								</>
							)}
						</Card>

						{/* Quick Actions — deliberately inert. The buttons name the
						    things this panel is expected to grow (projections for the
						    selected indicator, comparison, export) so the space is
						    reserved at the right size, but none of them do anything
						    yet and all of them say so. */}
						<Card className='bg-muted/50'>
							<CardHeader>
								<h2 className='text-lg font-semibold'>Quick Actions</h2>
							</CardHeader>
							<CardContent>
								<div className='flex flex-col gap-3'>
									<Button className='w-full' disabled title='Not available yet'>
										<HugeiconsIcon icon={AnalyticsUpIcon} className='mr-2' />
										Add a projection
									</Button>
									<Button variant='outline' className='w-full' disabled title='Not available yet'>
										<HugeiconsIcon icon={GitCompareIcon} className='mr-2' />
										Compare schools
									</Button>
									<Button variant='outline' className='w-full' disabled title='Not available yet'>
										<HugeiconsIcon icon={Download04Icon} className='mr-2' />
										Export this report
									</Button>
									<p className='text-xs text-muted-foreground'>Coming soon.</p>
								</div>
							</CardContent>
						</Card>
					</div>

					{indicators.isPending ? (
						<InformationalGridPlaceholder indicators={reference.indicators} />
					) : informationalResults.length > 0 ? (
						<section className='space-y-3'>
							<h2 className='text-sm font-medium text-muted-foreground'>
								Also published, for information
							</h2>
							<p className='text-sm text-muted-foreground'>
								Reported alongside the indicators above but not part of the accountability system,
								so these carry no performance colour.
							</p>
							<div className={INDICATOR_GRID}>
								{informationalResults.map((result) => (
									<IndicatorCard
										key={`${result.indicatorCode}-${result.studentGroupCode}`}
										result={result}
										unit={metaFor(result.indicatorCode)?.unit ?? 'percent'}
										lowerIsBetter={metaFor(result.indicatorCode)?.lowerIsBetter ?? false}
										selected={result.indicatorCode === selectedIndicator}
										onSelect={(code) => update({ indicator: code })}
									/>
								))}
							</div>
						</section>
					) : null}

					<CompositionPanel cds={selection.cds} year={selection.year} />

					<GrowthPanel
						cds={selection.cds}
						year={selection.year}
						studentGroup={selection.studentGroup}
					/>

					<LocalMeasures cds={selection.cds} year={selection.year} />

					{/* Needs nothing loaded, and is the part of the page most likely to
					    answer the question a reader arrived with, so it is never held
					    back behind a request. */}
					<footer className='border-t pt-6 text-xs text-muted-foreground'>
						<p>
							Source: California Department of Education, California School Dashboard downloadable
							data files. Figures are reproduced as published. A group shown as{' '}
							<strong>Not rated</strong> either sits outside the accountability system (English
							learners only, reclassified, English only, and the assessment-type groups are reported
							for information), has fewer than 30 students, or has only one year of data.
						</p>
					</footer>
				</div>
			</div>
		</div>
	)
}
