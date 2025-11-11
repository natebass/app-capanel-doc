Student Group Breakdown Component
================================================================

Overview
--------

The Student Group Breakdown component displays disaggregated performance data for different student demographic groups, enabling stakeholders to identify achievement gaps and monitor equity in educational outcomes.

Purpose
-------

To provide transparent visibility into how different student populations are performing, supporting targeted interventions and ensuring equitable support for all students.

Component Structure
-------------------

The component displays a table or list of student groups with their respective performance levels:

.. code-block:: text

   Student Groups
   ─────────────────────────────────────────────────────
   Group Name                    Status      Change
   ─────────────────────────────────────────────────────
   All Students                  ● Green     ⬆ +2.5%
   English Learners              ● Yellow    ⬆ +3.1%
   Students with Disabilities    ● Orange    ⬇ -1.2%
   Socioeconomically Disadv.     ● Green     ⬆ +2.8%
   Foster Youth                  Data not displayed
   Homeless                      Data not displayed
   ─────────────────────────────────────────────────────

Student Groups Displayed
------------------------

The component shows data for the following federally required student groups (when data is available):

- **All Students**: Overall school/district performance
- **English Learners**: Students learning English as a second language
- **Students with Disabilities**: Students with IEPs or 504 plans
- **Socioeconomically Disadvantaged**: Students from low-income families
- **Foster Youth**: Students in foster care system
- **Homeless**: Students experiencing homelessness
- **Race/Ethnicity Groups**:
  - African American
  - American Indian or Alaska Native
  - Asian
  - Filipino
  - Hispanic or Latino
  - Native Hawaiian or Pacific Islander
  - Two or More Races
  - White

Props / Attributes
------------------

.. code-block:: typescript

   interface StudentGroupBreakdownProps {
     groups: StudentGroupData[];
     metricName: string;
     metricType: 'higher-is-better' | 'lower-is-better';
     showChangeColumn?: boolean; // Default: true
     showStudentCount?: boolean; // Default: true
     sortBy?: 'name' | 'status' | 'change'; // Default: 'name'
     highlightGaps?: boolean; // Highlight groups performing below overall
     expandable?: boolean; // Allow expanding for more details
   }

   interface StudentGroupData {
     groupName: string;
     statusLevel: StatusLevel;
     changeLevel?: ChangeLevel;
     currentValue: number;
     priorValue?: number;
     studentCount: number;
     dataSuppressed: boolean;
     suppressionReason?: string;
   }

Data Suppression Rules
----------------------

Data is suppressed (not displayed) when:

- **n < 11**: Fewer than 11 students in the group
- **n < 20 for change**: Fewer than 20 students with both current and prior year data
- **Personally Identifiable**: Displaying data would reveal information about individual students

When suppressed, display: **"Data not displayed to protect student privacy"**

Equity Gap Highlighting
-----------------------

When `highlightGaps` is enabled, the component visually emphasizes groups performing significantly below the "All Students" average:

.. code-block:: typescript

   const isSignificantGap = (groupValue: number, allStudentsValue: number) => {
     const gapThreshold = 10; // percentage points
     return (allStudentsValue - groupValue) >= gapThreshold;
   };

Groups with significant gaps get additional styling:

.. code-block:: css

   .student-group--gap {
     border-left: 4px solid #ff6b6b;
     background-color: #fff5f5;
   }

Accessibility Features
----------------------

- **Data Table Semantics**: Uses proper `<table>`, `<thead>`, `<tbody>` structure
- **Column Headers**: Clear headers with scope attributes
- **Sortable Columns**: Keyboard-accessible sort controls with ARIA live regions
- **Screen Reader Announcements**: "Sorted by status level, descending"
- **Row Descriptions**: Full context for each row (e.g., "English Learners: Medium performance level, increased by 3.1 percentage points")

Usage Example
-------------

.. code-block:: tsx

   import { StudentGroupBreakdown } from '@/components/performance';

   export function PerformanceDetail() {
     const studentGroups = [
       {
         groupName: 'All Students',
         statusLevel: { level: 'green', label: 'High' },
         changeLevel: { level: 'increased', value: 2.5 },
         currentValue: 65.5,
         priorValue: 63.0,
         studentCount: 500,
         dataSuppressed: false
       },
       {
         groupName: 'English Learners',
         statusLevel: { level: 'yellow', label: 'Medium' },
         changeLevel: { level: 'increased', value: 3.1 },
         currentValue: 45.2,
         priorValue: 42.1,
         studentCount: 150,
         dataSuppressed: false
       },
       {
         groupName: 'Foster Youth',
         statusLevel: null,
         changeLevel: null,
         currentValue: null,
         studentCount: 8,
         dataSuppressed: true,
         suppressionReason: 'Fewer than 11 students'
       }
     ];

     return (
       <StudentGroupBreakdown
         groups={studentGroups}
         metricName="English Language Arts"
         metricType="higher-is-better"
         highlightGaps={true}
         sortBy="status"
       />
     );
   }

Responsive Behavior
-------------------

- **Desktop**: Full table with all columns
- **Tablet**: Stacked cards with key information
- **Mobile**: Accordion-style expandable list items

Interactive Features
--------------------

- **Sorting**: Click column headers to sort by name, status, or change
- **Filtering**: Option to show/hide suppressed groups
- **Expanding**: Click row to see additional details (trend chart, intervention resources)
- **Export**: Download group data as CSV

Related Components
------------------

- :doc:`StatusLevelIndicator` - Displays performance level for each group
- :doc:`ChangeLevelIndicator` - Shows change for each group
- :doc:`MetricCard` - Parent container component
- :doc:`DataSuppressionNotice` - Explains why data is hidden

See Also
--------

- `ESSA Student Group Requirements <https://www.cde.ca.gov/ta/ac/cm/>`_
- `Data Privacy Guidelines <https://www.cde.ca.gov/ds/sp/>`_
- `Achievement Gap Analysis <https://www.edtrust.org/>`_
