/**
 * Wording for form fields, layered over the generated request schemas.
 *
 * Shapes and limits come from `zod.gen.ts`, so a field the API adds or a limit
 * it tightens reaches the forms on the next `pnpm run openapi-ts`. What a spec
 * cannot carry is what to tell a reader when a field is wrong, so the fields
 * that need their own sentence are restated here — and only those.
 *
 * The numbers below mirror the spec's own constraints. They are repeated rather
 * than derived because Zod attaches a message to a check, not to a field.
 */
import { z } from 'zod'

/** A password being set or entered. `UserCreate.password` is 8–128. */
export const password = z
	.string()
	.min(1, { error: 'Password is required' })
	.min(8, { error: 'Password must be at least 8 characters' })
	.max(128, { error: 'Password must be at most 128 characters' })

/** The second box, which the API never sees. */
export const passwordConfirmation = z
	.string()
	.min(1, { error: 'Password confirmation is required' })

/** An address the user types. `UserCreate.email` is an email of at most 255. */
export const email = z
	.email({ error: 'Invalid email address' })
	.max(255, { error: 'Email must be at most 255 characters' })

/** Cross-field rule shared by every form with a confirmation box. */
export const passwordsMatch = { error: "The passwords don't match", path: ['confirm_password'] }
