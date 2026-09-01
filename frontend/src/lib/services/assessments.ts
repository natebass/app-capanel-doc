/**
 * Query options for the CAASPP and ELPAC reporting API.
 *
 * Every report is keyed by the same five things the state's own reports are
 * keyed by — an entity, an administration year, a test, a student group and a
 * grade — so the query keys mirror that and cached results are shared between
 * views that ask the same question. The keys themselves come from the generated
 * options; what this module adds is the mapping from that domain selection onto
 * each endpoint's parameters.
 */
import {
	entitiesReadEntityOptions,
	entitiesSearchEntitiesOptions,
	referenceReadCatalogOptions,
	reportsReadChildResultsOptions,
	reportsReadComparisonOptions,
	reportsReadGradesOptions,
	reportsReadOverviewOptions,
	reportsReadStudentGroupsOptions,
	reportsReadSubscoresOptions,
	reportsReadTrendOptions,
	type SchoolType,
} from '@/lib/client'
import { reference, report } from '@/lib/services/query'

export const STATEWIDE_CDS = '00000000000000'
export const ALL_STUDENTS_GROUP = 1
export const ALL_GRADES = '13'

export function catalogQuery(year?: number) {
	return reference(
		referenceReadCatalogOptions({ query: year ? { year } : {} }),
		'Could not load the assessment catalogue.',
	)
}

export function entitySearchQuery(q: string, level?: string, limit = 20) {
	return {
		...reference(
			entitiesSearchEntitiesOptions({ query: { q, level: level as never, limit } }),
			'Could not search for schools and districts.',
		),
		enabled: q.trim().length >= 2,
	}
}

export function entityQuery(cdsCode: string) {
	return reference(
		entitiesReadEntityOptions({ path: { cds_code: cdsCode } }),
		'Could not load that school or district.',
	)
}

export type ReportSelection = {
	cds: string
	year: number
	studentGroup: number
	grade: string
	schoolType: SchoolType
}

export function overviewQuery(selection: ReportSelection, compare = true) {
	return report(
		reportsReadOverviewOptions({ query: { ...selection, compare } }),
		'Could not load results for this selection.',
	)
}

export function subscoresQuery(selection: ReportSelection, testId: number) {
	return report(
		reportsReadSubscoresOptions({
			query: {
				cds: selection.cds,
				year: selection.year,
				studentGroup: selection.studentGroup,
				grade: selection.grade,
				testId,
			},
		}),
		'Could not load the reporting categories.',
	)
}

export function trendQuery(selection: ReportSelection, testId: number) {
	return report(
		reportsReadTrendOptions({
			query: {
				cds: selection.cds,
				studentGroup: selection.studentGroup,
				grade: selection.grade,
				testId,
			},
		}),
		'Could not load results over time.',
	)
}

export function studentGroupsQuery(selection: ReportSelection, testId: number) {
	return report(
		reportsReadStudentGroupsOptions({
			query: {
				cds: selection.cds,
				year: selection.year,
				grade: selection.grade,
				testId,
			},
		}),
		'Could not load results by student group.',
	)
}

export function gradesQuery(selection: ReportSelection, testId: number) {
	return report(
		reportsReadGradesOptions({
			query: {
				cds: selection.cds,
				year: selection.year,
				studentGroup: selection.studentGroup,
				testId,
			},
		}),
		'Could not load results by grade.',
	)
}

export function childResultsQuery(
	selection: ReportSelection,
	testId: number,
	options: { orderBy?: string; descending?: boolean; limit?: number } = {},
) {
	return report(
		reportsReadChildResultsOptions({
			query: {
				cds: selection.cds,
				year: selection.year,
				studentGroup: selection.studentGroup,
				grade: selection.grade,
				schoolType: selection.schoolType,
				testId,
				orderBy: options.orderBy ?? 'met_or_above_pct',
				descending: options.descending ?? true,
				limit: options.limit ?? 25,
			},
		}),
		'Could not load results for the schools and districts inside this one.',
	)
}

export function compareQuery(selection: ReportSelection, testId: number, cdsCodes: string[]) {
	return {
		...report(
			reportsReadComparisonOptions({
				query: {
					cdsCodes: cdsCodes.join(','),
					year: selection.year,
					studentGroup: selection.studentGroup,
					grade: selection.grade,
					testId,
				},
			}),
			'Could not compare these schools and districts.',
		),
		enabled: cdsCodes.length > 0,
	}
}
