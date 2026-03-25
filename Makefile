
.DEFAULT_GOAL := html
.PHONY: help docs-deps clean preview Makefile frontend backend

html:
	make -C backend/docs html

preview:
	make -C backend/docs preview

reload:
	make -C backend/docs reload

storybook:
	cd frontend && pnpm i && pnpm run storybook

frontend:
	cd frontend && pnpm i && pnpm run dev

backend:
	cd backend && uv sync && uv run fastapi dev

