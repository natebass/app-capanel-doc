/**
 * Query options for the California School Dashboard accountability API.
 *
 * This is a different publication from the assessment reports in
 * `assessments.ts`: those say what students scored, these say how the state
 * judged a school. The two use different student-group vocabularies — short
 * codes like `SED` here, numeric CAASPP ids there — so their query keys are
 * kept separate rather than sharing a cache.
 */
import { queryOptions } from '@tanstack/react-query'

import {
	type ChildIndicatorReport,
	type GrowthReport,
	type DashboardCatalog,
	DashboardService,
	type IndicatorGroupReport,
	type IndicatorReport,
	type IndicatorTrendReport,
} from '@/lib/client'
import { toNumber } from '@/lib/results'

export const STATEWIDE_CDS = '00000000000000'
export const ALL_STUDENTS = 'ALL'

/** Reference data changes only when new indicator files are imported. */
const REFERENCE_STALE_TIME = 30 * 60 * 1000
const REPORT_STALE_TIME = 5 * 60 * 1000

function unwrap<T>(response: { data?: T; error?: unknown }, fallback: string): T {
	if (response.error) {
		const detail = (response.error as { detail?: unknown }).detail
		if (typeof detail === 'string' && detail.trim()) throw new Error(detail)
		throw new Error(fallback)
	}
	return response.data as T
}

export type AccountabilitySelection = {
	cds: string
	year: number
	studentGroup: string
}

export function dashboardCatalogQuery(year?: number) {
	return queryOptions({
		queryKey: ['accountability', 'catalog', year ?? 'latest'] as const,
		queryFn: async (): Promise<DashboardCatalog> =>
			unwrap(
				await DashboardService.dashboardReadCatalog({ query: year ? { year } : {} }),
				'Could not load the accountability catalogue.',
			),
		staleTime: REFERENCE_STALE_TIME,
	})
}

export function indicatorsQuery(selection: AccountabilitySelection) {
	return queryOptions({
		queryKey: [
			'accountability',
			'indicators',
			selection.cds,
			selection.year,
			selection.studentGroup,
		] as const,
		queryFn: async (): Promise<IndicatorReport> =>
			unwrap(
				await DashboardService.dashboardReadIndicators({
					query: {
						cds: selection.cds,
						year: selection.year,
						studentGroup: selection.studentGroup,
					},
				}),
				'Could not load the accountability indicators.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function indicatorGroupsQuery(selection: AccountabilitySelection, indicator: string) {
	return queryOptions({
		queryKey: ['accountability', 'groups', selection.cds, selection.year, indicator] as const,
		queryFn: async (): Promise<IndicatorGroupReport> =>
			unwrap(
				await DashboardService.dashboardReadIndicator({
					query: { cds: selection.cds, year: selection.year, indicator },
				}),
				'Could not load the student group breakdown.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function indicatorTrendQuery(selection: AccountabilitySelection, indicator: string) {
	return queryOptions({
		queryKey: [
			'accountability',
			'trend',
			selection.cds,
			indicator,
			selection.studentGroup,
		] as const,
		queryFn: async (): Promise<IndicatorTrendReport> =>
			unwrap(
				await DashboardService.dashboardReadTrend({
					query: {
						cds: selection.cds,
						indicator,
						studentGroup: selection.studentGroup,
					},
				}),
				'Could not load the history for that indicator.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function indicatorChildrenQuery(
	selection: AccountabilitySelection,
	indicator: string,
	options: { descending?: boolean; limit?: number } = {},
) {
	const { descending = true, limit = 50 } = options
	return queryOptions({
		queryKey: [
			'accountability',
			'children',
			selection.cds,
			selection.year,
			indicator,
			selection.studentGroup,
			descending,
			limit,
		] as const,
		queryFn: async (): Promise<ChildIndicatorReport> =>
			unwrap(
				await DashboardService.dashboardReadChildren({
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
			),
		staleTime: REPORT_STALE_TIME,
	})
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

export function growthQuery(cds: string, year: number, studentGroup: string) {
	return queryOptions({
		queryKey: ['accountability', 'growth', cds, year, studentGroup] as const,
		queryFn: async (): Promise<GrowthReport> =>
			unwrap(
				await DashboardService.dashboardReadGrowth({
					query: { cds, year, studentGroup },
				}),
				'Could not load student growth.',
			),
		staleTime: REPORT_STALE_TIME,
	})
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

/** Render a status figure in the unit its indicator is measured in. */
export function formatStatus(value: string | number | null | undefined, unit: string) {
	const parsed = toNumber(value)
	if (parsed === null) return '—'
	if (unit === 'percent') return `${parsed.toFixed(1)}%`
	if (unit === 'dfs') return `${parsed > 0 ? '+' : ''}${parsed.toFixed(1)}`
	return parsed.toFixed(1)
}
