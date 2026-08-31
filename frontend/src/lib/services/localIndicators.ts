/**
 * Query options for the LCFF Local Indicator API.
 *
 * This is the local half of the Dashboard, and it works nothing like the
 * state half in `accountability.ts`. There are no performance colours here —
 * only `Met`, `Not Met` or `Not Met For Two or More Years` — because nothing
 * on this side is measured by the state. Each local educational agency rates
 * itself and reports the result to its own governing board.
 */
import { queryOptions } from '@tanstack/react-query'

import {
	type LocalIndicatorCatalog,
	type LocalIndicatorDetail,
	type LocalIndicatorReport,
	type LocalIndicatorTrendReport,
	LocalIndicatorsService,
} from '@/lib/client'

export const STATEWIDE_CDS = '00000000000000'

/** Reference data changes only when new files are imported. */
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

export function localIndicatorCatalogQuery(year?: number) {
	return queryOptions({
		queryKey: ['local-indicators', 'catalog', year ?? 'latest'] as const,
		queryFn: async (): Promise<LocalIndicatorCatalog> =>
			unwrap(
				await LocalIndicatorsService.localIndicatorsReadCatalog({
					query: year ? { year } : {},
				}),
				'Could not load the local indicator catalogue.',
			),
		staleTime: REFERENCE_STALE_TIME,
	})
}

export function localIndicatorsQuery(cds: string, year: number) {
	return queryOptions({
		queryKey: ['local-indicators', 'report', cds, year] as const,
		queryFn: async (): Promise<LocalIndicatorReport> =>
			unwrap(
				await LocalIndicatorsService.localIndicatorsReadLocalIndicators({
					query: { cds, year },
				}),
				'Could not load the local indicators.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function localIndicatorDetailQuery(cds: string, year: number, priority: number) {
	return queryOptions({
		queryKey: ['local-indicators', 'priority', cds, year, priority] as const,
		queryFn: async (): Promise<LocalIndicatorDetail> =>
			unwrap(
				await LocalIndicatorsService.localIndicatorsReadPriority({
					query: { cds, year, priority },
				}),
				'Could not load that priority.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function localIndicatorTrendQuery(cds: string, priority: number) {
	return queryOptions({
		queryKey: ['local-indicators', 'trend', cds, priority] as const,
		queryFn: async (): Promise<LocalIndicatorTrendReport> =>
			unwrap(
				await LocalIndicatorsService.localIndicatorsReadTrend({
					query: { cds, priority },
				}),
				'Could not load the history for that priority.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

/**
 * How a `Met` / `Not Met` value should read.
 *
 * Deliberately not the Dashboard's five colours: this side of the Dashboard
 * has no performance colour, and borrowing the palette would imply the state
 * measured something it did not.
 */
export function performanceTone(
	performance: string | null | undefined,
): 'met' | 'notMet' | 'notMetTwoYears' | 'none' {
	switch (performance) {
		case 'Met':
			return 'met'
		case 'Not Met':
			return 'notMet'
		case 'Not Met For Two or More Years':
			return 'notMetTwoYears'
		default:
			return 'none'
	}
}

/** Turn a published column name into something a reader can scan. */
export function humanizeField(field: string): string {
	return field
		.replace(/^Narrative/, 'Narrative ')
		.replace(/([a-z])([A-Z])/g, '$1 $2')
		.replace(/\s+/g, ' ')
		.trim()
		.replace(/^./, (c) => c.toUpperCase())
}
