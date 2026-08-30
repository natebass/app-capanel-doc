import type { Meta, StoryObj } from '@storybook/react'

import componentsConfig from '../../components.json?raw'
import openapiTsConfig from '../../openapi-ts.config.ts?raw'
import playwrightConfig from '../../playwright.config.ts?raw'
import tsConfig from '../../tsconfig.json?raw'
import viteConfig from '../../vite.config.ts?raw'
import vitestConfig from '../../vitest.config.ts?raw'

const viteConfigComments =
	viteConfig.match(/\/\*[\s\S]*?\*\/|\/\/.*/g)?.join('\n\n') ?? 'No comments found.'
const tsConfigComments =
	tsConfig.match(/\/\*[\s\S]*?\*\/|\/\/.*/g)?.join('\n\n') ?? 'No comments found.'
const playwrightConfigComments =
	playwrightConfig.match(/\/\*[\s\S]*?\*\/|\/\/.*/g)?.join('\n\n') ?? 'No comments found.'
const shadcnComponentsConfigComments =
	componentsConfig.match(/\/\*[\s\S]*?\*\/|\/\/.*/g)?.join('\n\n') ?? 'No comments found.'
const openapiTsConfigComments =
	openapiTsConfig.match(/\/\*[\s\S]*?\*\/|\/\/.*/g)?.join('\n\n') ?? 'No comments found.'
const vitestConfigComments =
	vitestConfig.match(/\/\*[\s\S]*?\*\/|\/\/.*/g)?.join('\n\n') ?? 'No comments found.'

const meta = {
	title: 'Project configuration files',
	parameters: {
		layout: 'centered',
	},
} satisfies Meta

export default meta

type Story = StoryObj<typeof meta>

export const ViteConfig: Story = {
	name: 'vite.config.ts',
	render: () => (
		<div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
			<h1 style={{ fontFamily: 'sans-serif' }}>Vite Config Documentation</h1>
			<pre
				style={{
					background: '#1e1e1e',
					color: '#d4d4d4',
					padding: '1.5rem',
					borderRadius: '8px',
					whiteSpace: 'pre-wrap',
					fontSize: '14px',
				}}
			>
				<code>{viteConfigComments}</code>
			</pre>
		</div>
	),
}

export const TSConfig: Story = {
	name: 'tsconfig.json',
	render: () => (
		<div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
			<h1 style={{ fontFamily: 'sans-serif' }}>TypeScript Config Documentation</h1>
			<pre
				style={{
					background: '#1e1e1e',
					color: '#d4d4d4',
					padding: '1.5rem',
					borderRadius: '8px',
					whiteSpace: 'pre-wrap',
					fontSize: '14px',
				}}
			>
				<code>{tsConfigComments}</code>
			</pre>
		</div>
	),
}

export const PlaywrightConfig: Story = {
	name: 'playwright.config.ts',
	render: () => (
		<div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
			<h1 style={{ fontFamily: 'sans-serif' }}>TypeScript Config Documentation</h1>
			<pre
				style={{
					background: '#1e1e1e',
					color: '#d4d4d4',
					padding: '1.5rem',
					borderRadius: '8px',
					whiteSpace: 'pre-wrap',
					fontSize: '14px',
				}}
			>
				<code>{playwrightConfigComments}</code>
			</pre>
		</div>
	),
}

export const VitestConfig: Story = {
	name: 'vitest.config.ts',
	render: () => (
		<div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
			<h1 style={{ fontFamily: 'sans-serif' }}>TypeScript Config Documentation</h1>
			<pre
				style={{
					background: '#1e1e1e',
					color: '#d4d4d4',
					padding: '1.5rem',
					borderRadius: '8px',
					whiteSpace: 'pre-wrap',
					fontSize: '14px',
				}}
			>
				<code>{vitestConfigComments}</code>
			</pre>
		</div>
	),
}

export const ShadcnComponentsConfig: Story = {
	name: 'components.json',
	render: () => (
		<div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
			<h1 style={{ fontFamily: 'sans-serif' }}>TypeScript Config Documentation</h1>
			<pre
				style={{
					background: '#1e1e1e',
					color: '#d4d4d4',
					padding: '1.5rem',
					borderRadius: '8px',
					whiteSpace: 'pre-wrap',
					fontSize: '14px',
				}}
			>
				<code>{shadcnComponentsConfigComments}</code>
			</pre>
		</div>
	),
}

export const OpenAPIConfig: Story = {
	name: 'openapi-ts.config.json',
	render: () => (
		<div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
			<h1 style={{ fontFamily: 'sans-serif' }}>TypeScript Config Documentation</h1>
			<pre
				style={{
					background: '#1e1e1e',
					color: '#d4d4d4',
					padding: '1.5rem',
					borderRadius: '8px',
					whiteSpace: 'pre-wrap',
					fontSize: '14px',
				}}
			>
				<code>{openapiTsConfigComments}</code>
			</pre>
		</div>
	),
}
