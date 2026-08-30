.. meta::
   :description lang=en: Cautions that apply when reading CAASPP and ELPAC results.

Interpreting Results
================================================================

The research files are precise about what they contain, and quietly unforgiving
about what they do not.  These are the traps worth knowing before drawing a
conclusion from a number.

A blank is not a zero
---------------------

Three different absences look similar in a spreadsheet.

**Withheld.**  A ``*`` means the state suppressed the figure because fewer than
11 students were in the group.  The students exist and were tested; the result
is simply not publishable.  This application flags the row as ``suppressed``.

**Not applicable.**  An empty field means the figure is not reported for that
row.  The clearest case is the mean scale score on an "all grades" row: scale
scores are set separately for each grade and are not comparable across grades,
so no cross-grade mean is published.  The percentages on the same row are fine.

**Absent.**  No row at all means the entity did not report that combination —
a school with no eleventh grade has no grade 11 row.

Treating any of these as zero produces a school that appears to have failed
every student.

Which denominator
-----------------

Three counts are published and they answer different questions.

* **Students enrolled** — eligible to test.
* **Students tested** — actually administered the test.  Participation rate is
  tested ÷ enrolled.
* **Students tested with scores** — answered enough questions for a valid
  score.  This is the denominator of the mean scale score.
* **Overall total** — students counted across all achievement levels.  This is
  the denominator of the level percentages.

The last two are usually equal but not always; use the one the state used.

Charter schools are counted twice by design
-------------------------------------------

Direct-funded independent charter schools are reported as their own districts.
Their results are included in the state and county totals *and* appear again as
school rows under that district code.  Adding up districts and adding up schools
therefore give different totals.

The state's own reports offer an "All Schools / Charter Schools / Non-Charter
Schools" filter.  The research files publish only the all-schools aggregate, so
a charter-filtered figure has to be rebuilt from the school rows.  This
application does that on request and marks the result ``derivedFromChildren``;
counts add exactly, and the mean scale score is recomputed as a mean weighted by
the number of tests with valid scores, which is close to but not identical to
the figure the state would publish.

Comparability across years
--------------------------

**2019–20 has no data.**  Testing was suspended statewide because of COVID-19.
Any trend line must skip that year rather than interpolate through it.

**The CSA changed in 2024–25.**  The blueprint was redesigned: score ranges
became achievement levels, domains and composites began to be reported, and the
scale itself changed.  Scores from 2024–25 onward are not comparable with
earlier administrations, and this application returns an explicit note on trend
responses that cross the break.

**ELPAC thresholds changed for 2018–19.**  Scores before and after are not
comparable.

**ELPAC kindergarten changed for 2024–25.**  Transitional kindergarten students
are no longer included.

Comparability across entities
-----------------------------

The CSA is optional and is built on content standards that are not universally
taught; Spanish literacy programs differ enormously between schools and
districts.  The state explicitly recommends against comparing CSA results
between organisations.

The alternate assessments are taken by a small, specific population — students
whose individualized education program designates the alternate.  Percentages
over small groups move sharply for reasons that have nothing to do with
instruction.

Proficiency figures are not all published
-----------------------------------------

Smarter Balanced and CAST publish "Standard Met and Above" directly.  The
alternate assessments, the CSA and the ELPAC do not.  This application derives a
comparable figure by summing the levels at or above the state's proficiency cut
and labels it ``derived`` so the distinction stays visible.  For the score
ranges the CSA used through 2023–24 the state defines no cut at all, so no
proficiency figure is offered.

Recently arrived English learners
---------------------------------

For CAASPP reporting, a recently arrived English learner is one whose first date
of entry into a United States school falls after 15 April of the year before the
assessment.  Those students need not take the ELA assessment, but if they do
take it their results are included in these figures.
