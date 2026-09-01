import { copyFileSync, existsSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import { devtools } from '@tanstack/devtools-vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import react from '@vitejs/plugin-react'
import type { Plugin } from 'vite-plus'
import { defineConfig, lazyPlugins, loadEnv } from 'vite-plus'

const trimTrailingSlash = (value: string): string => value.replace(/\/+$/, '')

const normalizeApiBase = (value: string | undefined): string | undefined => {
	if (!value) return
	const trimmed = trimTrailingSlash(value.trim())
	if (!trimmed || trimmed === '/api' || trimmed === '/api/v1') return
	if (trimmed.endsWith('/api/v1')) return trimmed.slice(0, -7)
	if (trimmed.endsWith('/api')) return trimmed.slice(0, -4)
	return trimmed
}

/**
 * Resolve the public base path the built site is served from.
 *
 * Unset (or `/`) builds for a naked custom domain such as `https://example.org/`.
 * A path such as `app-capanel-web` builds for a GitHub Pages project site at
 * `https://opensacorg.github.io/app-capanel-web/`; leading and trailing slashes
 * are added when missing. A value beginning with `.` (such as `./`) is passed
 * through unchanged to produce fully relative asset URLs, which suits a site
 * whose final path is unknown at build time but breaks a hard reload of any
 * nested route, so prefer the explicit path whenever it is known.
 */
const normalizeBasePath = (value: string | undefined): string => {
	const trimmed = value?.trim()
	if (!trimmed || trimmed === '/') return '/'
	if (trimmed.startsWith('.')) return trimmed
	const withLeadingSlash = trimmed.startsWith('/') ? trimmed : `/${trimmed}`
	return withLeadingSlash.endsWith('/') ? withLeadingSlash : `${withLeadingSlash}/`
}

/**
 * Emit the extra files a static host needs to serve a single-page app.
 *
 * `404.html` is a copy of `index.html`: GitHub Pages serves it for any path it
 * has no file for, which hands deep links back to the client-side router
 * instead of showing the default GitHub 404 page. `.nojekyll` stops Pages from
 * running the output through Jekyll, which would drop files whose names begin
 * with an underscore. Both are inert on any other host.
 */
const staticHostFallback = (): Plugin => {
	let outDir = 'dist'
	return {
		name: 'static-host-spa-fallback',
		apply: 'build',
		configResolved(config) {
			outDir = resolve(config.root, config.build.outDir)
		},
		closeBundle() {
			const indexHtml = resolve(outDir, 'index.html')
			if (!existsSync(indexHtml)) return
			copyFileSync(indexHtml, resolve(outDir, '404.html'))
			writeFileSync(resolve(outDir, '.nojekyll'), '')
		},
	}
}

/**
 * The front end is deployed on its own, separately from the API: a static host
 * such as GitHub Pages or a CDN serves the build, and requests to `/api` reach
 * the FastAPI backend on another origin.
 *
 * Set `VITE_BASE_PATH` to the path the site is served from (see
 * `normalizeBasePath`), and `VITE_API_URL` to the public backend origin. The
 * dev server always uses a root base so Vite's React refresh runtime loads on
 * routed URLs, and proxies API traffic to the local backend instead.
 */
const config = defineConfig(({ command, mode }) => {
	const env = loadEnv(mode, process.cwd(), '')
	const apiTarget =
		env.VITE_DEV_PROXY_TARGET || normalizeApiBase(env.VITE_API_URL) || 'http://localhost:8000'
	const basePath = normalizeBasePath(env.VITE_BASE_PATH)

	return {
		fmt: {
			// Formatting options (from biome formatter + javascript.formatter)
			useTabs: true,
			singleQuote: true,
			jsxSingleQuote: true,
			semi: false,
			// Ignore patterns (from biome files.includes negations)
			ignorePatterns: [
				'**/src/routeTree.gen.ts',
				'**/src/styles.css',
				'**/dist/**/*',
				'**/node_modules/**/*',
				'**/src/client/**/*',
				'**/playwright-report',
				'**/playwright.config.ts',
			],
			// Import sorting (from biome assist.actions.source.organizeImports)
			experimentalSortImports: {},
		},
		lint: {
			plugins: [
				'eslint',
				'react',
				'unicorn',
				'typescript',
				'oxc',
				'import',
				'jsdoc',
				'jest',
				'vitest',
				'jsx-a11y',
				'react-perf',
				'promise',
			],
			ignorePatterns: [
				'**/src/routeTree.gen.ts',
				'**/src/styles.css',
				'**/dist/**/*',
				'**/node_modules/**/*',
				'**/src/client/**/*',
				'**/src/lib/client/**/*',
				'**/playwright-report',
				'**/playwright.config.ts',
			],
			categories: {
				correctness: 'warn',
			},
			rules: {
				'eslint/no-unused-vars': 'error',
				'typescript/no-explicit-any': 'off',
				'react/no-array-index-key': 'off',
				'typescript/no-non-null-assertion': 'off',
				'eslint/no-param-reassign': 'error',
				'react/self-closing-comp': 'error',
				'eslint/no-else-return': 'error',
				'vite-plus/prefer-vite-plus-imports': 'error',
			},
			options: {
				typeAware: true,
				typeCheck: true,
			},
			jsPlugins: [
				{
					name: 'vite-plus',
					specifier: 'vite-plus/oxlint-plugin',
				},
			],
		},
		base: command === 'serve' ? '/' : basePath,
		build: {
			outDir: 'dist',
		},
		resolve: {
			tsconfigPaths: true,
			alias: {
				'@': fileURLToPath(new URL('./src', import.meta.url)),
			},
		},
		server: {
			proxy: {
				'/api': {
					target: apiTarget,
					changeOrigin: true,
				},
				'/docs': {
					target: apiTarget,
					changeOrigin: true,
				},
				'/redoc': {
					target: apiTarget,
					changeOrigin: true,
				},
			},
		},
		plugins: lazyPlugins(() => [
			staticHostFallback(),
			devtools(),
			tailwindcss(),
			tanstackRouter({ target: 'react', autoCodeSplitting: true }),
			react({
				// @ts-expect-error This is the official solution from the website.
				babel: {
					plugins: ['babel-plugin-react-compiler'],
				},
			}),
		]),
	}
})

export default config
