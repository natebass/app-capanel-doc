import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs))
}

/**
 * Build a URL for a file in `public/`, honouring the deployment base path.
 *
 * Absolute paths such as `/gauge-1.svg` only resolve when the site is served
 * from the domain root. Prefixing them with Vite's `BASE_URL` keeps them
 * correct under a GitHub Pages project path as well, and leaves them unchanged
 * for a naked custom domain.
 *
 * @param path Path to the file relative to `public/`, with or without a leading slash.
 */
export function assetUrl(path: string): string {
	return `${import.meta.env.BASE_URL.replace(/\/+$/, '')}/${path.replace(/^\/+/, '')}`
}
