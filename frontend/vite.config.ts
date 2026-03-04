import { fileURLToPath, URL } from 'node:url'

import { storybookTest } from '@storybook/addon-vitest/vitest-plugin'
import tailwindcss from '@tailwindcss/vite'
import { devtools } from '@tanstack/devtools-vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import viteTsConfigPaths from 'vite-tsconfig-paths'

const apiTarget = process.env.VITE_API_URL || 'http://localhost:9000'

/**
 * base: './' is required for relative paths in single-container deployment
 * Add a delay to allow the Nitro server to boot in the container. This prevents the "fetch failed" immediately upon starting
 * Keep relative assets for production container builds, but use root base
 * in dev so Vite's React refresh runtime is loaded correctly on routed URLs.
 * The plugin will run tests for the stories defined in your Storybook config
 * See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
 */
const config = defineConfig(({ command }) => ({
	plugins: [
		devtools(),
		viteTsConfigPaths({
			projects: ['./tsconfig.json'],
		}),
		tailwindcss(),
		tanstackRouter({ target: 'react', autoCodeSplitting: true }),
		react({
			babel: {
				plugins: ['babel-plugin-react-compiler'],
			},
		}),
	],
	resolve: {
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
	base: command === 'serve' ? '/' : './',
	build: {
		outDir: 'dist',
	},
	test: {
		projects: [
			{
				extends: true,
				plugins: [
					storybookTest({
						configDir: fileURLToPath(new URL('./.storybook', import.meta.url)),
					}),
				],
				test: {
					name: 'storybook',
					browser: {
						enabled: true,
						headless: true,
						provider: 'playwright',
						instances: [
							{
								browser: 'chromium',
							},
						],
					},
					setupFiles: ['.storybook/vitest.setup.ts'],
				},
			},
		],
	},
}))

export default config
