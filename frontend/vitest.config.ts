import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { storybookTest } from '@storybook/addon-vitest/vitest-plugin'
import { defineConfig } from 'vite-plus'
import { playwright } from 'vite-plus/test/browser-playwright'

const dirname =
	typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url))

/**
 * The plugin will run tests for the stories defined in your Storybook config.
 * See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
 */
export default defineConfig({
	build: {
		rollupOptions: {
			onwarn(warning: any, warn: any) {
				if (warning.code === 'MODULE_LEVEL_DIRECTIVE' && warning.message.includes('"use client"')) {
					return
				}
				warn(warning)
			},
		},
	},
	test: {
		projects: [
			{
				extends: true,
				plugins: [
					storybookTest({
						configDir: path.join(dirname, '.storybook'),
					}),
				],
				test: {
					name: 'storybook',
					browser: {
						enabled: true,
						headless: true,
						provider: playwright({}),
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
})
