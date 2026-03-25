import { createFormHook } from '@tanstack/react-form'

import {
	fieldContext,
	formContext,
	Select,
	SubscribeButton,
	TextArea,
	TextField,
} from '@/components/form/demo-form'

export const { useAppForm } = createFormHook({
	fieldComponents: {
		TextField,
		Select,
		TextArea,
	},
	formComponents: {
		SubscribeButton,
	},
	fieldContext,
	formContext,
})
