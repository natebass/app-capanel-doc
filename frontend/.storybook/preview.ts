import type { Preview } from '@storybook/react-vite'

// @ts-ignore
import '../src/globals.css'

const preview: Preview = {
	parameters: {
		controls: {
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i,
			},
		},

		a11y: {
			test: 'todo',
		},
		options: {
			storySort: {
				order: ['Getting started', 'Chakra UI cards', 'layout', ['Navigation bar', '*'], 'UI', '*'],
			},
		},
	},
}

export default preview
