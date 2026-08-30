.. meta::
   :description lang=en: The student groups CAASPP and ELPAC report results for.

Student Groups
================================================================

Results are published for the whole tested population and for each of the
student groups below — *Table A* of the state's record layouts.  A group is
identified by a three-digit ``Student Group ID``.

The two programs reuse the same identifiers with different wording.  ``128`` is
"Reported disabilities" under CAASPP and "Students Receiving Special Education
Services" under ELPAC, so this application keys the lookup on the program as
well as the identifier.

.. note::

   No results are reported for any group with fewer than 11 students.  Those
   rows are present in the file with every figure replaced by ``*``, and this
   application stores them with a ``suppressed`` flag rather than dropping them,
   so a report can distinguish "withheld" from "no such group".

CAASPP student groups
---------------------

.. list-table::
   :header-rows: 1
   :widths: 10 60 30

   * - ID
     - Name
     - Category
   * - ``001``
     - All Students
     - All Students
   * - ``128``
     - Reported disabilities
     - Disability Status
   * - ``099``
     - No reported disabilities
     - Disability Status
   * - ``031``
     - Socioeconomically disadvantaged
     - Economic Status
   * - ``111``
     - Not socioeconomically disadvantaged
     - Economic Status
   * - ``006``
     - IFEP, RFEP, and EO (Fluent English proficient and English only)
     - English-Language Fluency
   * - ``007``
     - IFEP (Initial fluent English proficient)
     - English-Language Fluency
   * - ``008``
     - RFEP (Reclassified fluent English proficient)
     - English-Language Fluency
   * - ``120``
     - ELs enrolled less than 12 months
     - English-Language Fluency
   * - ``142``
     - ELs enrolled 12 months or more
     - English-Language Fluency
   * - ``160``
     - EL (English learner, excluding RFEP)
     - English-Language Fluency
   * - ``243``
     - ADEL (Adult English learner)
     - English-Language Fluency
   * - ``180``
     - EO (English only)
     - English-Language Fluency
   * - ``170``
     - Ever-EL
     - English-Language Fluency
   * - ``250``
     - LTEL (Long-Term English learner)
     - English-Language Fluency
   * - ``251``
     - AR-LTEL (At-Risk of becoming LTEL)
     - English-Language Fluency
   * - ``252``
     - Never-EL
     - English-Language Fluency
   * - ``190``
     - TBD (To be determined)
     - English-Language Fluency
   * - ``075``
     - American Indian or Alaska Native
     - Race and Ethnicity
   * - ``076``
     - Asian
     - Race and Ethnicity
   * - ``074``
     - Black or African American
     - Race and Ethnicity
   * - ``077``
     - Filipino
     - Race and Ethnicity
   * - ``078``
     - Hispanic or Latino
     - Race and Ethnicity
   * - ``079``
     - Native Hawaiian or Pacific Islander
     - Race and Ethnicity
   * - ``080``
     - White
     - Race and Ethnicity
   * - ``144``
     - Two or more races
     - Race and Ethnicity
   * - ``201``
     - American Indian or Alaska Native
     - Ethnicity for Socioeconomically Disadvantaged
   * - ``202``
     - Asian
     - Ethnicity for Socioeconomically Disadvantaged
   * - ``200``
     - Black or African American
     - Ethnicity for Socioeconomically Disadvantaged
   * - ``203``
     - Filipino
     - Ethnicity for Socioeconomically Disadvantaged
   * - ``204``
     - Hispanic or Latino
     - Ethnicity for Socioeconomically Disadvantaged
   * - ``205``
     - Native Hawaiian or Pacific Islander
     - Ethnicity for Socioeconomically Disadvantaged
   * - ``206``
     - White
     - Ethnicity for Socioeconomically Disadvantaged
   * - ``207``
     - Two or more races
     - Ethnicity for Socioeconomically Disadvantaged
   * - ``221``
     - American Indian or Alaska Native
     - Ethnicity for Not Socioeconomically Disadvantaged
   * - ``222``
     - Asian
     - Ethnicity for Not Socioeconomically Disadvantaged
   * - ``220``
     - Black or African American
     - Ethnicity for Not Socioeconomically Disadvantaged
   * - ``223``
     - Filipino
     - Ethnicity for Not Socioeconomically Disadvantaged
   * - ``224``
     - Hispanic or Latino
     - Ethnicity for Not Socioeconomically Disadvantaged
   * - ``225``
     - Native Hawaiian or Pacific Islander
     - Ethnicity for Not Socioeconomically Disadvantaged
   * - ``226``
     - White
     - Ethnicity for Not Socioeconomically Disadvantaged
   * - ``227``
     - Two or more races
     - Ethnicity for Not Socioeconomically Disadvantaged
   * - ``004``
     - Female
     - Gender
   * - ``003``
     - Male
     - Gender
   * - ``028``
     - Migrant education
     - Migrant
   * - ``029``
     - Not migrant education
     - Migrant
   * - ``090``
     - Not a high school graduate
     - Parent Education
   * - ``091``
     - High school graduate
     - Parent Education
   * - ``092``
     - Some college (includes AA degree)
     - Parent Education
   * - ``093``
     - College graduate
     - Parent Education
   * - ``094``
     - Graduate school/Postgraduate
     - Parent Education
   * - ``121``
     - Declined to state
     - Parent Education
   * - ``050``
     - Armed forces family member
     - Military Status
   * - ``051``
     - Not armed forces family member
     - Military Status
   * - ``052``
     - Homeless
     - Homeless Status
   * - ``053``
     - Not homeless
     - Homeless Status
   * - ``240``
     - Foster youth
     - Foster Status
   * - ``241``
     - Not foster youth
     - Foster Status


