Trend Chart Component
================================================================

Overview
--------

The Trend Chart component visualizes performance data over multiple years, allowing stakeholders to see long-term patterns and assess whether improvements are sustained or temporary.

Purpose
-------

To provide a clear, accessible visualization of multi-year performance trends that helps stakeholders understand whether schools are making consistent progress toward their goals.

Component Structure
-------------------

The component displays a line chart or bar chart showing performance over time:

.. code-block:: text

   English Language Arts - 5 Year Trend
   ─────────────────────────────────────────────────────
   70% │                                        ●
       │                                   ●
   60% │                              ●
       │                         ●
   50% │                    ●
       │
   40% │
       └─────────────────────────────────────────────
         2020   2021   2022   2023   2024
   
   ● 2020: 50.2% (Yellow)
   ● 2021: 52.8% (Yellow)
   ● 2022: 58.3% (Yellow)
   ● 2023: 62.1% (Green)
   ● 2024: 65.5% (Green)

Chart Types
-----------

**Line Chart** (Default):
- Best for showing continuous trends
- Emphasizes direction of change
- Good for comparing multiple groups on same chart

**Bar Chart**:
- Best for comparing discrete years
- Easier to read exact values
- Good for showing status level colors

**Area Chart**:
- Shows cumulative progress
- Emphasizes magnitude of change
- Good for goal attainment visualization

Props / Attributes
------------------

.. code-block:: typescript

   interface TrendChartProps {
     metricName: string;
     chartType?: 'line' | 'bar' | 'area'; // Default: 'line'
     data: YearlyPerformanceData[];
     showStatusColors?: boolean; // Color points by status level
     showGoalLine?: boolean; // Display target goal
     goalValue?: number;
     height?: number; // Default: 300
     width?: number | 'auto'; // Default: 'auto'
     interactive?: boolean; // Enable tooltips and zoom
     ariaLabel?: string;
   }

   interface YearlyPerformanceData {
     year: number;
     value: number;
     statusLevel?: StatusLevel;
     studentCount?: number;
     dataSuppressed?: boolean;
   }

Accessibility Features
----------------------

- **Keyboard Navigation**: Arrow keys to navigate data points
- **Screen Reader Support**: Complete data table alternative
- **ARIA Labels**: Descriptive labels for all chart elements
- **Tooltip Announcements**: Screen readers announce on focus
- **High Contrast Mode**: Patterns in addition to colors

Data Table Alternative
----------------------

The component provides a data table for screen readers and as a fallback:

.. code-block:: html

   <div class="trend-chart">
     <svg class="trend-chart__visual" aria-hidden="true">
       <!-- Chart visualization -->
     </svg>
     
     <table class="trend-chart__data sr-only">
       <caption>English Language Arts Performance 2020-2024</caption>
       <thead>
         <tr>
           <th scope="col">Year</th>
           <th scope="col">Percentage Meeting Standard</th>
           <th scope="col">Status Level</th>
         </tr>
       </thead>
       <tbody>
         <tr>
           <th scope="row">2020</th>
           <td>50.2%</td>
           <td>Yellow (Medium)</td>
         </tr>
         <!-- More rows -->
       </tbody>
     </table>
   </div>

Interactive Features
--------------------

**Tooltips**: Hover/focus on data points to see details

.. code-block:: text

   2024: 65.5% Meeting Standard
   Status: Green (High)
   Change from 2023: +3.4 percentage points
   Students: 500

**Zoom**: Click and drag to zoom into specific time period

**Compare**: Toggle visibility of different student groups

**Export**: Download chart as PNG or SVG, data as CSV

Visual Design Guidelines
------------------------

**Color Palette**:

.. code-block:: css

   .trend-chart {
     --line-color: #1976D2;
     --point-color: #1565C0;
     --grid-color: #E0E0E0;
     --goal-line-color: #4CAF50;
     --axis-color: #424242;
   }

**Typography**:
- Axis labels: 12px, semibold
- Data labels: 11px, regular
- Title: 16px, bold

**Spacing**:
- Padding: 20px
- Point radius: 5px
- Line width: 2px

Usage Example
-------------

.. code-block:: tsx

   import { TrendChart } from '@/components/performance';

   export function PerformanceDetail() {
     const trendData = [
       { year: 2020, value: 50.2, statusLevel: { level: 'yellow' }, studentCount: 480 },
       { year: 2021, value: 52.8, statusLevel: { level: 'yellow' }, studentCount: 490 },
       { year: 2022, value: 58.3, statusLevel: { level: 'yellow' }, studentCount: 495 },
       { year: 2023, value: 62.1, statusLevel: { level: 'green' }, studentCount: 505 },
       { year: 2024, value: 65.5, statusLevel: { level: 'green' }, studentCount: 500 },
     ];

     return (
       <div className="performance-detail">
         <h2>English Language Arts Trend</h2>
         <TrendChart
           metricName="English Language Arts"
           data={trendData}
           showStatusColors={true}
           showGoalLine={true}
           goalValue={70}
           interactive={true}
           ariaLabel="Five year trend showing English Language Arts performance improving from 50.2% in 2020 to 65.5% in 2024"
         />
       </div>
     );
   }

Handling Missing Data
---------------------

When data is missing for specific years:

- **Gap in Line**: Show dotted line between available points
- **Annotation**: Add note explaining gap (e.g., "No testing in 2021 due to COVID-19")
- **Screen Reader**: Announce missing years in data table

Technical Implementation
------------------------

The component uses **D3.js** for rendering:

.. code-block:: typescript

   import * as d3 from 'd3';

   const drawLineChart = (data: YearlyPerformanceData[], config: ChartConfig) => {
     const svg = d3.select(containerRef.current);
     
     const xScale = d3.scaleLinear()
       .domain([d3.min(data, d => d.year), d3.max(data, d => d.year)])
       .range([0, width]);
     
     const yScale = d3.scaleLinear()
       .domain([0, 100])
       .range([height, 0]);
     
     const line = d3.line<YearlyPerformanceData>()
       .x(d => xScale(d.year))
       .y(d => yScale(d.value))
       .curve(d3.curveMonotoneX);
     
     svg.append('path')
       .datum(data)
       .attr('d', line)
       .attr('stroke', config.lineColor)
       .attr('fill', 'none');
   };

Related Components
------------------

- :doc:`MetricCard` - Contains the trend chart
- :doc:`StatusLevelIndicator` - Colors data points by status
- :doc:`StudentGroupBreakdown` - Can show trends for specific groups

See Also
--------

- `D3.js Documentation <https://d3js.org/>`_
- `Accessible Charts Guide <https://www.a11y-101.com/design/charts>`_
- `Data Visualization Best Practices <https://www.cde.ca.gov/ta/ac/cm/>`_
