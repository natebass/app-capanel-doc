// ============================================================================
// IMPORTS SECTION
// ============================================================================
// Unlike Python where you use 'import module', TypeScript uses destructuring
// to import specific functions and components from packages

// React hooks - similar to Python's context managers but for component lifecycle
import { useEffect, useState } from 'react';

// Our custom Card components - notice the relative path with './'
// This is like 'from .ui.card import Card, CardHeader, CardBody, CardFooter' in Python
import {
    Card, CardHeader, CardBody, CardFooter
} from './ui/card';

// Chakra UI components - like importing from a large UI library in Python
// Each component is a pre-built React element with styling
import {
    Box,        // Like a <div> but with built-in styling props
    Heading,    // Typography component for titles
    Text,       // Basic text component
    VStack,     // Vertical stack layout (like CSS flexbox column)
    HStack,     // Horizontal stack layout (like CSS flexbox row)
    Badge,      // Small status indicators
    Skeleton,   // Loading placeholder animations
    Alert,      // Error/info message components
    AlertIcon,  // Icons for alert messages
    Grid,       // CSS Grid layout component
    Stat,       // Statistics display components
    StatLabel,
    StatNumber,
    StatHelpText,
    Button,     // Interactive button component
    Icon        // Icon wrapper component
} from '@chakra-ui/react';

// Icon library - these are SVG icons similar to FontAwesome in Python web apps
import { FiSchool, FiUsers, FiMapPin } from 'react-icons/fi';

// API client - this would be like your requests.get() in Python
import { CensusDataService } from '../client';

// ============================================================================
// TYPE DEFINITIONS SECTION
// ============================================================================
// TypeScript interfaces are like Python's dataclasses or Pydantic models
// They define the shape of data structures

/**
 * CensusData Interface
 *
 * This matches the Python CensusData model from your backend.
 * In Python, this would look like:
 *
 * @dataclass
 * class CensusData:
 *     census_data_id: str
 *     academic_year: int
 *     aggregation_level: str
 *     # ... etc
 *
 * TypeScript uses interfaces to define object shapes at compile-time
 */
interface CensusData {
    // Primary key - string representation of UUID
    census_data_id: string;

    // Academic year as number (Python int equivalent)
    academic_year: number;

    // Administrative hierarchy fields
    aggregation_level: string;
    county_code: string;
    district_code: string;
    school_code: string;

    // Human-readable names
    county_name: string;
    district_name: string;
    school_name: string;

    // Charter status and reporting category
    charter: string;              // 'Y' or 'N' for charter school status
    reporting_category: string;

    // Enrollment numbers (all as TypeScript 'number' type)
    total_enr: number;           // Total enrollment across all grades

    // Grade-specific enrollment counts (TK = Transitional Kindergarten)
    gr_tk: number;               // Transitional Kindergarten
    gr_kn: number;               // Kindergarten
    gr_1: number;                // Grade 1
    gr_2: number;                // Grade 2
    gr_3: number;                // Grade 3
    gr_4: number;                // Grade 4
    gr_5: number;                // Grade 5
    gr_6: number;                // Grade 6
    gr_7: number;                // Grade 7
    gr_8: number;                // Grade 8
    gr_9: number;                // Grade 9 (Freshman)
    gr_10: number;               // Grade 10 (Sophomore)
    gr_11: number;               // Grade 11 (Junior)
    gr_12: number;               // Grade 12 (Senior)
}

/**
 * Component Props Interface
 *
 * This defines what parameters our component accepts.
 * In Python, this would be like function parameters with type hints:
 *
 * def census_data_card(census_data_id: str,
 *                     variant: Optional[str] = "elevated",
 *                     show_grade_breakdown: bool = False):
 *
 * The '?' makes properties optional (like Optional[] in Python)
 */
interface CensusDataCardProps {
    censusDataId: string;                                      // Required parameter
    variant?: "outline" | "filled" | "elevated";              // Optional with specific allowed values
    showGradeBreakdown?: boolean;                              // Optional boolean, defaults to false
}

