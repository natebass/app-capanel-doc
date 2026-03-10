import { createFileRoute, useRouter } from '@tanstack/react-router'
import { ChevronLeft } from 'lucide-react'
import { Suspense, useCallback, useState } from 'react'
import { z } from 'zod'

import type { ColorKey } from '@/components/dashboard/card/IndicatorCard'
import { IndicatorDetailModal } from '@/components/dashboard/detail/IndicatorDetailModal'
import { IndicatorGrid, IndicatorGridSkeleton } from '@/components/dashboard/IndicatorGrid'
import NavbarD52 from '@/components/layout/navbar/NavbarD52'
import { Button } from '@/components/ui/button'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select'
import { STATEWIDE_CDS, type IndicatorCode } from '@/lib/constants/indicators'
import ScrollReset from '@/lib/hooks/ScrollReset'
import { useDashboardSummarySuspense } from '@/lib/hooks/useDashboardData'
import { useLastViewedSchool } from '@/lib/hooks/useLastViewedSchool'

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

	const [selectedIndicator, setSelectedIndicator] = useState<IndicatorCode | null>(null)
	const [selectedColor, setSelectedColor] = useState<ColorKey | null>(null)

	const handleIndicatorClick = useCallback((code: IndicatorCode) => {
		setSelectedIndicator(code)
		setSelectedColor(null)
	}, [])

	const handleColorClick = useCallback((code: IndicatorCode, color: ColorKey) => {
		setSelectedIndicator(code)
		setSelectedColor(color)
	}, [])

	const handleCloseModal = useCallback(() => {
		setSelectedIndicator(null)
		setSelectedColor(null)
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
						className={styles.backButton}
					>
						<ChevronLeft className='h-4 w-4' />
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
					<DashboardContent
						cds={effectiveCds}
						year={effectiveYear}
						selectedIndicator={selectedIndicator}
						selectedColor={selectedColor}
						onIndicatorClick={handleIndicatorClick}
						onColorClick={handleColorClick}
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
	selectedColor,
	onIndicatorClick,
	onColorClick,
	onCloseModal,
}: {
	cds: string
	year: ReportingYear
	selectedIndicator: IndicatorCode | null
	selectedColor: ColorKey | null
	onIndicatorClick: (code: IndicatorCode) => void
	onColorClick: (code: IndicatorCode, color: ColorKey) => void
	onCloseModal: () => void
}) {
	const { data } = useDashboardSummarySuspense(cds, year)
	const indicators = Array.isArray(data.indicators) ? data.indicators : []
	const reportingYear = data.reportingyear || year

	const entityName =
		data.schoolname ||
		data.districtname ||
		(cds === STATEWIDE_CDS ? 'California Statewide' : 'Unknown')

	const indicatorData = selectedIndicator
		? indicators.find((ind) => ind.indicator === selectedIndicator)
		: null

	return (
		<>
			<div className={styles.content}>
				<div className={styles.header}>
					<h1>{entityName}</h1>
					{data.countyname && cds !== STATEWIDE_CDS && (
						<p className={styles.subtitle}>
							{data.districtname && data.schoolname
								? `${data.districtname} | ${data.countyname}`
								: data.countyname}
						</p>
					)}
					<p className={styles.meta}>
						{reportingYear} California School Dashboard
						{data.charter_flag === 'Y' && ' | Charter School'}
					</p>
				</div>

				<div className={styles.gridSection}>
					<IndicatorGrid
						indicators={indicators}
						onIndicatorClick={onIndicatorClick}
						onColorClick={onColorClick}
						compact={true}
						cds={cds}
						reportingyear={year}
					/>
				</div>
			</div>

			<IndicatorDetailModal
				isOpen={!!selectedIndicator}
				onClose={onCloseModal}
				cds={cds}
				indicator={indicatorData || null}
				reportingyear={reportingYear}
				selectedColor={selectedColor}
			/>
		</>
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
			<div className={styles.gridSection}>
				<IndicatorGridSkeleton compact={true} />
			</div>
		</div>
	)
}
