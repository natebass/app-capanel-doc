/**
 * The report's own structure, drawn before its figures arrive.
 *
 * These are not grey boxes standing in for a page. They are the page: the same
 * card, the same colour bar, the same table with the same columns, holding the
 * indicator and student group names the catalogue already knows. Only the
 * measured values are skeletons, because only the measured values are unknown.
 *
 * That distinction is the whole point. A reader who can already see that
 * Chronic Absenteeism and Suspension Rate are coming, in that order, in cards
 * of that size, is oriented before the first number lands — and when the
 * numbers do land nothing moves, because the layout was right all along.
 *
 * What is deliberately absent: any hint of a value. No placeholder colour bar
 * that could read as a performance colour, no zeroes, no arrows. An assumed
 * layout is honest; an assumed figure would not be.
 */
import { IndicatorGauge } from '@/components/accountability/IndicatorGauge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table'
import { useAfterFirstPaint } from '@/hooks/useAfterFirstPaint'
import type { IndicatorPublic, StudentGroupCodePublic } from '@/lib/client'
import { assumedCatalog } from '@/lib/services/accountabilityShape'

/**
 * The indicator grid's own responsive shape, shared with the loaded page.
 *
 * The placeholder and the real grid must break at exactly the same widths, or
 * the report would reflow the moment its figures arrive — which is the one
 * thing this whole module exists to prevent.
 */
export const INDICATOR_GRID =
	'grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5'

/**
 * One indicator card, named but unmeasured.
 *
 * The gauge is the unrated one the real card falls back to — every colour, no
 * needle — so nothing here can be mistaken for a rating, and the card's most
 * conspicuous element is already at its final size and position. When the
 * figures land, the needle gauge appears in the space this one is holding.
 */
export function IndicatorCardPlaceholder({ name }: { name?: string }) {
	return (
		<Card className='relative overflow-hidden' aria-hidden>
			<CardContent className='space-y-3 pt-4'>
				<IndicatorGauge color={null} />
				<div className='flex items-start justify-between gap-2'>
					{name ? (
						<h3 className='text-sm font-medium leading-tight text-muted-foreground'>{name}</h3>
					) : (
						<Skeleton className='h-4 w-32 rounded-md' />
					)}
				</div>
				{/* Sized to the 2xl figure it replaces, so the card does not resize. */}
				<Skeleton className='h-8 w-24 rounded-md' />
				<div className='flex items-center gap-1.5'>
					<Skeleton className='h-5 w-20 rounded-full' />
				</div>
			</CardContent>
		</Card>
	)
}

/**
 * The indicator grid, in the state's own order.
 *
 * Only the accountability indicators: the informational ones are reported far
 * lower down the loaded page, so drawing them here would put them somewhere
 * they are about to leave.
 */
export function IndicatorGridPlaceholder({ indicators }: { indicators: Array<IndicatorPublic> }) {
	const accountability = [...indicators]
		.sort((a, b) => a.sortOrder - b.sortOrder)
		.filter((indicator) => !indicator.isInformational)

	return (
		<section className={INDICATOR_GRID}>
			{accountability.map((indicator) => (
				<IndicatorCardPlaceholder key={indicator.code} name={indicator.name} />
			))}
		</section>
	)
}

/**
 * The measures published alongside the seven without counting towards them,
 * in the position and with the explanation the loaded page gives them.
 */
export function InformationalGridPlaceholder({
	indicators,
}: {
	indicators: Array<IndicatorPublic>
}) {
	const informational = [...indicators]
		.sort((a, b) => a.sortOrder - b.sortOrder)
		.filter((indicator) => indicator.isInformational)

	if (informational.length === 0) return null

	return (
		<section className='space-y-3'>
			<h2 className='text-sm font-medium text-muted-foreground'>Also published, for information</h2>
			<p className='text-sm text-muted-foreground'>
				Reported alongside the indicators above but not part of the accountability system, so these
				carry no performance colour.
			</p>
			<div className={INDICATOR_GRID}>
				{informational.map((indicator) => (
					<IndicatorCardPlaceholder key={indicator.code} name={indicator.name} />
				))}
			</div>
		</section>
	)
}

/**
 * The student group table, with the group names already in it.
 *
 * The state does not report every group for every indicator, so this lists
 * more rows than the loaded table usually holds. It is the right trade: the
 * columns, the reading order and the left-hand column are all true, and the
 * table shortening is a smaller disturbance than a table appearing from
 * nothing.
 */
