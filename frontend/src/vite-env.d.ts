/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly VITE_API_URL?: string
	readonly VITE_API_BASE_URL?: string
	/** Path the built site is served from, e.g. `/app-capanel-web/`. Defaults to `/`. */
	readonly VITE_BASE_PATH?: string
	readonly VITE_DEV_PROXY_TARGET?: string
}

interface ImportMeta {
	readonly env: ImportMetaEnv
}
