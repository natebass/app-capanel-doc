import type { IndicatorSummary } from '@/lib/client'
import { INDICATOR_ORDER, type IndicatorCode } from '@/lib/constants/indicators'

import { IndicatorCard, IndicatorCardSkeleton, type ColorKey } from './card/IndicatorCard'

interface IndicatorGridProps {
	indicators: IndicatorSummary[]
	onIndicatorClick?: (code: IndicatorCode) => void
	onColorClick?: (code: IndicatorCode, color: ColorKey) => void
	compact?: boolean
	columns?: 1 | 2 | 4 | 5
	cds?: string
	reportingyear?: string
}

export function IndicatorGrid({
	indicators,
	onIndicatorClick,
	onColorClick,
	compact = false,
	columns = 5,
	cds,
	reportingyear,
}: IndicatorGridProps) {
	// Create a map for quick lookup
	const indicatorMap = new Map(indicators.map((ind) => [ind.indicator, ind]))

	// Sort indicators by the defined order
	const sortedIndicators = INDICATOR_ORDER.map((code) => {
		const ind = indicatorMap.get(code)
		if (ind) return ind
		// Return placeholder for missing indicators
		return {
			indicator: code,
			currstatus: null,
			priorstatus: null,
			change: null,
			statuslevel: null,
			changelevel: null,
			color: null,
			currdenom: null,
		}
	})

	const gridClasses = {
		1: 'grid-cols-1',
		2: 'grid-cols-1 sm:grid-cols-2',
		4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
		5: 'grid-cols-1 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5',
	}

	return (
		<div className={`font-figtree grid gap-4 ${gridClasses[columns]}`}>
			{sortedIndicators.map((ind) => (
				<IndicatorCard
					key={ind.indicator}
					indicator={ind}
					onClick={() => onIndicatorClick?.(ind.indicator as IndicatorCode)}
					onColorClick={(color) => onColorClick?.(ind.indicator as IndicatorCode, color)}
					compact={compact}
					cds={cds}
					reportingyear={reportingyear}
				/>
			))}
		</div>
	)
}

export function IndicatorGridSkeleton({
	compact = false,
	columns = 4,
	count = 8,
}: {
	compact?: boolean
	columns?: 1 | 2 | 4 | 5
	count?: number
}) {
	const gridClasses = {
		1: 'grid-cols-1',
		2: 'grid-cols-1 sm:grid-cols-2',
		4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
		5: 'grid-cols-1 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5',
	}

	return (
		<div className={`grid gap-4 ${gridClasses[columns]}`}>
			{Array.from({ length: count }).map((_, i) => (
				<IndicatorCardSkeleton key={i} compact={compact} />
			))}
		</div>
	)
}