export function StudentGroupTablePlaceholder({
	groups = assumedCatalog().studentGroups,
}: {
	/** Defaults to the assumed catalogue, for panels that hold no catalogue. */
	groups?: Array<StudentGroupCodePublic>
}) {
	// Around half the nodes on this page, and always scrolled well out of sight
	// while the report is loading. Held back one frame so it is not in front of
	// the header and filters that a reader can actually see.
	const painted = useAfterFirstPaint()

	// The loaded table leads with All Students and follows with the rest.
	const rows = [
		...groups.filter((group) => group.code === 'ALL'),
		...groups.filter((group) => group.code !== 'ALL'),
	]

	if (!painted) return null

	return (
		<div className='overflow-x-auto' aria-hidden>
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead>Student group</TableHead>
						<TableHead className='text-right'>Status</TableHead>
						<TableHead className='text-right'>Change</TableHead>
						<TableHead>Colour</TableHead>
						<TableHead className='text-right'>Students</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					{rows.map((group) => (
						<TableRow key={group.code} className={group.code === 'ALL' ? 'font-medium' : undefined}>
							<TableCell className='text-muted-foreground'>{group.name}</TableCell>
							<TableCell className='text-right'>
								<Skeleton className='ml-auto h-4 w-12 rounded-md' />
							</TableCell>
							<TableCell className='text-right'>
								<Skeleton className='ml-auto h-4 w-16 rounded-md' />
							</TableCell>
							<TableCell>
								<Skeleton className='h-5 w-14 rounded-full' />
							</TableCell>
							<TableCell className='text-right'>
								<Skeleton className='ml-auto h-4 w-14 rounded-md' />
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</div>
	)
}

/** The trend chart's footprint, so the tab does not collapse while it loads. */
export function TrendPlaceholder() {
	return (
		<div className='space-y-3' aria-hidden>
			<div className='flex h-64 w-full items-end gap-4 rounded-xl border p-4'>
				{/* Deliberately flat and equal: an uneven skeleton would read as a
				    shape the data has not been shown to have. */}
				{Array.from({ length: 8 }, (_, index) => (
					<Skeleton key={index} className='h-full flex-1 rounded-md opacity-40' />
				))}
			</div>
		</div>
	)
}

/**
 * The enrolment panel's bars, named where the catalogue names them.
 *
 * Enrolment uses the same student group vocabulary as the indicators, so the
 * left-hand labels are known before the shares are.
 */
export function CompositionPlaceholder({
	groups = assumedCatalog().studentGroups,
}: {
	groups?: Array<StudentGroupCodePublic>
}) {
	// The heading and the Census Day note are cheap and true, so they are never
	// held back; the bar rows beneath them are eighty-odd nodes below the fold,
	// so they wait for the first paint to be over.
	const painted = useAfterFirstPaint()

	// The panel reports the demographic groups, not the assessment-type ones.
	const rows = groups.filter((group) => !['SBA', 'CAA', 'CAST', 'ALL'].includes(group.code))

	return (
		<section className='space-y-4'>
			<header className='space-y-1'>
				<h2 className='text-lg font-semibold tracking-tight'>Who attends</h2>
				<p className='text-sm text-muted-foreground'>
					Students enrolled on Census Day, the first Wednesday in October. Groups overlap, so the
					shares do not add up to 100%.
				</p>
			</header>
			<Card>
				<CardContent className='space-y-2 pt-6' aria-hidden>
					{(painted ? rows : []).map((group) => (
						<div key={group.code} className='flex items-center gap-3'>
							<span className='w-56 shrink-0 truncate text-sm text-muted-foreground'>
								{group.name}
							</span>
							<span className='relative h-4 flex-1 overflow-hidden rounded-sm bg-muted' />
							<Skeleton className='h-4 w-16 shrink-0 rounded-md' />
							<Skeleton className='h-4 w-20 shrink-0 rounded-md' />
						</div>
					))}
				</CardContent>
			</Card>
		</section>
	)
}

/**
 * The growth panel, which is always the same two subjects.
 *
 * ELA and mathematics are the only subjects the state reports growth for, so
 * both cards can be drawn and titled with nothing loaded at all.
 */
export function GrowthPlaceholder() {
	return (
		<section className='space-y-4'>
			<header className='space-y-1'>
				<h2 className='text-lg font-semibold tracking-tight'>Student growth</h2>
				<p className='text-sm text-muted-foreground'>
					How far students moved compared with their own earlier results, rather than where they
					landed.
				</p>
			</header>
			<div className='grid gap-4 sm:grid-cols-2' aria-hidden>
				{['English Language Arts/Literacy', 'Mathematics'].map((subject) => (
					<Card key={subject}>
						<CardContent className='space-y-3 pt-4'>
							<div className='flex items-baseline justify-between gap-2'>
								<h3 className='text-sm font-medium text-muted-foreground'>{subject}</h3>
								<Skeleton className='h-8 w-16 rounded-md' />
							</div>
							<div className='flex gap-1'>
								{Array.from({ length: 5 }, (_, index) => (
									<span key={index} className='h-1.5 w-8 rounded-sm bg-muted' />
								))}
							</div>
							<Skeleton className='h-4 w-40 rounded-md' />
							<div className='space-y-1 pt-1'>
								<Skeleton className='h-3 w-full rounded-md' />
								<Skeleton className='h-3 w-2/3 rounded-md' />
							</div>
						</CardContent>
					</Card>
				))}
			</div>
		</section>
	)
}
