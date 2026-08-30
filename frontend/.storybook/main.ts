import { fileURLToPath } from 'node:url'

import type { StorybookConfig } from '@storybook/react-vite'

const config: StorybookConfig = {
	stories: ['../src/**/*.mdx', '../src/**/*.stories.@(ts|tsx)'],

	addons: ['@storybook/addon-docs', '@storybook/addon-a11y', '@storybook/addon-vitest'],

	framework: {
		name: '@storybook/react-vite',
		options: {
			builder: {
				viteConfigPath: 'vite.config.ts',
			},
		},
	},

	// docs: {
	//   autodocs: 'tag',
	// },

	typescript: {
		reactDocgen: 'react-docgen-typescript',
		reactDocgenTypescriptOptions: {
			shouldExtractLiteralValuesFromEnum: true,
			shouldRemoveUndefinedFromOptional: true,
			propFilter: (prop) => (prop.parent ? !/node_modules/.test(prop.parent.fileName) : true),
		},
	},

	staticDirs: ['../public'],

	viteFinal: async (config) => {
		const sourceAlias = {
			find: '@',
			replacement: fileURLToPath(new URL('../src', import.meta.url)),
		}
		const aliases = config.resolve?.alias

		return {
			...config,
			resolve: {
				...config.resolve,
				alias: Array.isArray(aliases)
					? [...aliases, sourceAlias]
					: Object.assign({}, aliases, { '@': sourceAlias.replacement }),
			},
		}
	},
}

export default config
