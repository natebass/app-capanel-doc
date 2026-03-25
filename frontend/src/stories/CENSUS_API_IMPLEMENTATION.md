# Census Data API Implementation

## Overview

Successfully implemented comprehensive census data integration including:

1. **Total enrollment display** in dashboard "Total Users" tab
2. **Interactive census data search card** with tabbed interface
3. **Consistent error handling** across all components
4. **Loading states** with skeleton UI components
5. **Type-safe TypeScript implementation** with proper interfaces

## What Was Implemented

### 1. Census Service (`src/services/censusService.ts`)

- **CensusService** class with `getCensusData()` method
- **TypeScript interfaces** for `CensusData` and `CensusDataResponse`
- **Error handling** for 404, 422, and 500 HTTP errors
- **API endpoint**: `/api/v1/censusdata`

### 2. Census Data Hook (`src/hooks/useCensusData.ts`)

- **useCensusData()** - Main TanStack Query hook
- **useTotalEnrollment()** - Specialized hook for total enrollment data
- **Query configuration**:
  - 5-minute stale time
  - 10-minute cache time
  - 3 retry attempts with exponential backoff
  - No refetch on window focus (prevents excessive API calls)

### 3. Dashboard Component Updates (`src/routes/_home/dashboard.tsx`)

- **TotalEnrollmentDisplay** component replacing line 64 comment
- **CensusDataSearchCard** - New interactive card with tabs for searching specific census data
- **Loading state** with Chakra UI Spinner and Skeleton components
- **Error state** with consistent styled error messages across both cards
- **Success state** with formatted number display (includes thousands separators)
- **Type-safe** implementation with proper null/undefined handling

### 4. Census Data Search Card (`CensusDataSearchCard` component)

- **Interactive Tabs**: Three-tab interface ("Found ID", "Default", "Last Searched")
- **Dynamic Data Loading**: Loads census data by ID using `useCensusDataById` hook
- **Sample Data Button**: Allows testing with predefined sample ID
- **State Management**: React useState for managing search ID
- **Responsive Design**: Works seamlessly in dashboard grid layout
- **Consistent Styling**: Matches existing dashboard card patterns

#### Tab Features:

- **"Found ID" Tab**:
  - Displays loaded census data (school name, enrollment, charter status, academic year)
  - "Load Sample Data" button when no data is selected
  - Loading skeleton during API calls
  - Error handling with styled error messages
- **"Default" Tab**: Shows placeholder content when no data is selected
- **"Last Searched" Tab**: Shows status of the last search operation

## Features

### Loading States

```tsx
// Shows centered spinner while fetching data
<Spinner size='md' color='blue.500' />
```

### Error Handling

```tsx
// Shows styled error message on API failure
<Box color='red.600' bg='red.50' border='1px solid' borderColor='red.200'>
	Failed to load data
</Box>
```

### Data Formatting

```tsx
// Formats numbers with thousands separators (e.g., "1,234,567")
const formattedTotalEnr = totalEnr?.toLocaleString() || '0'
```

### Caching & Performance

- **5-minute cache**: Data stays fresh for 5 minutes
- **Background refetch**: Updates data automatically
- **Retry logic**: 3 attempts with exponential backoff (1s, 2s, 4s delays)
- **Error resilience**: Graceful fallbacks on API failures

## API Response Expected Format

The service expects the API to return data in this format:

```typescript
{
	data: {
		total_enr: 123456
	}
,
	status: "success"
}
```

## Testing the Implementation

### 1. Run Development Server

```bash
cd "C:\Users\shwnd\Desktop\LB_LocalCopy\Coding\app-capanel-web\frontend"
npm run dev
```

### 2. Navigate to Dashboard

- Go to `http://localhost:5173` (or your dev server URL)
- Navigate to the Dashboard page
- Test both implementations:
  - **First Card**: Click on the "Total" tab to see total enrollment data
  - **Second Card**: Interact with the census data search card tabs

### 3. Expected Behaviors

#### **First Card (Total Users with Total Enrollment)**:

- **When API is Working**: Shows loading spinner briefly, displays formatted total enrollment number, maintains existing
  trend indicators (+12.5% from last month)
- **When API is Down/Error**: Shows loading spinner briefly, displays red error box with "Failed to load data",
  preserves card layout and styling
- **When API Returns No Data**: Shows "N/A" in place of the number

#### **Second Card (Census Data Search Card)**:

- **"Found ID" Tab**:
  - Initially shows placeholder content with "Load Sample Data" button
  - When button clicked: Shows loading skeleton, then displays census data (school name, enrollment, charter/public
    status, academic year)
  - On API error: Shows consistent red error box with "Failed to load census data"
  - School icon (FiHome) and properly formatted enrollment numbers
  - Color-coded charter status badges (purple for charter, gray for public)
- **"Default" Tab**: Shows static placeholder content with "No data selected" message
- **"Last Searched" Tab**: Shows checkmark (✓) when data was loaded, dash (-) when no searches performed

### 4. Browser DevTools Testing

- **Network Tab**: Check for API calls to `/api/v1/censusdata`
- **Console**: Monitor for any errors or warnings
- **React Query DevTools**: Inspect query status and cached data

## Integration with Existing Code

The implementation seamlessly integrates with:

- ✅ **Existing TanStack Query setup**
- ✅ **Chakra UI v3 components and styling**
- ✅ **TypeScript type safety**
- ✅ **Current tabbed interface design**
- ✅ **Existing error handling patterns**
- ✅ **OpenAPI client architecture**

## Error Resolution

### Common Issues:

1. **API Endpoint Not Available**
   - Service will show error state
   - Retries 3 times automatically
   - Falls back to "Failed to load data" message

2. **Type Mismatch in API Response**
   - TypeScript will catch at compile time
   - Runtime safety with optional chaining (`totalEnr?.toLocaleString()`)

3. **Network Connectivity Issues**
   - TanStack Query handles network retries
   - Caches last successful response
   - Shows appropriate loading/error states

## Next Steps for Production

### 1. API Backend Implementation

Ensure the backend API endpoint `/api/v1/censusdata` returns:

```json
{
	"data": {
		"total_enr": 123456
	},
	"status": "success"
}
```

### 2. Environment Configuration

Configure proper API base URL in OpenAPI settings for different environments.

### 3. Monitoring

Add logging/monitoring for:

- API response times
- Error rates
- Cache hit/miss ratios

### 4. Testing

Add unit tests for:

- `CensusService.getCensusData()`
- `useTotalEnrollment()` hook
- `TotalEnrollmentDisplay` component

## Files Modified/Created

- ✅ **Created**: `src/services/censusService.ts`
- ✅ **Created**: `src/hooks/useCensusData.ts`
- ✅ **Modified**: `src/routes/_home/dashboard.tsx` (line 64 implementation)
- ✅ **Created**: `CENSUS_API_IMPLEMENTATION.md` (this file)

The implementation is complete and ready for testing with a working `/api/v1/censusdata` backend endpoint.
