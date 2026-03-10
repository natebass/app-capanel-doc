import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
	input: './openapi.json',
	output: './src/lib/client',
	plugins: [
		'@hey-api/typescript',
		{
			name: '@hey-api/sdk',
			operations: {
				strategy: 'byTags',
				containerName: '{{name}}Service',
				nesting: 'operationId',
			},
		},
		{
			name: '@hey-api/schemas',
			type: 'json',
		},
	],
})
