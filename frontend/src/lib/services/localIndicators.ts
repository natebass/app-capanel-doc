/**
 * Query options for the LCFF Local Indicator API.
 *
 * This is the local half of the Dashboard, and it works nothing like the
 * state half in `accountability.ts`. There are no performance colours here —
 * only `Met`, `Not Met` or `Not Met For Two or More Years` — because nothing
 * on this side is measured by the state. Each local educational agency rates
 * itself and reports the result to its own governing board.
 */
import {
	localIndicatorsReadCatalogOptions,
	localIndicatorsReadLocalIndicatorsOptions,
	localIndicatorsReadPriorityOptions,
	localIndicatorsReadTrendOptions,
} from '@/lib/client'
import { reference, report } from '@/lib/services/query'

export const STATEWIDE_CDS = '00000000000000'

export function localIndicatorCatalogQuery(year?: number) {
	return reference(
		localIndicatorsReadCatalogOptions({ query: year ? { year } : {} }),
		'Could not load the local indicator catalogue.',
	)
}

export function localIndicatorsQuery(cds: string, year: number) {
	return report(
		localIndicatorsReadLocalIndicatorsOptions({ query: { cds, year } }),
		'Could not load the local indicators.',
	)
}

export function localIndicatorDetailQuery(cds: string, year: number, priority: number) {
	return report(
		localIndicatorsReadPriorityOptions({ query: { cds, year, priority } }),
		'Could not load that priority.',
	)
}

export function localIndicatorTrendQuery(cds: string, priority: number) {
	return report(
		localIndicatorsReadTrendOptions({ query: { cds, priority } }),
		'Could not load the history for that priority.',
	)
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
