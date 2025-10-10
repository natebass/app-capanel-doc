import { useForm } from '@tanstack/react-form';
import * as React from 'react';
import './SearchBar.css';
import { redirect } from '@tanstack/react-router';

const previewResults = [
	{
		category: 'Recent',
		items: [
			{ id: 1, label: 'A' },
			{ id: 2, label: 'Bob' },
		],
	},
];

export default function SearchBar({ className }: { className?: string }) {
	const [showDropdown, setShowDropdown] = React.useState(false);
	const [query, setQuery] = React.useState('');

	const form = useForm({
		defaultValues: { search: '' },
		onSubmit: ({ value }) => {
			redirect({ to: '/dashboard', search: { q: value.search } });
		},
	});

	// Filter preview results by query
	const filteredResults = React.useMemo(() => {
		if (!query) return previewResults;
		return previewResults
			.map((cat) => ({
				...cat,
				items: cat.items.filter((item) =>
					item.label.toLowerCase().includes(query.toLowerCase()),
				),
			}))
			.filter((cat) => cat.items.length > 0);
	}, [query]);

	return (
		<div className={`searchbar-root ${className}`}>
			<form
				onSubmit={form.handleSubmit}
				autoComplete='off'
				className='searchbar-form'
			>
				<input
					name='search'
					value={form.state.values.search}
					onChange={(e) => {
						form.setFieldValue('search', e.target.value);
						setQuery(e.target.value);
						setShowDropdown(true);
					}}
					onFocus={() => {
						setShowDropdown(true);
					}}
					onBlur={() => setTimeout(() => setShowDropdown(false), 150)}
					placeholder='Search...'
					className='searchbar-input'
				/>
			</form>
			{showDropdown && filteredResults.length > 0 && (
				<div className='searchbar-dropdown'>
					{filteredResults.map((cat) => (
						<div key={cat.category} className='searchbar-category-block'>
							<div className='searchbar-category-heading'>{cat.category}</div>
							{cat.items.map((item) => (
								<button
									key={item.id}
									type='button'
									className='searchbar-result-item'
									onMouseDown={(e) => e.preventDefault()}
									onClick={() => {
										form.setFieldValue('search', item.label);
										setShowDropdown(false);
										form.handleSubmit();
									}}
								>
									{item.label}
								</button>
							))}
						</div>
					))}
				</div>
			)}
		</div>
	);
}
