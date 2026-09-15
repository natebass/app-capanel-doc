/**
 * Query options for the California School Dashboard accountability API.
 *
 * This is a different publication from the assessment reports in
 * `assessments.ts`: those say what students scored, these say how the state
 * judged a school. The two use different student-group vocabularies — short
 * codes like `SED` here, numeric CAASPP ids there — so their query keys are
 * kept separate rather than sharing a cache. The generated options key each
 * operation by its own name and parameters, which keeps that separation.
 */
import {
	type DashboardCatalog,
	dashboardReadCatalogOptions,
	dashboardReadChildrenOptions,
	dashboardReadEnrollmentOptions,
	dashboardReadGrowthOptions,
	dashboardReadIndicatorOptions,
	dashboardReadIndicatorsOptions,
	dashboardReadTrendOptions,
} from '@/lib/client'
import { toNumber } from '@/lib/results'
import { assumedCatalog, rememberCatalog } from '@/lib/services/accountabilityShape'
import { reference, report } from '@/lib/services/query'

export const STATEWIDE_CDS = '00000000000000'
export const ALL_STUDENTS = 'ALL'

export type AccountabilitySelection = {
	cds: string
	year: number
	studentGroup: string
}

/**
 * The catalogue, with a guess standing in until it answers.
 *
 * This endpoint is the slowest on the page and every other query on the page
 * waits behind it, because the year they are all keyed by comes out of it.
 * That is a waterfall built on reference data that changes a few times a year.
 *
 * The placeholder breaks it. `placeholderData` gives the page a catalogue on
 * its first render, so the report's real structure draws immediately and the
 * indicator, enrolment and growth requests all leave at once rather than in
 * series. When the real catalogue lands it replaces the guess; where the guess
 * named a different year, the queries keyed by it simply refetch.
 *
 * `isPlaceholderData` is how a component tells the two apart, and it must:
 * the guess is good enough to lay out a page and never good enough to present
 * as a state figure.
 */
export function dashboardCatalogQuery(year?: number) {
	const options = reference(
		dashboardReadCatalogOptions({ query: year ? { year } : {} }),
		'Could not load the accountability catalogue.',
	)
	const load = options.queryFn as (context: never) => Promise<DashboardCatalog>
	/**
	 * Only the unparameterised catalogue is worth keeping.
	 *
	 * Asked for a year, this endpoint answers about that year: `/catalog?year=
	 * 2021` reports a `reportingYear` of 2021. Remembering that would make a
	 * year somebody once linked to into the year every later visit opens on —
	 * and since every other query is keyed by it, the page would spend a six
	 * second request on the wrong year before the real catalogue corrected it.
	 * The indicator and student group lists are identical either way, so
	 * nothing is lost by keeping only the canonical answer.
	 */
	const canonical = year === undefined

	// Cast on the way out for the same reason `described` casts: the generated
	// context type belongs to this one operation and cannot be named here
	// without repeating the whole of it.
	return {
		...options,
		placeholderData: assumedCatalog,
		// Remembered here rather than in an effect so a catalogue is kept once
		// per fetch, not once per render of everything that reads it.
		queryFn: async (context: never) => {
			const catalog = await load(context)
			if (canonical) rememberCatalog(catalog)
			return catalog
		},
	} as typeof options & { placeholderData: typeof assumedCatalog }
}

export function indicatorsQuery(selection: AccountabilitySelection) {
	return report(
		dashboardReadIndicatorsOptions({
			query: {
				cds: selection.cds,
				year: selection.year,
				studentGroup: selection.studentGroup,
			},
		}),
		'Could not load the accountability indicators.',
	)
}

export function indicatorGroupsQuery(selection: AccountabilitySelection, indicator: string) {
	return report(
		dashboardReadIndicatorOptions({
			query: { cds: selection.cds, year: selection.year, indicator },
		}),
		'Could not load the student group breakdown.',
	)
}

export function indicatorTrendQuery(selection: AccountabilitySelection, indicator: string) {
	return report(
		dashboardReadTrendOptions({
			query: {
				cds: selection.cds,
				indicator,
				studentGroup: selection.studentGroup,
			},
		}),
		'Could not load the history for that indicator.',
	)
}

export function indicatorChildrenQuery(
	selection: AccountabilitySelection,
	indicator: string,
	options: { descending?: boolean; limit?: number } = {},
) {
	const { descending = true, limit = 50 } = options
	return report(
		dashboardReadChildrenOptions({
			query: {
				cds: selection.cds,
				year: selection.year,
				indicator,
				studentGroup: selection.studentGroup,
				descending,
				limit,
			},
		}),
		'Could not load the schools inside this entity.',
	)
}

