.. meta::
   :description lang=en: Grade codes used in the CAASPP and ELPAC research files.

Grades
================================================================

Every result row carries a grade code — *Table B* of the record layouts.  Some
codes are aggregates rather than a single grade, and which grades an aggregate
covers depends on the test.

.. list-table::
   :header-rows: 1
   :widths: 12 58 30

   * - Code
     - Label
     - Aggregate
   * - ``KN``
     - Kindergarten
     - no
   * - ``01``
     - Grade 1
     - no
   * - ``02``
     - Grade 2
     - no
   * - ``03``
     - Grade 3
     - no
   * - ``04``
     - Grade 4
     - no
   * - ``05``
     - Grade 5
     - no
   * - ``06``
     - Grade 6
     - no
   * - ``07``
     - Grade 7
     - no
   * - ``08``
     - Grade 8
     - no
   * - ``09``
     - Grade 9
     - no
   * - ``10``
     - Grade 10
     - no
   * - ``11``
     - Grade 11
     - no
   * - ``12``
     - Grade 12
     - no
   * - ``14``
     - All High School
     - yes
   * - ``99``
     - High School Graduating Class
     - yes
   * - ``13``
     - All Grades
     - yes


What the aggregates cover
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Test
     - ``13`` — All Grades
   * - Smarter Balanced, CAA for ELA/mathematics
     - Grades 3–8 and grade 11.
   * - CAST, CAA for Science
     - Grades 5, 8, 10, 11 and 12.
   * - California Spanish Assessment
     - Grades 3–12.
   * - Summative and Initial ELPAC, and their alternates
     - Kindergarten through grade 12.

``14`` — All High School covers grades 10, 11 and 12 for the science tests and
grades 9–12 for the CSA.  ``99`` — High School Graduating Class reports every
grade twelve student who took a science test in high school, whichever year
they took it in.

.. warning::

   No mean scale score is published on an aggregate row.  Scale scores are set
   per grade and are not comparable across grades, so the state leaves the field
   empty; the percentages on the same row are valid.

.. note::

   From the 2024–25 administration, ELPAC kindergarten figures no longer include
   transitional kindergarten students.
