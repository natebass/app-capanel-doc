/**
 * How long a load has been running, in the terms a reader cares about.
 *
 * A request that answers in under a second needs no explanation; the skeleton
 * is the explanation. Past a few seconds the silence starts to read as a bug,
 * and past ten it reads as a broken page — so the wait is graded, and the page
 * can say more the longer it goes on.
 *
 * The long case here is not a slow network. These endpoints read the state's
 * Dashboard files, and the first request after an import pays for the whole
 * dataset; every request after it is quick. That is worth telling a reader,
 * because "this happens once" and "this site is slow" are different messages.
 *
 * React Query does not record when a fetch began — `dataUpdatedAt` is set when
 * it ends — so the wait is timed here, from the edge where fetching starts.
 */
import { useEffect, useState } from 'react'

/**
 * `waiting` — under the threshold, or not loading at all.
 * `slow` — long enough that a reader wants to know something is happening.
 * `cold` — long enough to be the first read of a new dataset.
 */
export type LoadStage = 'waiting' | 'slow' | 'cold'

export const SLOW_AFTER_MS = 2_500
export const COLD_AFTER_MS = 8_000

/**
 * Grade an in-flight load by how long it has been running.
 *
 * Takes a single boolean rather than the queries themselves, so several
 * unrelated queries can be graded as the one wait a reader actually
 * experiences. Pass `isFetching` rather than `isPending` so a background
 * refetch over stale data is graded too: on the accountability report that
 * refetch is the recache, which is the case most worth explaining.
 *
 * Re-renders only at the two thresholds.
 */
export function useSlowLoad(
	loading: boolean,
	{ slowAfterMs = SLOW_AFTER_MS, coldAfterMs = COLD_AFTER_MS } = {},
): LoadStage {
	const [stage, setStage] = useState<LoadStage>('waiting')
	const [wasLoading, setWasLoading] = useState(loading)

	// A new run starts ungraded. Adjusted during the render that observes the
	// edge rather than in an effect, so a load that begins and ends inside one
	// render cannot leave the previous run's grade behind it.
	if (loading !== wasLoading) {
		setWasLoading(loading)
		setStage('waiting')
	}

	// The thresholds are a timer, which is what an effect is for. They are torn
	// down with the run they belong to.
	useEffect(() => {
		if (!loading) return
		const timers = [
			setTimeout(() => setStage('slow'), slowAfterMs),
			setTimeout(() => setStage('cold'), coldAfterMs),
		]
		return () => timers.forEach(clearTimeout)
	}, [loading, slowAfterMs, coldAfterMs])

	return loading ? stage : 'waiting'
}

/**
 * Seconds elapsed, ticking once a second while `active`.
 *
 * Kept apart from {@link useSlowLoad} so the ticking re-renders only the small
 * component showing the number, rather than the page around it.
 *
 * `offsetMs` is what had already elapsed when counting began — a caller that
 * starts counting at a threshold passes that threshold, so the first number
 * shown is the true age of the wait and not zero.
 */
export function useElapsedSeconds(active: boolean, offsetMs = 0): number {
	const [seconds, setSeconds] = useState(Math.floor(offsetMs / 1000))
	const [wasActive, setWasActive] = useState(active)

	if (active !== wasActive) {
		setWasActive(active)
		setSeconds(Math.floor(offsetMs / 1000))
	}

	useEffect(() => {
		if (!active) return
		// Read inside the effect: the clock is an external system, and reading
		// it during render would make the render impure.
		const from = Date.now() - offsetMs
		const timer = setInterval(
			() => setSeconds(Math.max(0, Math.floor((Date.now() - from) / 1000))),
			1000,
		)
		return () => clearInterval(timer)
	}, [active, offsetMs])

	return active ? seconds : 0
}
