Metric Card Component
================================================================

Overview
--------

The Metric Card is the primary container component that displays comprehensive performance data for a single metric (e.g., English Language Arts, Mathematics, Suspension Rate). It integrates multiple sub-components to provide a complete picture of performance.

Purpose
-------

To present all relevant information about a specific performance metric in a consistent, scannable, and accessible format that supports data-driven decision-making.

Component Structure
-------------------

A Metric Card contains the following sections:

1. **Header**: Metric name and icon
2. **Status Section**: Current performance level (StatusLevelIndicator)
3. **Change Section**: Year-over-year change (ChangeLevelIndicator)
4. **Data Section**: Key statistics and values
5. **Student Group Section**: Disaggregated data (StudentGroupBreakdown)
6. **Action Section**: Links to detailed reports or interventions

Visual Layout
-------------

.. code-block:: text

   ┌─────────────────────────────────────────┐
   │ 📊 English Language Arts         [...]  │
   ├─────────────────────────────────────────┤
   │ Status: ● Green (High)                  │
   │ Change: ⬆ Increased (+2.5%)             │
   ├─────────────────────────────────────────┤
   │ Students Meeting Standard: 65.5%        │
   │ Distance from Standard: +10.5 points    │
   ├─────────────────────────────────────────┤
   │ Student Groups:                         │
   │ ▸ English Learners: Yellow              │
   │ ▸ Students with Disabilities: Orange    │
   │ ▸ Socioeconomically Disadvantaged: Green│
   ├─────────────────────────────────────────┤
   │ [View Details] [Download Data]          │
   └─────────────────────────────────────────┘

Props / Attributes
------------------

.. code-block:: typescript

   interface MetricCardProps {
     metricName: string;
     metricType: 'academic' | 'climate' | 'readiness' | 'elpi';
     statusLevel: StatusLevel;
     changeLevel: ChangeLevel;
     currentValue: number;
     distanceFromStandard?: number;
     studentGroups: StudentGroupData[];
     dataSuppressed?: boolean;
     suppressionReason?: string;
     lastUpdated: Date;
     onViewDetails?: () => void;
     onDownloadData?: () => void;
   }

   interface StudentGroupData {
     groupName: string;
     statusLevel: StatusLevel;
     changeLevel?: ChangeLevel;
     currentValue: number;
     studentCount: number;
   }

Responsive Behavior
-------------------

- **Desktop (≥1024px)**: Full card with all sections expanded
- **Tablet (768px - 1023px)**: Stacked layout with collapsible student groups
- **Mobile (<768px)**: Compact view with expandable sections

Accessibility Features
----------------------

- **Semantic HTML**: Uses `<article>`, `<header>`, `<section>` for proper structure
- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Screen Reader Support**: Comprehensive ARIA labels and live regions
- **Focus Management**: Clear focus indicators and logical tab order
- **Skip Links**: "Skip to data" and "Skip to student groups" links

Usage Example
-------------

.. code-block:: tsx

   import { MetricCard } from '@/components/performance';

   export function Dashboard() {
     const elaData = {
       metricName: 'English Language Arts',
       metricType: 'academic',
       statusLevel: { level: 'green', label: 'High' },
       changeLevel: { level: 'increased', value: 2.5 },
       currentValue: 65.5,
       distanceFromStandard: 10.5,
       studentGroups: [
         {
           groupName: 'English Learners',
           statusLevel: { level: 'yellow', label: 'Medium' },
           currentValue: 45.2,
           studentCount: 150
         },
         // ... more groups
       ],
       lastUpdated: new Date('2024-10-15')
     };

     return (
       <div className="dashboard">
         <MetricCard 
           {...elaData}
           onViewDetails={() => navigateTo('/ela-details')}
           onDownloadData={() => downloadCSV('ela-data.csv')}
         />
       </div>
     );
   }

Data Suppression Handling
--------------------------

When data is suppressed for privacy (n < 11), the card displays:

.. code-block:: html

   <div class="metric-card metric-card--suppressed">
     <p class="suppression-notice">
       <span class="icon">ℹ️</span>
       Data not displayed to protect student privacy.
       <button>Learn More</button>
     </p>
   </div>

Theming & Styling
-----------------

The component supports custom theming:

.. code-block:: css

   .metric-card {
     --card-bg: #ffffff;
     --card-border: #e0e0e0;
     --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
     --card-radius: 8px;
     --card-padding: 1.5rem;
   }

Related Components
------------------

- :doc:`StatusLevelIndicator` - Displays performance level
- :doc:`ChangeLevelIndicator` - Shows year-over-year change
- :doc:`StudentGroupBreakdown` - Disaggregated data table
- :doc:`DataSuppressionNotice` - Privacy protection message

See Also
--------

- :doc:`/developer-guide/components`
- `Material Design Card Pattern <https://material.io/components/cards>`_
- `Inclusive Components <https://inclusive-components.design/>`_
