import {
	type CellData,
	type ColumnDef,
	createPaginatedRowModel,
	type RowData,
	rowPaginationFeature,
	tableFeatures,
} from '@tanstack/react-table'

/**
 * The feature set every {@link import('./DataTable').DataTable} is built from.
 * v9 requires features to be registered explicitly instead of bundling them all.
 */
export const dataTableFeatures = tableFeatures({
	rowPaginationFeature,
	paginatedRowModel: createPaginatedRowModel(),
})

export type DataTableFeatures = typeof dataTableFeatures

/** `ColumnDef` pre-bound to {@link dataTableFeatures}. */
export type DataTableColumnDef<
	TData extends RowData,
	TValue extends CellData = CellData,
> = ColumnDef<DataTableFeatures, TData, TValue>
