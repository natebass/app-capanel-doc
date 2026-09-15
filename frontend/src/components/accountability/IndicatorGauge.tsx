/**
 * The state's own gauge, at card size.
 *
 * The Dashboard reports a performance level as a five-colour dial with a
 * needle in it, and that is the picture readers arrive already knowing. A
 * coloured band along the top of a card said the same thing in a vocabulary
 * only this site used.
 *
 * Every level is one static SVG, all drawn to the same scale, so a card can
 * swap one for another — or for the unrated dial it shows while it waits —
 * without the layout moving. That is the whole reason the unrated one is a
 * reframed copy rather than the original: see `public/gauge-0.svg`.
 */
import { assetUrl } from '@/lib/utils'

const LEVEL_NAME: Record<number, string> = {
	1: 'Red',
	2: 'Orange',
	3: 'Yellow',
	4: 'Green',
	5: 'Blue',
}

/**
 * The dial with no needle: every colour, no reading.
 *
 * It stands for two things that amount to the same claim — a level the state
 * has not assigned (a first year of data, too few students, a group reported
 * for information) and a level this browser has not fetched yet.
 */
export const UNRATED_GAUGE = '/gauge-0.svg'

export function gaugeUrl(color?: number | null) {
	return assetUrl(color && LEVEL_NAME[color] ? `/gauge-${color}.svg` : UNRATED_GAUGE)
}

/** Sized once, here, so the card and its placeholder cannot drift apart. */
export const GAUGE_BOX = 'mx-auto w-28 max-w-full'

export function IndicatorGauge({
	color,
	className,
}: {
	color?: number | null
	className?: string
}) {
	const level = color ? LEVEL_NAME[color] : undefined

	return (
		<img
			src={gaugeUrl(color)}
			alt={level ? `Performance level: ${level}` : 'No performance level'}
			className={`${GAUGE_BOX} ${className ?? ''}`}
			// The unrated dial is a statement of absence, so it reads back a
			// step: present, but never mistakable for a rating.
			style={{ opacity: level ? 1 : 0.4 }}
		/>
	)
}
