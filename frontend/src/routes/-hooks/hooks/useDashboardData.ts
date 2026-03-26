import { queryOptions, useQuery, useSuspenseQuery } from '@tanstack/react-query'

import {
	AcademicIndicatorsService,
	type DashboardAggregation,
	type DashboardSummaryResponse,
	type EquityReportResponse,
} from '../../../lib/client'

export type { DashboardSummaryResponse, EquityReportResponse }

export const DASHBOARD_QUERY_KEY = ['dashboard', 'data'] as const
export const DASHBOARD_SUMMARY_KEY = ['dashboard', 'summary'] as const
export const EQUITY_REPORT_KEY = ['dashboard', 'equity'] as const

function getApiErrorMessage(error: unknown, fallback: string) {
	if (error && typeof error === 'object') {
		const detail = (error as { detail?: unknown }).detail

		if (typeof detail === 'string' && detail.trim().length > 0) {
			return detail
		}

		if (Array.isArray(detail) && detail.length > 0) {
			const first = detail[0] as { msg?: string } | undefined
			if (first?.msg) {
				return first.msg
			}
		}
	}

	if (error instanceof Error && /failed to fetch|networkerror|load failed/i.test(error.message)) {
		return 'Cannot reach the API. Ensure the backend is reachable at /api.'
	}

	return fallback
}

// ===== Legacy single-indicator hooks =====

export function dashboardQueryOptions(cds: string | null) {
	return queryOptions({
		queryKey: [...DASHBOARD_QUERY_KEY, cds],
		queryFn: async (): Promise<DashboardAggregation> => {
			const response = await AcademicIndicatorsService.academicIndicatorsGetDashboardData({
				query: { q: cds! },
			})
			if (response.error) {
				throw new Error(getApiErrorMessage(response.error, 'Failed to fetch dashboard data'))
			}
			return response.data as DashboardAggregation
		},
		staleTime: 5 * 60 * 1000, // 5 minutes
		gcTime: 10 * 60 * 1000, // 10 minutes
		enabled: !!cds,
	})
}

export function useDashboardData(cds: string | null) {
	return useQuery(dashboardQueryOptions(cds))
}

export function useDashboardDataSuspense(cds: string) {
	return useSuspenseQuery(dashboardQueryOptions(cds))
}

// ===== New dashboard summary hooks (all indicators) =====

export function dashboardSummaryQueryOptions(
	cds: string | null,
	reportingyear: string = '2025',
	studentgroup: string = 'ALL',
) {
	return queryOptions({
		queryKey: [...DASHBOARD_SUMMARY_KEY, cds, reportingyear, studentgroup],
		queryFn: async (): Promise<DashboardSummaryResponse> => {
			const response = await AcademicIndicatorsService.academicIndicatorsGetDashboardSummary({
				query: { cds: cds!, reportingyear, studentgroup },
			})
			if (response.error) {
				throw new Error(getApiErrorMessage(response.error, 'Failed to fetch dashboard summary'))
			}
			return response.data as DashboardSummaryResponse
		},
		staleTime: 5 * 60 * 1000, // 5 minutes
		gcTime: 10 * 60 * 1000, // 10 minutes
		enabled: !!cds,
	})
}

export function useDashboardSummary(
	cds: string | null,
	reportingyear: string = '2025',
	studentgroup: string = 'ALL',
) {
	return useQuery(dashboardSummaryQueryOptions(cds, reportingyear, studentgroup))
}

export function useDashboardSummarySuspense(
	cds: string,
	reportingyear: string = '2025',
	studentgroup: string = 'ALL',
) {
	return useSuspenseQuery(dashboardSummaryQueryOptions(cds, reportingyear, studentgroup))
}

// ===== Equity report hooks =====

export function equityReportQueryOptions(
	cds: string | null,
	indicator: string | null,
	reportingyear: string = '2025',
) {
	return queryOptions({
		queryKey: [...EQUITY_REPORT_KEY, cds, indicator, reportingyear],
		queryFn: async (): Promise<EquityReportResponse> => {
			const response = await AcademicIndicatorsService.academicIndicatorsGetEquityReport({
				query: { cds: cds!, indicator: indicator!, reportingyear },
			})
			if (response.error) {
				throw new Error(getApiErrorMessage(response.error, 'Failed to fetch equity report'))
			}
			return response.data as EquityReportResponse
		},
		staleTime: 5 * 60 * 1000, // 5 minutes
		gcTime: 10 * 60 * 1000, // 10 minutes
		enabled: !!cds && !!indicator,
	})
}

export function useEquityReport(
	cds: string | null,
	indicator: string | null,
	reportingyear: string = '2025',
) {
	return useQuery(equityReportQueryOptions(cds, indicator, reportingyear))
}

export function useEquityReportSuspense(
	cds: string,
	indicator: string,
	reportingyear: string = '2025',
) {
	return useSuspenseQuery(equityReportQueryOptions(cds, indicator, reportingyear))
}
