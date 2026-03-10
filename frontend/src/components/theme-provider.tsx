import { createContext, useContext, useEffect, useState } from 'react'

export type Theme = 'dark' | 'light' | 'system'

type ThemeProviderProps = {
	children: React.ReactNode
	defaultTheme?: Theme
	storageKey?: string
}

type ThemeProviderState = {
	theme: Theme
	resolvedTheme: Theme
	setTheme: (theme: Theme) => void
}

const initialState: ThemeProviderState = {
	theme: 'system',
	resolvedTheme: 'light',
	setTheme: () => null,
}

const ThemeProviderContext = createContext<ThemeProviderState>(initialState)

export function ThemeProvider({
	children,
	defaultTheme = 'system',
	storageKey = 'capanel-ui-theme-44d8',
	...props
}: ThemeProviderProps) {
	const [theme, setTheme] = useState<Theme>(
		() => (localStorage.getItem(storageKey) as Theme) || defaultTheme,
	)
	const [resolvedTheme, setResolvedTheme] = useState<Theme>(() => {
		if (theme !== 'system') return theme
		return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
	})

	useEffect(() => {
		const root = window.document.documentElement

		root.classList.remove('light', 'dark')

		if (theme === 'system') {
			const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
			const systemTheme = mediaQuery.matches ? 'dark' : 'light'

			root.classList.add(systemTheme)
			setResolvedTheme(systemTheme)

			const listener = (e: MediaQueryListEvent) => {
				const currentTheme = e.matches ? 'dark' : 'light'
				root.classList.remove('light', 'dark')
				root.classList.add(currentTheme)
				setResolvedTheme(currentTheme)
			}

			mediaQuery.addEventListener('change', listener)
			return () => mediaQuery.removeEventListener('change', listener)
		}

		root.classList.add(theme)
		setResolvedTheme(theme)
	}, [theme])

	const value = {
		theme,
		resolvedTheme,
		setTheme: (theme: Theme) => {
			localStorage.setItem(storageKey, theme)
			setTheme(theme)
		},
	}

	return (
		<ThemeProviderContext.Provider {...props} value={value}>
			{children}
		</ThemeProviderContext.Provider>
	)
}

export const useTheme = () => {
	const context = useContext(ThemeProviderContext)

	if (context === undefined) {
		throw new Error('useTheme must be used within a ThemeProvider')
	}

	return context
}