/**
 * Groups the state reports for information but never assigns a colour to.
 *
 * These are not small-sample cases — statewide they carry hundreds of
 * thousands of students — they simply sit outside the accountability system,
 * so "no colour" here means "not rated", not "not enough data".
 */
export const INFORMATIONAL_GROUPS = new Set(['ELO', 'RFP', 'EO', 'SBA', 'CAA', 'CAST'])

/**
 * Why a result has no performance colour.
 *
 * Returns null when it has one.
 */
export function explainMissingColor(result: {
	color?: number | null
	accountabilityMet?: boolean
	smallDenominator?: boolean
	studentGroupCode?: string
	priorStatus?: string | number | null
}): string | null {
	if (result.color) return null
	if (result.studentGroupCode && INFORMATIONAL_GROUPS.has(result.studentGroupCode)) {
		return 'Reported for information only; the state does not rate this group.'
	}
	if (toNumber(result.priorStatus) === null) {
		return 'No colour: the state needs two years of data to assign one.'
	}
	if (result.accountabilityMet === false) {
		return 'Too few students for the state to assign a performance colour.'
	}
	return 'The state assigned no colour to this combination.'
}

export function enrollmentQuery(cds: string, year: number) {
	return report(
		dashboardReadEnrollmentOptions({ query: { cds, year } }),
		'Could not load enrolment.',
	)
}

export function growthQuery(cds: string, year: number, studentGroup: string) {
	return report(
		dashboardReadGrowthOptions({ query: { cds, year, studentGroup } }),
		'Could not load student growth.',
	)
}

/** The five Dashboard performance colours, in the state's own order. */
export const DASHBOARD_COLORS: Record<number, { name: string; token: string; text: string }> = {
	1: { name: 'Red', token: 'var(--color-cde-dashboard-red)', text: '#ffffff' },
	2: { name: 'Orange', token: 'var(--color-cde-dashboard-orange)', text: '#1a1a1a' },
	3: { name: 'Yellow', token: 'var(--color-cde-dashboard-yellow)', text: '#1a1a1a' },
	4: { name: 'Green', token: 'var(--color-cde-dashboard-green)', text: '#ffffff' },
	5: { name: 'Blue', token: 'var(--color-cde-dashboard-blue)', text: '#ffffff' },
}

/**
 * How a figure reads, given the indicator's direction.
 *
 * Chronic absenteeism and suspension are judged in reverse: falling is the
 * good outcome, so the arrow and the wording have to flip with them.
 *
 * The API sends every figure as a decimal string so no precision is lost in
 * transit, so these take the raw value and parse it here.
 */
export function describeChange(value: string | number | null | undefined, lowerIsBetter: boolean) {
	const change = toNumber(value)
	if (change === null) return { label: 'No prior year', direction: 'none' as const }
	if (change === 0) return { label: 'No change', direction: 'flat' as const }
	const rose = change > 0
	const good = lowerIsBetter ? !rose : rose
	return {
		label: `${rose ? 'Up' : 'Down'} ${Math.abs(change).toFixed(1)}`,
		direction: good ? ('good' as const) : ('bad' as const),
	}
}

/**
 * The background a change reads against.
 *
 * "Up" is the good outcome for five indicators and the bad one for the other
 * two, so direction cannot be left to the word alone — the same label means
 * opposite things on the suspension card and the graduation card. These are
 * this application's own tones rather than the five Dashboard hues, so a
 * rising figure is never mistaken for a performance colour.
 */
export const CHANGE_TONES = {
	good: 'bg-[var(--color-ca-dashboard-green)] text-white',
	bad: 'bg-[var(--color-ca-dashboard-red)] text-white',
	flat: 'bg-muted text-muted-foreground',
	none: 'bg-muted text-muted-foreground',
} as const

/** A school year the way the state writes it: 2025 is 2024–25. */
export function formatSchoolYear(year: number) {
	return `${year - 1}\u2013${String(year).slice(2)}`
}

/** Render a status figure in the unit its indicator is measured in. */
export function formatStatus(value: string | number | null | undefined, unit: string) {
	const parsed = toNumber(value)
	if (parsed === null) return '—'
	if (unit === 'percent') return `${parsed.toFixed(1)}%`
	if (unit === 'dfs') return `${parsed > 0 ? '+' : ''}${parsed.toFixed(1)}`
	return parsed.toFixed(1)
}
