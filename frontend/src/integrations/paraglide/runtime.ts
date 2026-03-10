export const locales = ['en', 'es'] as const

export type Locale = (typeof locales)[number]

const LOCALE_STORAGE_KEY = 'locale'

export function getLocale(): Locale {
	if (typeof window === 'undefined') {
		return 'en'
	}
	const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY)
	return stored === 'es' ? 'es' : 'en'
}

export function setLocale(locale: Locale) {
	if (typeof window !== 'undefined') {
		window.localStorage.setItem(LOCALE_STORAGE_KEY, locale)
	}
}
