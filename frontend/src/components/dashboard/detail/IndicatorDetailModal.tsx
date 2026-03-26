import { Suspense } from 'react'

import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog'
import type { IndicatorSummary } from '@/lib/client'
import { useEquityReport } from '@/routes/-hooks/hooks/useDashboardData'

import { EquityReport, EquityReportSkeleton } from './EquityReport'

interface IndicatorDetailModalProps {
	isOpen: boolean
	onClose: () => void
	cds: string
	indicator: IndicatorSummary | null
	testYear: string
}

function EquityReportContent({
	cds,
	testId,
	testYear,
}: {
	cds: string
	testId: string
	testYear: string
}) {
	const { data, isLoading, error } = useEquityReport(cds, testId, testYear)

	if (isLoading) {
		return <EquityReportSkeleton />
	}

	if (error || !data) {
		return <div className='text-sm text-muted-foreground'>Unable to load student group data.</div>
	}

	return <EquityReport groups={data.groups} />
}

export function IndicatorDetailModal({
	isOpen,
	onClose,
	cds,
	indicator,
	testYear,
}: IndicatorDetailModalProps) {
	if (!indicator) {
		return null
	}

	return (
		<Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
			<DialogContent className='sm:max-w-xl max-h-[90vh] overflow-y-auto'>
				<DialogHeader>
					<DialogTitle>Test Detail: {indicator.test_id}</DialogTitle>
					<DialogDescription>
						{indicator.test_type} | Grade {indicator.grade}
					</DialogDescription>
				</DialogHeader>

				<div className='space-y-6 pt-4'>
					<div className='grid grid-cols-2 gap-4'>
						<div className='rounded-lg bg-muted/30 p-4'>
							<p className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
								Standard Met or Exceeded
							</p>
							<p className='text-2xl font-bold mt-1'>{indicator.overall_met_and_above_pct}%</p>
						</div>
						<div className='rounded-lg bg-muted/30 p-4'>
							<p className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
								Mean Scale Score
							</p>
							<p className='text-2xl font-bold mt-1'>{indicator.overall_mean_scale_score}</p>
						</div>
						<div className='rounded-lg bg-muted/30 p-4'>
							<p className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
								Students Enrolled
							</p>
							<p className='text-xl font-semibold mt-1'>{indicator.students_enrolled}</p>
						</div>
						<div className='rounded-lg bg-muted/30 p-4'>
							<p className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
								Students Tested
							</p>
							<p className='text-xl font-semibold mt-1'>{indicator.students_tested}</p>
						</div>
					</div>

					<div className='space-y-4'>
						<h4 className='text-sm font-semibold border-b pb-2'>Student Group Breakdown</h4>
						<Suspense fallback={<EquityReportSkeleton />}>
							<EquityReportContent cds={cds} testId={indicator.test_id} testYear={testYear} />
						</Suspense>
					</div>
				</div>
			</DialogContent>
		</Dialog>
	)
}
