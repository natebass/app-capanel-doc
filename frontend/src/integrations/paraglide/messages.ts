import { type Locale, getLocale } from './runtime'

export const m = {
	language_label: () => 'Language',
	current_locale: ({ locale }: { locale: Locale }) => `Current locale: ${locale}`,
	example_message: ({ username }: { username: string }) => `Hello ${username}`,
	learn_router: () => 'Learn Router',
}

export function t(key: keyof typeof m) {
	const locale = getLocale()
	if (locale === 'es' && key === 'learn_router') {
		return 'Aprender Router'
	}
	return m[key]
}
