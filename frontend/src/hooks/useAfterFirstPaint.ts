/**
 * False until the browser has painted once, true afterwards.
 *
 * React commits a whole tree in one pass, so everything rendered in the first
 * pass is paid for before anything at all appears. On a report whose loading
 * state draws its real structure that is a bad trade below the fold: the
 * student group table alone is around half the nodes on the page, and nobody
 * can see it at the moment it is delaying the header and the filters that they
 * can see.
 *
 * So the heavy off-screen placeholders wait one frame. They still appear
 * essentially instantly — a frame is about sixteen milliseconds, and they are
 * scrolled out of view when it passes — but they are no longer in front of the
 * first paint.
 *
 * Two frames rather than one: the first callback runs before the paint being
 * waited on, the second after it.
 *
 * A timer races the frames because a hidden tab never paints — browsers stop
 * serving `requestAnimationFrame` there — and content that waits for a frame
 * that never comes is content that is missing rather than deferred. Whichever
 * arrives first wins; in a visible tab that is always the frames.
 */
import { useEffect, useState } from 'react'

/** Long enough to clear a 60Hz frame, short enough to go unnoticed. */
const FALLBACK_MS = 32

export function useAfterFirstPaint(): boolean {
	const [painted, setPainted] = useState(false)

	useEffect(() => {
		let second = 0
		const first = requestAnimationFrame(() => {
			second = requestAnimationFrame(() => setPainted(true))
		})
		const fallback = setTimeout(() => setPainted(true), FALLBACK_MS)
		return () => {
			cancelAnimationFrame(first)
			cancelAnimationFrame(second)
			clearTimeout(fallback)
		}
	}, [])

	return painted
}
