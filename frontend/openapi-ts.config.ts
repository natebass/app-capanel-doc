import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
	input: './openapi.json',
	output: './src/lib/client',
	plugins: [
		'@hey-api/typescript',
		{
			name: 'zod',
			exportFromIndex: true,
		},
		{
			name: '@hey-api/sdk',
			operations: {
				strategy: 'byTags',
				containerName: '{{name}}Service',
				nesting: 'operationId',
			},
			validator: true,
		},
		{
			name: '@tanstack/react-query',
			queryOptions: true,
			mutationOptions: true,
			infiniteQueryOptions: true,
			exportFromIndex: true,
		},
	],
})
