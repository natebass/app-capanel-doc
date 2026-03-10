declare module 'echarts' {
	export const init: (el: unknown) => {
		setOption: (option: unknown) => void
		resize: () => void
		dispose: () => void
	}
}
