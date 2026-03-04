Performance Chart Component
================================================================

Overview
--------

The Performance Chart component provides a high-level visual summary of performance across multiple metrics for a selected school, district, or student group. It complements the :doc:`TrendChart` by emphasizing cross-metric comparison in a single view.

Purpose
-------

To help stakeholders quickly identify strengths, risks, and priority areas by comparing current-year performance levels and recent direction of change across key indicators.

Key Use Cases
-------------

- Compare current status across English Language Arts, Mathematics, and College/Career indicators
- Spot metrics that are improving, declining, or stable
- Prioritize metrics requiring intervention planning
- Support leadership briefings with a concise visual summary

Chart Design
------------

The chart can be rendered as a grouped bar chart with status color encoding:

.. code-block:: text

   2025 Performance Summary
   -----------------------------------------------
   ELA            [################]  Green   (+)
   Math           [############....]  Yellow  (=)
   Suspension     [########........]  Orange  (-)
   College/Career [#############...]  Green   (+)

   Legend: (+) improving, (=) stable, (-) declining

Data Model
----------

.. code-block:: typescript

   interface PerformanceChartProps {
     entityName: string;
     reportingYear: number;
     metrics: PerformanceMetric[];
     chartType?: 'grouped-bar' | 'radar'; // Default: 'grouped-bar'
     showChangeMarkers?: boolean; // Default: true
     showStatusLegend?: boolean; // Default: true
     interactive?: boolean; // Default: true
     ariaLabel?: string;
   }

   interface PerformanceMetric {
     metricId: string;
     metricName: string;
     value: number;
     statusLevel: 'blue' | 'green' | 'yellow' | 'orange' | 'red';
     changeDirection?: 'increased' | 'maintained' | 'declined';
     targetValue?: number;
   }

Accessibility Features
----------------------

- **Keyboard Navigation**: Tab/arrow navigation between metric bars
- **Screen Reader Support**: Announces metric, value, status level, and change direction
- **Non-Color Cues**: Uses text markers and icons in addition to color
- **Table Fallback**: Provides an accessible table view for all chart data

Usage Example
-------------

.. code-block:: tsx

   import { PerformanceChart } from '@/components/performance';

   export function LEAPerformanceOverview() {
     const metrics = [
       { metricId: 'ela', metricName: 'English Language Arts', value: 65.5, statusLevel: 'green', changeDirection: 'increased' },
       { metricId: 'math', metricName: 'Mathematics', value: 54.2, statusLevel: 'yellow', changeDirection: 'maintained' },
       { metricId: 'suspension', metricName: 'Suspension Rate', value: 4.8, statusLevel: 'orange', changeDirection: 'declined' },
     ];

     return (
       <PerformanceChart
         entityName="Sample Unified School District"
         reportingYear={2025}
         metrics={metrics}
         showChangeMarkers={true}
         showStatusLegend={true}
         interactive={true}
         ariaLabel="2025 performance summary comparing status and change across key metrics"
       />
     );
   }

Implementation Notes
--------------------

- Use :doc:`StatusLevelIndicator` color tokens for consistent status mapping
- Align change arrows with :doc:`ChangeLevelIndicator` semantics
- Include tooltip and inline text labels for low-vision readability
- Keep chart responsive with mobile-friendly horizontal scrolling

Related Components
------------------

- :doc:`MetricCard` - Detailed metric-level container
- :doc:`TrendChart` - Year-over-year trend for a single metric
- :doc:`StudentGroupBreakdown` - Disaggregated subgroup context

See Also
--------

- `California Dashboard <https://www.caschooldashboard.org/>`_
- `WAI-ARIA Authoring Practices: Graphics <https://www.w3.org/WAI/ARIA/apg/patterns/>`_