// ============================================================================
// MAIN COMPONENT FUNCTION
// ============================================================================

/**
 * Census Data Card Component
 *
 * This is a React functional component (like a Python function that returns HTML).
 * It displays school census data fetched from the FastAPI backend.
 * Requires superuser authentication to access the /api/v1/censusdata/{id} endpoint.
 *
 * PYTHON EQUIVALENT:
 * def census_data_card(census_data_id: str, variant: str = "elevated",
 *                     show_grade_breakdown: bool = False) -> str:
 *     # Function body would return HTML string
 *
 * @param censusDataId - UUID string to identify which school's data to fetch
 * @param variant - Visual style of the card (outline, filled, or elevated)
 * @param showGradeBreakdown - Whether to show detailed grade-by-grade enrollment
 *
 * @example
 * ```tsx
 * <CensusDataCard
 *   censusDataId="123e4567-e89b-12d3-a456-426614174000"
 *   variant="elevated"
 *   showGradeBreakdown={true}
 * />
 * ```
 */
function CensusDataCard({
                            censusDataId,
                            variant = "elevated",           // Default value syntax (like Python defaults)
                            showGradeBreakdown = false      // TypeScript infers this as boolean
                        }: CensusDataCardProps) {          // Type annotation for the entire props object

    // =========================================================================
    // STATE MANAGEMENT SECTION
    // =========================================================================
    // React hooks are like Python properties with getters/setters
    // useState creates a variable and a function to update it

    // State for storing the fetched census data
    // Similar to: self.data = None in a Python class
    const [data, setData] = useState<CensusData | null>(null);

    // State for tracking loading status
    // Similar to: self.loading = True in Python
    const [loading, setLoading] = useState<boolean>(true);

    // State for storing error messages
    // Similar to: self.error = None in Python
    const [error, setError] = useState<string | null>(null);

    // =========================================================================
    // SIDE EFFECTS SECTION (API CALLS)
    // =========================================================================
    // useEffect is like Python's __init__ method - it runs when component loads
    // or when dependencies change. Similar to:
    //
    // def __init__(self, census_data_id):
    //     self.fetch_census_data(census_data_id)

    useEffect(() => {
        /**
         * Async function to fetch census data from API
         *
         * PYTHON EQUIVALENT:
         * async def fetch_census_data(self):
         *     try:
         *         response = await requests.get(f'/api/v1/censusdata/{self.census_data_id}')
         *         self.data = response.json()
         *     except requests.HTTPError as e:
         *         self.error = str(e)
         *     finally:
         *         self.loading = False
         */
        const fetchCensusData = async () => {
            try {
                // Reset state before making API call (like clearing previous results)
                setLoading(true);                    // Show loading spinner
                setError(null);                      // Clear any previous errors

                // API Call to your FastAPI backend
                // This calls the router endpoint: GET /api/v1/censusdata/{id}
                // Equivalent to: requests.get(f'/api/v1/censusdata/{censusDataId}')
                const response = await CensusDataService.readCensusData(censusDataId);

                // Update state with successful response
                setData(response);                   // Store the census data

            } catch (err) {
                // Error handling - similar to Python try/except blocks
                if (err instanceof Error) {
                    // Handle specific HTTP status codes (like your FastAPI exceptions)
                    if (err.message.includes('403')) {
                        setError('Access denied: Superuser permissions required');
                    } else if (err.message.includes('404')) {
                        setError('Census data not found');
                    } else {
                        setError(err.message);
                    }
                } else {
                    // Generic error fallback
                    setError('Failed to fetch census data');
                }
            } finally {
                // This always runs (like Python's finally block)
                setLoading(false);                   // Hide loading spinner
            }
        };

        // Only fetch data if we have a valid ID (guard clause)
        // Similar to: if census_data_id: fetch_census_data()
        if (censusDataId) {
            fetchCensusData();
        }

    }, [censusDataId]);                        // Dependency array - re-run when censusDataId changes

    // =========================================================================
    // CONDITIONAL RENDERING SECTION
    // =========================================================================
    // These are like Python if/elif/else statements that return different HTML
    // based on the current state of the component

    /**
     * Loading State - Show skeleton placeholders while fetching data
     *
     * PYTHON EQUIVALENT:
     * if self.loading:
     *     return self.render_loading_skeleton()
     *
     * Skeleton components are animated placeholders that show while data loads.
     * This improves user experience by showing the layout structure immediately.
     */
    if (loading) {
        return (
            <Card variant={variant}>
                <CardHeader>
                    {/* Skeleton bars mimic the actual content dimensions */}
                    <Skeleton height="24px" width="200px" />          {/* School name placeholder */}
                    <Skeleton height="16px" width="150px" mt={2} />   {/* District/county placeholder */}
                </CardHeader>
                <CardBody>
                    <VStack spacing={3}>
                        <Skeleton height="20px" width="100%" />         {/* Full width bar */}
                        <Skeleton height="20px" width="80%" />          {/* Shorter bar */}
                        <Skeleton height="40px" width="60%" />          {/* Enrollment number placeholder */}
                    </VStack>
                </CardBody>
            </Card>
        );
    }

    /**
     * Error State - Show error message and retry button
     *
     * PYTHON EQUIVALENT:
     * if self.error:
     *     return self.render_error_message(self.error)
     *
     * This handles all error scenarios (403 Forbidden, 404 Not Found, network errors)
     */
    if (error) {
        return (
            <Card variant={variant}>
                <CardBody>
                    {/* Chakra UI Alert component for error messages */}
                    <Alert status="error">                           {/* Red color scheme */}
                        <AlertIcon />                                   {/* Warning/error icon */}
                        <Box>
                            <Text fontWeight="bold">Error loading census data</Text>
                            <Text fontSize="sm">{error}</Text>           {/* Display specific error message */}
                        </Box>
                    </Alert>
                </CardBody>
                <CardFooter>
                    {/* Retry button - reloads the entire page */}
                    <Button
                        size="sm"
                        onClick={() => window.location.reload()}      {/* JavaScript equivalent of browser refresh */}
                        width="full"                                  {/* Full width button */}
                        colorScheme="red"                            {/* Red theme to match error */}
                        variant="outline"                            {/* Outline style (not filled) */}
                    >
                        Retry
                    </Button>
                </CardFooter>
            </Card>
        );
    }

    /**
     * Empty State - Show message when no data is found
     *
     * PYTHON EQUIVALENT:
     * if not self.data:
     *     return self.render_empty_message()
     *
     * This handles the case where the API call succeeded but returned null/empty data
     */
    if (!data) {
        return (
            <Card variant={variant}>
                <CardBody>
                    <Text color="fg.muted" textAlign="center">     {/* Muted text color, centered */}
                        No census data found for ID: {censusDataId}
                    </Text>
                </CardBody>
            </Card>
        );
    }

    // =========================================================================
    // DATA PROCESSING SECTION
    // =========================================================================
    // This section processes the raw data before displaying it

    /**
     * Grade Data Processing
     *
     * Transform the individual grade fields into a structured array for easier rendering.
     * Filter out grades with zero enrollment to keep the display clean.
     *
     * PYTHON EQUIVALENT:
     * grade_data = [
     *     {'label': 'TK', 'count': data.gr_tk},
     *     {'label': 'K', 'count': data.gr_kn},
     *     # ... etc
     * ]
     * grade_data = [grade for grade in grade_data if grade['count'] > 0]
     */
    const gradeData = [
        { label: 'TK', count: data.gr_tk },     // Transitional Kindergarten
        { label: 'K', count: data.gr_kn },      // Kindergarten
        { label: '1', count: data.gr_1 },       // 1st Grade
        { label: '2', count: data.gr_2 },       // 2nd Grade
        { label: '3', count: data.gr_3 },       // 3rd Grade
        { label: '4', count: data.gr_4 },       // 4th Grade
        { label: '5', count: data.gr_5 },       // 5th Grade
        { label: '6', count: data.gr_6 },       // 6th Grade
        { label: '7', count: data.gr_7 },       // 7th Grade
        { label: '8', count: data.gr_8 },       // 8th Grade
        { label: '9', count: data.gr_9 },       // 9th Grade (Freshman)
        { label: '10', count: data.gr_10 },     // 10th Grade (Sophomore)
        { label: '11', count: data.gr_11 },     // 11th Grade (Junior)
        { label: '12', count: data.gr_12 }      // 12th Grade (Senior)
    ].filter(grade => grade.count > 0);       // Only keep grades with students

    return (
        <Card variant={variant}>
            <CardHeader>
                <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1} flex={1}>
                        <HStack>
                            <Icon as={FiSchool} boxSize={5} color="blue.500" />
                            <Heading size="md" noOfLines={2}>
                                {data.school_name}
                            </Heading>
                        </HStack>
                        <HStack spacing={2} color="fg.muted" fontSize="sm" flexWrap="wrap">
                            <HStack>
                                <Icon as={FiMapPin} boxSize={3} />
                                <Text>{data.district_name}</Text>
                            </HStack>
                            <Text>•</Text>
                            <Text>{data.county_name}</Text>
                        </HStack>
                    </VStack>
                    <VStack spacing={1} align="end">
                        <Badge
                            colorScheme={data.charter === 'Y' ? 'purple' : 'gray'}
                            size="sm"
                        >
                            {data.charter === 'Y' ? 'Charter' : 'Public'}
                        </Badge>
                        <Text fontSize="xs" color="fg.muted">
                            AY {data.academic_year}
                        </Text>
                    </VStack>
                </HStack>
            </CardHeader>

            <CardBody>
                <VStack spacing={4}>
                    {/* Total Enrollment - Main statistic */}
                    <Box textAlign="center" width="full">
                        <Stat>
                            <StatLabel>
                                <HStack justify="center">
                                    <Icon as={FiUsers} boxSize={4} />
                                    <Text>Total Enrollment</Text>
                                </HStack>
                            </StatLabel>
                            <StatNumber fontSize="2xl" color="blue.500">
                                {data.total_enr.toLocaleString()}
                            </StatNumber>
                            <StatHelpText>
                                {data.reporting_category}
                            </StatHelpText>
                        </Stat>
                    </Box>

                    {/* Grade-by-grade breakdown (optional) */}
                    {showGradeBreakdown && gradeData.length > 0 && (
                        <Box width="full">
                            <Text fontSize="sm" fontWeight="medium" mb={3}>
                                Enrollment by Grade
                            </Text>
                            <Grid
                                templateColumns="repeat(auto-fit, minmax(60px, 1fr))"
                                gap={2}
                                maxH="200px"
                                overflowY="auto"
                                p={1}
                            >
                                {gradeData.map((grade) => (
                                    <Box
                                        key={grade.label}
                                        p={2}
                                        bg="bg.muted"
                                        borderRadius="md"
                                        textAlign="center"
                                        _hover={{ bg: "bg.emphasized" }}
                                        transition="background-color 0.2s"
                                    >
                                        <Text fontSize="xs" color="fg.muted">
                                            Grade {grade.label}
                                        </Text>
                                        <Text fontSize="sm" fontWeight="bold">
                                            {grade.count.toLocaleString()}
                                        </Text>
                                    </Box>
                                ))}
                            </Grid>
                        </Box>
                    )}
                </VStack>
            </CardBody>

            {/* Footer with additional metadata */}
            <CardFooter>
                <VStack width="full" spacing={2}>
                    <HStack justify="space-between" width="full" fontSize="xs" color="fg.muted">
                        <Text>School Code: {data.school_code}</Text>
                        <Text>District Code: {data.district_code}</Text>
                    </HStack>
                    {data.aggregation_level && (
                        <Text fontSize="xs" color="fg.muted" textAlign="center">
                            Aggregation Level: {data.aggregation_level}
                        </Text>
                    )}
                </VStack>
            </CardFooter>
        </Card>
    );
}

export { CensusDataCard };
export type { CensusDataCardProps, CensusData };