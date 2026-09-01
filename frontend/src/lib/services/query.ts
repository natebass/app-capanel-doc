/**
 * Shared plumbing for the generated query options.
 *
 * `@hey-api/openapi-ts` generates a `*Options()` function per operation, which
 * covers the query key and the fetch. Two things it cannot know are layered on
 * top here: how long a particular kind of answer stays fresh, and what to tell
 * a reader when the request fails.
 */
import type { QueryKey, UseQueryOptions } from '@tanstack/react-query'

/** Reference data changes only when new files are imported. */
export const REFERENCE_STALE_TIME = 30 * 60 * 1000
export const REPORT_STALE_TIME = 5 * 60 * 1000

/**
 * The generated query function rethrows whatever the API put in the response
 * body. Components render `error.message`, so turn that body into a real Error,
 * preferring the API's own `detail` over the caller's fallback sentence.
 */
function asError(error: unknown, fallback: string): Error {
	if (error instanceof Error && error.message) return error
	const detail = (error as { detail?: unknown } | null | undefined)?.detail
	if (typeof detail === 'string' && detail.trim()) return new Error(detail)
	return new Error(fallback)
}

type QueryFn = (context: never) => Promise<unknown>

/**
 * Attach a staleness window and a failure message to generated query options.
 *
 * The error type narrows to `Error` on the way out, because everything the
 * wrapped query function throws has been through `asError` by then.
 */
export function described<TData, TError, TQueryKey extends QueryKey>(
	options: UseQueryOptions<TData, TError, TData, TQueryKey>,
	fallback: string,
	staleTime: number,
): UseQueryOptions<TData, Error, TData, TQueryKey> {
	const queryFn = options.queryFn as QueryFn
	return {
		...options,
		staleTime,
		queryFn: async (context: never) => {
			try {
				return (await queryFn(context)) as TData
			} catch (error) {
				throw asError(error, fallback)
			}
		},
		// `options` still carries retry/throwOnError typed against the API's own
		// error shape; the wrapper above is what makes `Error` true at runtime.
	} as UseQueryOptions<TData, Error, TData, TQueryKey>
}

/** Reference data: catalogues, entity lookups, anything import-scoped. */
export function reference<TData, TError, TQueryKey extends QueryKey>(
	options: UseQueryOptions<TData, TError, TData, TQueryKey>,
	fallback: string,
) {
	return described(options, fallback, REFERENCE_STALE_TIME)
}

/** Published results: the report endpoints. */
export function report<TData, TError, TQueryKey extends QueryKey>(
	options: UseQueryOptions<TData, TError, TData, TQueryKey>,
	fallback: string,
) {
	return described(options, fallback, REPORT_STALE_TIME)
}
