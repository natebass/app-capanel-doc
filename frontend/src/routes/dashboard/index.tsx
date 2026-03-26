import { ArrowLeft01Icon, BookOpen01Icon, Calculator01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, useRouter } from '@tanstack/react-router'
import { Suspense, useCallback, useState } from 'react'
import { z } from 'zod'

import NavbarD52 from '@/components/common/navbar/navbar-D52'
import { IndicatorDetailModal } from '@/components/dashboard/detail/IndicatorDetailModal'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select'
import type { IndicatorSummary } from '@/lib/client'
import { STATEWIDE_CDS } from '@/lib/constants/indicators'
import ScrollReset from '@/routes/-hooks/hooks/ScrollReset'
import { useDashboardSummarySuspense } from '@/routes/-hooks/hooks/useDashboardData'
import { useLastViewedSchool } from '@/routes/-hooks/hooks/useLastViewedSchool'

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

export const Route = createFileRoute('/dashboard/')({
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
						className={styles.backButton}
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
							<SelectTrigger className={styles.yearSelectTrigger}>
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
					<DashboardContent cds={effectiveCds} year={effectiveYear} />
				</Suspense>
			</div>
		</div>
	)
}

function getTestName(testId: string) {
	if (testId === '1') return { name: 'English Language Arts', icon: BookOpen01Icon }
	if (testId === '2') return { name: 'Mathematics', icon: Calculator01Icon }
	if (testId === '3' || testId === '4') return { name: 'Science (CAST)', icon: BookOpen01Icon }
	return { name: `Test ${testId}`, icon: BookOpen01Icon }
}

function DashboardContent({ cds, year }: { cds: string; year: ReportingYear }) {
	const { data } = useDashboardSummarySuspense(cds, year)
	const indicators = Array.isArray(data.indicators) ? data.indicators : []
	const reportingYear = data.test_year || year
	const [selectedIndicator, setSelectedIndicator] = useState<IndicatorSummary | null>(null)

	const entityName = cds === STATEWIDE_CDS ? 'California Statewide' : 'Dashboard'

	return (
		<div className={styles.content}>
			<div className={styles.header}>
				<h1>{entityName}</h1>
				<p className={styles.meta}>{reportingYear} CAASPP Test Results</p>
			</div>

			<div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3 mt-6'>
				{indicators.length === 0 ? (
					<div className='col-span-full py-12 text-center text-muted-foreground bg-muted/20 rounded-lg border border-dashed'>
						No CAASPP test data available for this selection.
					</div>
				) : (
					indicators.map((ind, i) => {
						const testInfo = getTestName(ind.test_id || '')
						const percentMet = ind.overall_met_and_above_pct
							? parseFloat(ind.overall_met_and_above_pct)
							: 0

						return (
							<Card
								key={`${ind.test_id}-${i}`}
								className='overflow-hidden border shadow-sm transition-all hover:shadow-md cursor-pointer hover:border-primary/50'
								onClick={() => setSelectedIndicator(ind)}
							>
								<CardHeader className='bg-muted/30 pb-4 border-b'>
									<CardTitle className='flex items-center gap-2 text-lg'>
										<div className='p-2 bg-primary/10 rounded-md text-primary'>
											<HugeiconsIcon icon={testInfo.icon} className='h-5 w-5' />
										</div>
										{testInfo.name}
									</CardTitle>
									<CardDescription>
										Grade: {ind.grade === '13' ? 'All Grades' : ind.grade}
									</CardDescription>
								</CardHeader>
								<CardContent className='pt-6'>
									<div className='flex flex-col gap-6'>
										<div className='flex justify-between items-end'>
											<div>
												<p className='text-sm font-medium text-muted-foreground mb-1'>
													Standard Met or Exceeded
												</p>
												<div className='flex items-baseline gap-1'>
													<span className='text-4xl font-bold tracking-tight text-foreground'>
														{ind.overall_met_and_above_pct || '--'}%
													</span>
												</div>
											</div>
										</div>

										<div className='w-full bg-secondary h-3 rounded-full overflow-hidden'>
											<div
												className='bg-primary h-full transition-all duration-500 ease-in-out'
												style={{ width: `${percentMet}%` }}
											/>
										</div>

										<div className='grid grid-cols-2 gap-4 pt-4 border-t'>
											<div>
												<p className='text-xs font-medium text-muted-foreground'>
													Mean Scale Score
												</p>
												<p className='text-lg font-semibold'>
													{ind.overall_mean_scale_score || '--'}
												</p>
											</div>
											<div>
												<p className='text-xs font-medium text-muted-foreground'>Students Tested</p>
												<p className='text-lg font-semibold'>{ind.students_tested || '--'}</p>
											</div>
										</div>
									</div>
								</CardContent>
							</Card>
						)
					})
				)}
			</div>

			<IndicatorDetailModal
				isOpen={!!selectedIndicator}
				onClose={() => setSelectedIndicator(null)}
				cds={cds}
				indicator={selectedIndicator}
				testYear={reportingYear}
			/>
		</div>
	)
}

function DashboardSkeleton() {
	return (
		<div className={styles.content}>
			<div className={styles.header}>
				<div className={styles.skeleton} style={{ height: 32, width: 256 }} />
				<div className={styles.skeleton} style={{ height: 16, width: 192, marginTop: 8 }} />
				<div className={styles.skeleton} style={{ height: 16, width: 224, marginTop: 4 }} />
			</div>
			<div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3 mt-6'>
				{[1, 2, 3].map((i) => (
					<div
						key={i}
						className='h-[280px] rounded-xl bg-card border shadow-sm p-6 flex flex-col gap-4'
					>
						<div className={styles.skeleton} style={{ height: 28, width: 180 }} />
						<div className={styles.skeleton} style={{ height: 16, width: 100 }} />
						<div className='mt-auto flex flex-col gap-4'>
							<div className={styles.skeleton} style={{ height: 40, width: 80 }} />
							<div
								className={styles.skeleton}
								style={{ height: 12, width: '100%', borderRadius: 999 }}
							/>
							<div className='flex justify-between mt-4'>
								<div className={styles.skeleton} style={{ height: 32, width: 60 }} />
								<div className={styles.skeleton} style={{ height: 32, width: 60 }} />
							</div>
						</div>
					</div>
				))}
			</div>
		</div>
	)
}
