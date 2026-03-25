import { Suspense, useState } from 'react'
import { FiArrowDown, FiArrowUp, FiChevronDown, FiChevronRight, FiMinus } from 'react-icons/fi'

import { Gauge } from '@/components/gauge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog'
import type { IndicatorSummary } from '@/lib/client'
import { type IndicatorCode, INDICATORS, getIndicatorLabel } from '@/lib/constants/indicators'
import { useEquityReport } from '@/lib/hooks/useDashboardData'

import { EquityReport, EquityReportSkeleton } from './EquityReport'

export type ColorKey = 'red' | 'orange' | 'yellow' | 'green' | 'blue'

interface CollapsibleSectionProps {
	title: string
	defaultOpen?: boolean
	children: React.ReactNode
}

function CollapsibleSection({ title, defaultOpen = true, children }: CollapsibleSectionProps) {
	const [isOpen, setIsOpen] = useState(defaultOpen)

	return (
		<Collapsible open={isOpen} onOpenChange={setIsOpen}>
			<CollapsibleTrigger className='flex w-full items-center gap-2 rounded-lg p-2 text-left font-medium hover:bg-accent transition-colors'>
				{isOpen ? <FiChevronDown className='h-4 w-4' /> : <FiChevronRight className='h-4 w-4' />}
				{title}
			</CollapsibleTrigger>
			<CollapsibleContent className='px-2'>{children}</CollapsibleContent>
		</Collapsible>
	)
}

interface IndicatorDetailModalProps {
	isOpen: boolean
	onClose: () => void
	cds: string
	indicator: IndicatorSummary | null
	reportingyear: string
	selectedColor?: ColorKey | null
}

function formatStatus(value: number | null, indicator: string): string {
	if (value === null) return 'N/A'

	if (['CHRONIC', 'SUSP', 'GRAD', 'ELPI', 'CCI'].includes(indicator)) {
		return `${value.toFixed(1)}%`
	}

	return value.toFixed(1)
}

function ChangeDisplay({ change, indicator }: { change: number | null; indicator: string }) {
	if (change === null) {
		return (
			<div className='flex items-center gap-2 text-muted-foreground'>
				<FiMinus className='h-4 w-4' />
				<span>No change data available</span>
			</div>
		)
	}

	const config = INDICATORS[indicator as IndicatorCode]
	const isInverted = config?.invertedScale ?? false
	const isPositive = isInverted ? change < 0 : change > 0

	return (
		<div
			className={`flex items-center gap-2 ${
				isPositive ? 'text-green-600' : change === 0 ? 'text-muted-foreground' : 'text-red-600'
			}`}
		>
			{change > 0 ? (
				<FiArrowUp className='h-4 w-4' />
			) : change < 0 ? (
				<FiArrowDown className='h-4 w-4' />
			) : (
				<FiMinus className='h-4 w-4' />
			)}
			<span>
				{change > 0 ? '+' : ''}
				{change.toFixed(1)} from prior year
			</span>
		</div>
	)
}

function EquityReportContent({
	cds,
	indicator,
	reportingyear,
	filterColor,
}: {
	cds: string
	indicator: string
	reportingyear: string
	filterColor?: ColorKey | null
}) {
	const { data, isLoading, error } = useEquityReport(cds, indicator, reportingyear)

	if (isLoading) {
		return <EquityReportSkeleton />
	}

	if (error || !data) {
		return <div className='text-sm text-muted-foreground'>Unable to load equity report data.</div>
	}

	return (
		<EquityReport colorCounts={data.color_counts} groups={data.groups} filterColor={filterColor} />
	)
}

export function IndicatorDetailModal({
	isOpen,
	onClose,
	cds,
	indicator,
	reportingyear,
	selectedColor,
}: IndicatorDetailModalProps) {
	if (!indicator) {
		return null
	}

	const config = INDICATORS[indicator.indicator as IndicatorCode]
	const performanceLevel = (indicator.statuslevel ?? 0) as 0 | 1 | 2 | 3 | 4 | 5

	return (
		<Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
			<DialogContent className='sm:max-w-2xl max-h-[90vh] overflow-y-auto'>
				<DialogHeader>
					<DialogTitle>{getIndicatorLabel(indicator.indicator)}</DialogTitle>
					<DialogDescription>{config?.description}</DialogDescription>
				</DialogHeader>

				<div className='space-y-2'>
					<CollapsibleSection title='Performance Overview' defaultOpen={!selectedColor}>
						<div className='flex flex-col items-center gap-4 rounded-lg p-4 sm:flex-row sm:items-start'>
							<div className='flex-shrink-0'>
								<Gauge value={performanceLevel} size={160} />
							</div>

							<div className='flex-1 space-y-3'>
								<div>
									<p className='text-sm font-medium text-muted-foreground'>Current Status</p>
									<p className='text-2xl font-bold'>
										{formatStatus(indicator.currstatus ?? null, indicator.indicator)}
									</p>
								</div>

								<div>
									<p className='text-sm font-medium text-muted-foreground'>
										Change from Prior Year
									</p>
									<ChangeDisplay
										change={indicator.change ?? null}
										indicator={indicator.indicator}
									/>
								</div>

								{indicator.currdenom && (
									<div>
										<p className='text-sm font-medium text-muted-foreground'>Students</p>
										<p className='text-lg'>{indicator.currdenom.toLocaleString()}</p>
									</div>
								)}

								{indicator.priorstatus !== null && (
									<div>
										<p className='text-sm font-medium text-muted-foreground'>Prior Year Status</p>
										<p className='text-lg'>
											{formatStatus(indicator.priorstatus ?? null, indicator.indicator)}
										</p>
									</div>
								)}
							</div>
						</div>
					</CollapsibleSection>

					<CollapsibleSection title='Equity Report' defaultOpen={true}>
						<div className='py-2'>
							<Suspense fallback={<EquityReportSkeleton />}>
								<EquityReportContent
									cds={cds}
									indicator={indicator.indicator}
									reportingyear={reportingyear}
									filterColor={selectedColor}
								/>
							</Suspense>
						</div>
					</CollapsibleSection>
				</div>
			</DialogContent>
		</Dialog>
	)
}
