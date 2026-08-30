/**
 * Shared helpers for rendering assessment results.
 *
 * The API returns every distribution already labelled with the state's own
 * wording, so nothing here decides what a level *means*; these functions only
 * decide how it looks and how it reads.
 */
import type { LevelResult } from '@/lib/client'

/**
 * Colour for one level of an ordered scale.
 *
 * Schemes have three or four levels; a three-level scale skips the third stop
 * so its top level stays the darkest, and the ramp reads the same way in both.
 */
export function levelColor(levelNumber: number, levelCount: number): string {
	const stop = levelCount >= 4 ? levelNumber : ([1, 2, 4][levelNumber - 1] ?? 4)
	return `var(--achievement-${Math.min(Math.max(stop, 1), 4)})`
}

/** Percentages arrive as decimal strings so no precision is lost in transit. */
export function toNumber(value: string | number | null | undefined): number | null {
	if (value === null || value === undefined || value === '') return null
	const parsed = typeof value === 'number' ? value : Number(value)
	return Number.isFinite(parsed) ? parsed : null
}

export function formatPercent(value: string | number | null | undefined, digits = 1): string {
	const parsed = toNumber(value)
	return parsed === null ? '—' : `${parsed.toFixed(digits)}%`
}

export function formatCount(value: number | null | undefined): string {
	return value === null || value === undefined ? '—' : value.toLocaleString()
}

export function formatScore(value: string | number | null | undefined): string {
	const parsed = toNumber(value)
	return parsed === null ? '—' : parsed.toFixed(1)
}

/** True when at least one level in a distribution carries a percentage. */
export function hasDistribution(levels: readonly LevelResult[]): boolean {
	return levels.some((level) => toNumber(level.pct) !== null)
}

/**
 * Why a figure is missing.
 *
 * The state withholds results for groups of fewer than eleven students, and
 * separately publishes nothing where a figure does not apply — a mean scale
 * score across grades, for instance, which is not a comparable quantity.
 */
export function missingReason(suppressed: boolean): string {
	return suppressed
		? 'Withheld: fewer than 11 students were tested, so the state does not publish results for this group.'
		: 'Not reported for this selection.'
}
