import { ArrowLeft01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, useRouter } from '@tanstack/react-router'
import { Suspense, useCallback, useState } from 'react'
import { z } from 'zod'

import { useLastViewedSchool } from '@/lib/hooks/useLastViewedSchool'
import { IndicatorDetailModal } from '@/components/dashboard/detail/IndicatorDetailModal'
import type { IndicatorSummary } from '@/lib/client'
import NavbarD52 from '@/components/layout/navbar/NavbarD52'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select'
import { STATEWIDE_CDS } from '@/lib/constants/indicators'
import ScrollReset from '@/lib/hooks/ScrollReset'
import { useDashboardSummarySuspense } from '@/lib/hooks/useDashboardData'

import styles from './index.module.css'

const AVAILABLE_YEARS = ['2025', '2024'] as const
type ReportingYear = (typeof AVAILABLE_YEARS)[number]

const searchSchema = z.object({
	q: z.coerce.string().optional(),
	year: z.coerce
		.string()
		.optional()
		.transform((val) => {
			if (val === '2024' || val === '2025') return val
			return undefined
		}),
})

export const Route = createFileRoute('/report/')({
	component: DashboardPage,
	validateSearch: searchSchema,
})

function DashboardPage() {
	const { q, year: urlYear } = Route.useSearch()
	const navigate = Route.useNavigate()
	const router = useRouter()
	const { cds: lastViewedCds } = useLastViewedSchool()

	const effectiveCds = q || lastViewedCds || STATEWIDE_CDS
	const effectiveYear: ReportingYear = urlYear || '2025'

	const [selectedIndicator, setSelectedIndicator] = useState<IndicatorSummary | null>(null)

	const handleCloseModal = useCallback(() => {
		setSelectedIndicator(null)
	}, [])

	const handleYearChange = useCallback(
		(year: ReportingYear) => {
			if (year === effectiveYear) return
			navigate({ search: (prev) => ({ ...prev, year }) })
		},
		[effectiveYear, navigate],
	)

	return (
		<div className={styles.page}>
			<ScrollReset />
			<NavbarD52 shadow />
			<div className={styles.container}>
				<div className={styles.topBar}>
					<Button
						variant='outline'
						size='sm'
						onClick={() => router.history.back()}
						className='gap-1 bg-white hover:bg-gray-100'
					>
						<HugeiconsIcon icon={ArrowLeft01Icon} className='h-4 w-4' />
						Go back
					</Button>
					<div className={styles.yearSelector}>
						<span className={styles.yearLabel}>Reporting Year:</span>
						<Select
							value={effectiveYear}
							onValueChange={(val) => handleYearChange(val as ReportingYear)}
						>
							<SelectTrigger className='w-30 bg-white'>
								<SelectValue />
							</SelectTrigger>
							<SelectContent>
								{AVAILABLE_YEARS.map((year) => (
									<SelectItem key={year} value={year}>
										{year}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					</div>
				</div>

				<Suspense fallback={<DashboardSkeleton />}>
					<DashboardContent
						cds={effectiveCds}
						year={effectiveYear}
						selectedIndicator={selectedIndicator}
						onIndicatorClick={setSelectedIndicator}
						onCloseModal={handleCloseModal}
					/>
				</Suspense>
			</div>
		</div>
	)
}

function DashboardContent({
	cds,
	year,
	selectedIndicator,
	onIndicatorClick,
	onCloseModal,
}: {
	cds: string
	year: ReportingYear
	selectedIndicator: IndicatorSummary | null
	onIndicatorClick: (ind: IndicatorSummary) => void
	onCloseModal: () => void
}) {
	const { data } = useDashboardSummarySuspense(cds, year)
	const indicators = Array.isArray(data.indicators) ? data.indicators : []
	const reportingYear = data.test_year || year

	const entityName = cds === STATEWIDE_CDS ? 'California Statewide' : 'Dashboard'

	return (
		<>
			<div className={styles.content}>
				<div className={styles.header}>
					<h1>{entityName}</h1>
					<p className={styles.meta}>
						{reportingYear} CAASPP Test Results
					</p>
				</div>

				<div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3 mt-6'>
					{indicators.length === 0 ? (
						<div className='col-span-full py-12 text-center text-muted-foreground bg-muted/20 rounded-lg border border-dashed'>
							No CAASPP test data available for this selection.
						</div>
					) : (
						indicators.map((ind, i) => {
							const percentMet = ind.overall_met_and_above_pct ? parseFloat(ind.overall_met_and_above_pct) : 0
							return (
								<Card
									key={`${ind.test_id}-${i}`}
									className='overflow-hidden border shadow-sm transition-all hover:shadow-md cursor-pointer hover:border-primary/50'
									onClick={() => onIndicatorClick(ind)}
								>
									<CardHeader className='bg-muted/30 pb-4 border-b'>
										<CardTitle className='text-lg'>{ind.test_id}</CardTitle>
										<CardDescription>Grade {ind.grade}</CardDescription>
									</CardHeader>
									<CardContent className='pt-6'>
										<div className='flex flex-col gap-4'>
											<div className='flex justify-between items-end'>
												<div>
													<p className='text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1'>Standard Met or Exceeded</p>
													<p className='text-3xl font-bold'>{ind.overall_met_and_above_pct}%</p>
												</div>
											</div>
											<div className='w-full bg-secondary h-2 rounded-full overflow-hidden'>
												<div className='bg-primary h-full transition-all' style={{ width: `${percentMet}%` }} />
											</div>
										</div>
									</CardContent>
								</Card>
							)
						})
					)}
				</div>
			</div>

			<IndicatorDetailModal
				isOpen={!!selectedIndicator}
				onClose={onCloseModal}
				cds={cds}
				indicator={selectedIndicator}
				testYear={reportingYear}
			/>
		</>
	)
}

function DashboardSkeleton() {
	return (
		<div className={styles.content}>
			<div className={styles.header}>
				<div className={styles.skeleton} style={{ height: 32, width: 256 }} />
				<div className={styles.skeleton} style={{ height: 16, width: 224, marginTop: 12 }} />
			</div>
			<div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3 mt-6'>
				{[1, 2, 3].map((i) => (
					<div key={i} className='h-[200px] rounded-xl bg-card border shadow-sm p-6 flex flex-col gap-4 animate-pulse' />
				))}
			</div>
		</div>
	)
}
