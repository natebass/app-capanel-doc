Status Level Indicator Component
================================================================

Overview
--------

The Status Level Indicator is a color-coded visual component that displays the current performance level of a school or district on a specific metric. It uses a five-color system aligned with California's accountability framework.

Purpose
-------

To provide an immediate, accessible visual representation of performance status that can be understood at a glance by all stakeholders, regardless of their familiarity with educational data.

Visual Design
-------------

The component displays one of five colors, each representing a performance level:

- **Blue (Very High)**: Highest performance level
- **Green (High)**: High performance level
- **Yellow (Medium)**: Medium performance level
- **Orange (Low)**: Low performance level
- **Red (Very Low)**: Lowest performance level

Color Specifications
--------------------

All colors meet WCAG 2.1 AA accessibility standards:

.. code-block:: css

   :root {
     --status-blue: #1E90FF;    /* Blue - Very High */
     --status-green: #28A745;   /* Green - High */
     --status-yellow: #FFC107;  /* Yellow - Medium */
     --status-orange: #FF8C00;  /* Orange - Low */
     --status-red: #DC3545;     /* Red - Very Low */
   }

Component Structure
-------------------

.. code-block:: html

   <div class="status-indicator status-indicator--green">
     <span class="status-indicator__label">High</span>
     <span class="status-indicator__icon" aria-hidden="true">●</span>
   </div>

Props / Attributes
------------------

.. code-block:: typescript

   interface StatusLevelIndicatorProps {
     level: 'blue' | 'green' | 'yellow' | 'orange' | 'red';
     label: string; // e.g., "Very High", "High", "Medium", "Low", "Very Low"
     showIcon?: boolean; // Default: true
     size?: 'small' | 'medium' | 'large'; // Default: 'medium'
     ariaLabel?: string; // For screen readers
   }

Accessibility Features
----------------------

- **Screen Reader Support**: Includes descriptive ARIA labels
- **Color Blindness Consideration**: Uses patterns/icons in addition to color
- **Keyboard Navigation**: Focusable with clear focus indicators
- **High Contrast Mode**: Maintains visibility in Windows high contrast mode

Usage Example
-------------

.. code-block:: tsx

   import { StatusLevelIndicator } from '@/components/performance';

   export function PerformanceCard() {
     return (
       <div className="performance-card">
         <h3>English Language Arts</h3>
         <StatusLevelIndicator 
           level="green"
           label="High"
           ariaLabel="Performance level: High"
         />
       </div>
     );
   }

Related Components
------------------

- :doc:`ChangeLevelIndicator` - Shows year-over-year change
- :doc:`MetricCard` - Container for performance data
- :doc:`PerformanceChart` - Visualizes trends over time

See Also
--------

- `California Dashboard Colors <https://www.cde.ca.gov/ta/ac/cm/>`_
- `WCAG Color Contrast Guidelines <https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html>`_
