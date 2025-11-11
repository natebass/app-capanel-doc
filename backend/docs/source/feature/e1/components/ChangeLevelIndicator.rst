Change Level Indicator Component
================================================================

Overview
--------

The Change Level Indicator displays the year-over-year change in performance for a specific metric, showing whether the school or district improved, maintained, or declined in their performance.

Purpose
-------

To provide stakeholders with a clear understanding of performance trends over time, enabling them to assess whether interventions and strategies are working.

Visual Design
-------------

The component uses directional icons and text to indicate change:

- **Increased Significantly** ⬆⬆ (Green)
- **Increased** ⬆ (Light Green)
- **Maintained** ➡ (Gray)
- **Declined** ⬇ (Light Orange)
- **Declined Significantly** ⬇⬇ (Orange/Red)

**Note**: For metrics where lower is better (suspension rate, chronic absenteeism), the colors are inverted (decline = improvement = green).

Component Structure
-------------------

.. code-block:: html

   <div class="change-indicator change-indicator--increased">
     <span class="change-indicator__icon" aria-hidden="true">⬆</span>
     <span class="change-indicator__label">Increased</span>
     <span class="change-indicator__value">+2.5%</span>
   </div>

Props / Attributes
------------------

.. code-block:: typescript

   interface ChangeLevelIndicatorProps {
     changeLevel: 'increased-significantly' | 'increased' | 'maintained' | 'declined' | 'declined-significantly';
     changeValue: number; // Percentage point change
     metricType: 'higher-is-better' | 'lower-is-better'; // Determines color scheme
     label?: string; // Custom label override
     showValue?: boolean; // Display numeric change, default: true
     ariaLabel?: string; // For screen readers
   }

Color Logic by Metric Type
---------------------------

**Higher is Better** (Academic Achievement):

- Increased = Green (Good)
- Declined = Red (Needs Attention)

**Lower is Better** (Suspension Rate, Chronic Absenteeism):

- Declined = Green (Good)
- Increased = Red (Needs Attention)

Change Thresholds
------------------

Thresholds vary by metric type. Example for academic metrics:

.. code-block:: typescript

   const academicThresholds = {
     increasedSignificantly: 3.0,  // +3.0 points or more
     increased: 1.0,                // +1.0 to +2.9 points
     maintained: 0.0,               // -0.9 to +0.9 points
     declined: -1.0,                // -1.0 to -2.9 points
     declinedSignificantly: -3.0    // -3.0 points or less
   };

Accessibility Features
----------------------

- **Screen Reader Announcements**: "Performance increased by 2.5 percentage points"
- **Semantic HTML**: Uses appropriate ARIA roles and labels
- **Color + Icon**: Never relies on color alone
- **Focus Management**: Keyboard accessible with visible focus states

Usage Example
-------------

.. code-block:: tsx

   import { ChangeLevelIndicator } from '@/components/performance';

   export function PerformanceCard() {
     return (
       <div className="performance-card">
         <h3>Mathematics Achievement</h3>
         <ChangeLevelIndicator 
           changeLevel="increased"
           changeValue={2.5}
           metricType="higher-is-better"
           ariaLabel="Mathematics performance increased by 2.5 percentage points from last year"
         />
       </div>
     );
   }

Edge Cases
----------

**Insufficient Data**: When no prior year data exists, display "No Comparison Data" instead of change indicator.

**First Year of Testing**: For new schools or new metrics, show "Baseline Year" label.

**Data Suppression**: When data is suppressed for privacy, show "Data Not Displayed" with explanation tooltip.

Related Components
------------------

- :doc:`StatusLevelIndicator` - Shows current performance level
- :doc:`TrendChart` - Multi-year trend visualization
- :doc:`MetricCard` - Container for performance data

See Also
--------

- `California Dashboard Change Levels <https://www.cde.ca.gov/ta/ac/cm/>`_
- `Accessible Icon Libraries <https://fontawesome.com/>`_
