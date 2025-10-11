
.DEFAULT_GOAL := storybook

storybook:
	cd frontend && pnpm i && pnpm run storybook

html:
	uv run scripts/html_task.py
