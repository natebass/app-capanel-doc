
.DEFAULT_GOAL := storybook

storybook:
	cd frontend && pnpm i && pnpm run storybook

html:
	make -C backend/docs html

preview:
	make -C backend/docs preview

reload:
	make -C backend/docs reload
