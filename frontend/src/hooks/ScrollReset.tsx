import { useRouterState } from '@tanstack/react-router';
import { useEffect } from 'react';

export default function ScrollReset({ selector }: { selector?: string } = {}) {
	const location = useRouterState({ select: (s) => s.location });

	useEffect(() => {
		if (typeof window === 'undefined') return;

		// Disable browser’s automatic restoration (back/forward, bfcache)
		if ('scrollRestoration' in window.history) {
			window.history.scrollRestoration = 'manual';
		}

		// Respect in-page anchors; skip resetting when navigating to a hash
		if (location.hash) return;

		const el = selector
			? (document.querySelector(selector) as HTMLElement | null)
			: null;

		const scroll = () => {
			if (el) el.scrollTo({ top: 0, left: 0, behavior: 'auto' });
			else window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
		};

		// Run after the new route paints
		requestAnimationFrame(scroll);
	}, [location.hash, selector]);

	return null;
}
