import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import { devtools } from '@tanstack/devtools-vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv, lazyPlugins } from 'vite-plus'

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
 * base: './' is required for relative paths in single-container deployment
 * Add a delay to allow the Nitro server to boot in the container. This prevents the "fetch failed" immediately upon starting.
 * Keep relative assets for production container builds, but use root base in dev so Vite's React refresh runtime is loaded correctly on routed URLs.
 */
const config = defineConfig(({ command, mode }) => {
	const env = loadEnv(mode, process.cwd(), '')
	const apiTarget =
		env.VITE_DEV_PROXY_TARGET || normalizeApiBase(env.VITE_API_URL) || 'http://localhost:8000'

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
		base: command === 'serve' ? '/' : './',
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
				'/docs/oauth2-redirect': {
					target: apiTarget,
					changeOrigin: true,
				},
				'/redoc': {
					target: apiTarget,
					changeOrigin: true,
				},
				'/openapi.json': {
					target: apiTarget,
					changeOrigin: true,
				},
			},
		},
		plugins: lazyPlugins(() => [
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
