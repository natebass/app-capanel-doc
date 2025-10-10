
.DEFAULT_GOAL := storybook

storybook:
	cd frontend && pnpm i && pnpm run storybook

