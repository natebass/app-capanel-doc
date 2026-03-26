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
}

export default config
