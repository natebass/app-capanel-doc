function extractErrorMessage(err: unknown): string {
	if (err instanceof Error) {
		return err.message
	}

	const errDetail =
		(err as { detail?: unknown; body?: { detail?: unknown } })?.body?.detail ??
		(err as { detail?: unknown })?.detail
	if (Array.isArray(errDetail) && errDetail.length > 0) {
		const first = errDetail[0] as { msg?: string }
		return first.msg ?? 'Something went wrong.'
	}
	return typeof errDetail === 'string' ? errDetail : 'Something went wrong.'
}

export const handleError = function (this: (msg: string) => void, err: unknown) {
	const errorMessage = extractErrorMessage(err)
	this(errorMessage)
}

export const getInitials = (name: string): string => {
	return name
		.split(' ')
		.slice(0, 2)
		.map((word) => word[0])
		.join('')
		.toUpperCase()
}