ELPAC student groups
--------------------

.. list-table::
   :header-rows: 1
   :widths: 10 60 30

   * - ID
     - Name
     - Category
   * - ``001``
     - All Students
     - All Students
   * - ``004``
     - Female
     - Gender
   * - ``003``
     - Male
     - Gender
   * - ``228``
     - Spanish
     - Primary Language
   * - ``229``
     - Vietnamese
     - Primary Language
   * - ``230``
     - Mandarin (Putonghua)
     - Primary Language
   * - ``231``
     - Arabic
     - Primary Language
   * - ``232``
     - Filipino (Pilipino or Tagalog)
     - Primary Language
   * - ``233``
     - Cantonese
     - Primary Language
   * - ``234``
     - Korean
     - Primary Language
   * - ``235``
     - Hmong
     - Primary Language
   * - ``236``
     - Punjabi
     - Primary Language
   * - ``237``
     - Russian
     - Primary Language
   * - ``238``
     - All Remaining Languages
     - Primary Language
   * - ``028``
     - Migrant Education
     - Migrant
   * - ``099``
     - Students not Receiving Special Education Services
     - Disability Status
   * - ``128``
     - Students Receiving Special Education Services
     - Disability Status
   * - ``239``
     - Students Receiving Special Education Services Tested with Alternate Assessment for any or all Domains
     - Disability Status
   * - ``031``
     - Economically Disadvantaged
     - Economic Status
   * - ``111``
     - Not Economically Disadvantaged
     - Economic Status
   * - ``074``
     - Black or African American
     - Ethnicity
   * - ``075``
     - American Indian or Alaska Native
     - Ethnicity
   * - ``076``
     - Asian
     - Ethnicity
   * - ``077``
     - Filipino
     - Ethnicity
   * - ``078``
     - Hispanic or Latino
     - Ethnicity
   * - ``079``
     - Native Hawaiian or Other Pacific Islander
     - Ethnicity
   * - ``080``
     - White
     - Ethnicity
   * - ``144``
     - Two or More Races
     - Ethnicity
   * - ``120``
     - English Learners (ELs) Enrolled in School in the U.S. Fewer Than 12 Months
     - English Learners
   * - ``142``
     - English Learners Enrolled in School in the U.S. 12 Months or More
     - English Learners
   * - ``160``
     - All English Learners
     - English Learners
   * - ``050``
     - Military
     - Military Status
   * - ``051``
     - Not Military
     - Military Status
   * - ``052``
     - Homeless
     - Homeless Status
   * - ``053``
     - Not Homeless
     - Homeless Status
   * - ``240``
     - Foster youth
     - Foster Status
   * - ``241``
     - Not foster youth
     - Foster Status

