/**
 * Query options for the CAASPP and ELPAC reporting API.
 *
 * Every report is keyed by the same five things the state's own reports are
 * keyed by — an entity, an administration year, a test, a student group and a
 * grade — so the query keys mirror that and cached results are shared between
 * views that ask the same question.
 */
import { queryOptions } from '@tanstack/react-query'

import {
	type Catalog,
	type ChildEntityReport,
	type CompareReport,
	EntitiesService,
	type EntityAncestry,
	type EntityList,
	type GradeReport,
	type OverviewReport,
	ReferenceService,
	ReportsService,
	type SchoolType,
	type StudentGroupReport,
	type SubscoreReport,
	type TrendReport,
} from '@/lib/client'

export const STATEWIDE_CDS = '00000000000000'
export const ALL_STUDENTS_GROUP = 1
export const ALL_GRADES = '13'

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

export function catalogQuery(year?: number) {
	return queryOptions({
		queryKey: ['catalog', year ?? 'latest'] as const,
		queryFn: async (): Promise<Catalog> =>
			unwrap(
				await ReferenceService.referenceReadCatalog({ query: year ? { year } : {} }),
				'Could not load the assessment catalogue.',
			),
		staleTime: REFERENCE_STALE_TIME,
	})
}

export function entitySearchQuery(q: string, level?: string, limit = 20) {
	return queryOptions({
		queryKey: ['entities', 'search', q, level ?? 'any', limit] as const,
		queryFn: async (): Promise<EntityList> =>
			unwrap(
				await EntitiesService.entitiesSearchEntities({
					query: { q, level: level as never, limit },
				}),
				'Could not search for schools and districts.',
			),
		staleTime: REFERENCE_STALE_TIME,
		enabled: q.trim().length >= 2,
	})
}

export function entityQuery(cdsCode: string) {
	return queryOptions({
		queryKey: ['entities', cdsCode] as const,
		queryFn: async (): Promise<EntityAncestry> =>
			unwrap(
				await EntitiesService.entitiesReadEntity({ path: { cds_code: cdsCode } }),
				'Could not load that school or district.',
			),
		staleTime: REFERENCE_STALE_TIME,
	})
}

export type ReportSelection = {
	cds: string
	year: number
	studentGroup: number
	grade: string
	schoolType: SchoolType
}

export function overviewQuery(selection: ReportSelection, compare = true) {
	return queryOptions({
		queryKey: ['reports', 'overview', selection, compare] as const,
		queryFn: async (): Promise<OverviewReport> =>
			unwrap(
				await ReportsService.reportsReadOverview({ query: { ...selection, compare } }),
				'Could not load results for this selection.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function subscoresQuery(selection: ReportSelection, testId: number) {
	return queryOptions({
		queryKey: ['reports', 'subscores', selection, testId] as const,
		queryFn: async (): Promise<SubscoreReport> =>
			unwrap(
				await ReportsService.reportsReadSubscores({
					query: {
						cds: selection.cds,
						year: selection.year,
						studentGroup: selection.studentGroup,
						grade: selection.grade,
						testId,
					},
				}),
				'Could not load the reporting categories.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function trendQuery(selection: ReportSelection, testId: number) {
	return queryOptions({
		queryKey: [
			'reports',
			'trend',
			selection.cds,
			selection.studentGroup,
			selection.grade,
			testId,
		] as const,
		queryFn: async (): Promise<TrendReport> =>
			unwrap(
				await ReportsService.reportsReadTrend({
					query: {
						cds: selection.cds,
						studentGroup: selection.studentGroup,
						grade: selection.grade,
						testId,
					},
				}),
				'Could not load results over time.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function studentGroupsQuery(selection: ReportSelection, testId: number) {
	return queryOptions({
		queryKey: [
			'reports',
			'studentGroups',
			selection.cds,
			selection.year,
			selection.grade,
			testId,
		] as const,
		queryFn: async (): Promise<StudentGroupReport> =>
			unwrap(
				await ReportsService.reportsReadStudentGroups({
					query: {
						cds: selection.cds,
						year: selection.year,
						grade: selection.grade,
						testId,
					},
				}),
				'Could not load results by student group.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function gradesQuery(selection: ReportSelection, testId: number) {
	return queryOptions({
		queryKey: [
			'reports',
			'grades',
			selection.cds,
			selection.year,
			selection.studentGroup,
			testId,
		] as const,
		queryFn: async (): Promise<GradeReport> =>
			unwrap(
				await ReportsService.reportsReadGrades({
					query: {
						cds: selection.cds,
						year: selection.year,
						studentGroup: selection.studentGroup,
						testId,
					},
				}),
				'Could not load results by grade.',
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function childResultsQuery(
	selection: ReportSelection,
	testId: number,
	options: { orderBy?: string; descending?: boolean; limit?: number } = {},
) {
	return queryOptions({
		queryKey: ['reports', 'children', selection, testId, options] as const,
		queryFn: async (): Promise<ChildEntityReport> =>
			unwrap(
				await ReportsService.reportsReadChildResults({
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
			),
		staleTime: REPORT_STALE_TIME,
	})
}

export function compareQuery(selection: ReportSelection, testId: number, cdsCodes: string[]) {
	return queryOptions({
		queryKey: ['reports', 'compare', cdsCodes, selection.year, selection.grade, testId] as const,
		queryFn: async (): Promise<CompareReport> =>
			unwrap(
				await ReportsService.reportsReadComparison({
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
		staleTime: REPORT_STALE_TIME,
		enabled: cdsCodes.length > 0,
	})
}
