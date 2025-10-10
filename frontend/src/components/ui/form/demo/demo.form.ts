import { createFormHook } from '@tanstack/react-form';
import { SubscribeButton } from '../../button/SubscribeButton';
import { Select, TextArea, TextField } from '../demo.FormComponents';
import { fieldContext, formContext } from './demo.form-context.ts';

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
});
