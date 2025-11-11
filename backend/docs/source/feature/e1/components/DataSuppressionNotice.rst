Data Suppression Notice Component
================================================================

Overview
--------

The Data Suppression Notice component displays a message explaining why performance data is not shown for a particular metric or student group, ensuring transparency while protecting student privacy.

Purpose
-------

To inform stakeholders when and why data cannot be displayed, maintaining trust and compliance with federal and state privacy regulations (FERPA) while helping users understand data limitations.

Component Structure
-------------------

The component displays an informational message with an icon and optional detailed explanation:

.. code-block:: html

   <div class="data-suppression-notice">
     <div class="notice-icon">
       <svg aria-hidden="true"><!-- Info icon --></svg>
     </div>
     <div class="notice-content">
       <p class="notice-title">Data Not Displayed</p>
       <p class="notice-reason">
         To protect student privacy, data is not shown when 
         there are fewer than 11 students in a group.
       </p>
       <button class="notice-learn-more">Learn More About Privacy</button>
     </div>
   </div>

Suppression Reasons
-------------------

The component handles multiple suppression scenarios:

1. **Small N-Size** (n < 11)
   - Message: "Data not displayed to protect student privacy. There are fewer than 11 students in this group."
   - Most common suppression reason

2. **Small N-Size for Change** (n < 20 with both years of data)
   - Message: "Change data not displayed. Fewer than 20 students have data for both years."
   - Applies to year-over-year comparisons

3. **Complementary Suppression**
   - Message: "Data not displayed to prevent identification of students through comparison with other groups."
   - When showing data would allow calculation of suppressed group

4. **Insufficient Testing Participation** (<95% participation)
   - Message: "Data not displayed due to insufficient test participation."
   - Applies when participation rate is too low

5. **New School / No Prior Data**
   - Message: "This is the first year of data collection. Change data will be available next year."
   - Not a privacy suppression, but data unavailability

6. **Data Not Yet Available**
   - Message: "Data for this metric will be available in [Month Year]."
   - During data collection/verification periods

Props / Attributes
------------------

.. code-block:: typescript

   interface DataSuppressionNoticeProps {
     reason: SuppressionReason;
     metricName?: string; // Optional context
     studentCount?: number; // If available without violating privacy
     showLearnMore?: boolean; // Default: true
     variant?: 'inline' | 'card' | 'tooltip'; // Default: 'inline'
     onLearnMore?: () => void; // Custom learn more handler
   }

   type SuppressionReason = 
     | 'small-n-size'
     | 'small-n-change'
     | 'complementary'
     | 'insufficient-participation'
     | 'no-prior-data'
     | 'not-yet-available';

Visual Variants
---------------

**Inline Variant** (Default):
- Appears within metric card where data would normally be
- Compact, single-line message
- Subtle styling to not draw excessive attention

**Card Variant**:
- Full card replacement when entire metric is suppressed
- More detailed explanation
- Links to resources

**Tooltip Variant**:
- Appears on hover/focus of suppressed data indicator
- Brief message
- Minimal visual footprint

Accessibility Features
----------------------

- **ARIA Role**: Uses `role="alert"` for screen reader announcements
- **Semantic HTML**: Proper heading hierarchy
- **Keyboard Navigation**: "Learn More" button is keyboard accessible
- **Color Independence**: Uses icon in addition to styling
- **Clear Language**: Avoids jargon, uses plain language

Usage Example
-------------

.. code-block:: tsx

   import { DataSuppressionNotice } from '@/components/performance';

   export function MetricCard({ data }) {
     if (data.suppressed) {
       return (
         <div className="metric-card">
           <h3>{data.metricName}</h3>
           <DataSuppressionNotice
             reason={data.suppressionReason}
             metricName={data.metricName}
             studentCount={data.studentCount}
             variant="card"
             onLearnMore={() => openModal('privacy-policy')}
           />
         </div>
       );
     }

     return (
       <div className="metric-card">
         {/* Regular metric card content */}
       </div>
     );
   }

Learn More Modal Content
-------------------------

When user clicks "Learn More", display detailed information:

.. code-block:: text

   Why is data not displayed?

   California protects student privacy by not showing 
   performance data when there are fewer than 11 students 
   in a group. This follows the Family Educational Rights 
   and Privacy Act (FERPA) and California Education Code.

   What does this mean?
   - The school has data for this group
   - The group is too small to display publicly
   - This protects individual student identities

   Where can I get more information?
   - Contact the school directly
   - Review aggregate district-level data
   - Request information through proper channels

Styling Guidelines
------------------

.. code-block:: css

   .data-suppression-notice {
     background-color: #f5f5f5;
     border-left: 4px solid #757575;
     padding: 1rem;
     border-radius: 4px;
   }

   .notice-icon {
     color: #1976D2;
     font-size: 1.5rem;
   }

   .notice-title {
     font-weight: 600;
     color: #424242;
     margin-bottom: 0.5rem;
   }

   .notice-reason {
     color: #616161;
     font-size: 0.875rem;
     line-height: 1.5;
   }

Compliance & Legal
------------------

**FERPA**: Family Educational Rights and Privacy Act
- Federal law protecting student education records
- Requires suppression when data could identify individuals

**California Education Code §49073.1**:
- State law requiring data suppression for small groups
- Threshold: n < 11 students

**ESSA**: Every Student Succeeds Act
- Federal accountability law
- Requires public reporting but respects privacy

Edge Cases
----------

**All Groups Suppressed**:
- Show school-level aggregate if available
- Explain that no disaggregated data can be shown

**Partial Suppression**:
- Show available groups
- Note which groups are suppressed

**Historical Data**:
- Explain if prior years have data but current year suppressed

Related Components
------------------

- :doc:`MetricCard` - Container that may show suppression notice
- :doc:`StudentGroupBreakdown` - May show suppression for specific groups
- :doc:`TrendChart` - May have gaps due to suppression

See Also
--------

- `FERPA Guidelines <https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html>`_
- `CA Education Code §49073.1 <https://leginfo.legislature.ca.gov/>`_
- `CDE Privacy Policies <https://www.cde.ca.gov/ds/sp/>`_
