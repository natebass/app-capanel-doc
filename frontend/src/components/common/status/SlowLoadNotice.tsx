/**
 * What a long wait means, said while the reader is still waiting.
 *
 * A skeleton answers "something is coming". It does not answer "why is this
 * taking fifteen seconds", and a reader who is not told will assume the site
 * is broken rather than that it is reading a dataset for the first time.
 *
 * So the notice is graded with the wait. Under a few seconds it says nothing.
 * Past that it is a quiet line: the page is working. Past eight seconds it
 * becomes a real explanation, because at that point the reader has decided
 * something is wrong and needs telling otherwise.
 *
 * `aria-live='polite'` rather than an alert: this interrupts nothing, it just
 * needs to reach a reader who cannot see the skeletons move.
 */
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { COLD_AFTER_MS, type LoadStage, useElapsedSeconds } from '@/hooks/useSlowLoad'

export function SlowLoadNotice({
	stage,
	subject = 'this report',
}: {
	stage: LoadStage
	/** What is being read, in a sentence: "the first read of <subject>". */
	subject?: string
}) {
	// Counting begins at the threshold, so the threshold is what had already
	// elapsed by then — otherwise an eight-second wait would announce itself
	// as zero seconds old.
	const seconds = useElapsedSeconds(stage === 'cold', COLD_AFTER_MS)

	if (stage === 'waiting') return null

	if (stage === 'slow') {
		return (
			<div
				aria-live='polite'
				className='flex items-center gap-2 text-sm text-muted-foreground'
				data-slot='slow-load-notice'
			>
				{/* A div, not a paragraph: the pulsing dot beside it is one too, and
				    a block element inside a <p> is invalid and gets reparented. */}
				<Skeleton className='size-3 shrink-0 rounded-full' aria-hidden />
				Still loading {subject}&hellip;
			</div>
		)
	}

	return (
		<Alert aria-live='polite' data-slot='slow-load-notice'>
			<AlertTitle>Loading a new dataset</AlertTitle>
			<AlertDescription>
				This is the first read of {subject} since the state&rsquo;s files were last imported, so the
				whole dataset is being assembled. It takes about fifteen seconds and happens once — the next
				visit is quick. Everything already known is on the page below.
				{seconds > 0 ? (
					<span className='block pt-1 tabular-nums text-muted-foreground'>{seconds}s elapsed</span>
				) : null}
			</AlertDescription>
		</Alert>
	)
}
