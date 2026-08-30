"""Reference data endpoints.

One call returns everything the report controls need for a year: the tests
reported that year with their achievement levels and reporting categories, the
student groups, and the grades.
"""

from fastapi import APIRouter, HTTPException, Query, Response

from app.api.deps import SessionDep
from app.model.reference import Program
from app.model.reports import AssessmentPublic, Catalog
from app.service import reports as report_service
from app.service.reference import reference_data

router = APIRouter(prefix="/reference", tags=["reference"])

# Reference data only changes when the importer runs, so it is safe to cache
# in the browser and in any proxy for a few minutes.
CACHE_CONTROL = "public, max-age=300"


@router.get("/catalog")
def read_catalog(
    session: SessionDep,
    response: Response,
    year: int | None = Query(
        default=None, description="Administration year; defaults to the most recent."
    ),
) -> Catalog:
    """Everything needed to populate the report filters for one year."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    data = reference_data(session)

    years = report_service.available_years(session)
    if not years:
        raise HTTPException(
            status_code=404,
            detail="No assessment results have been imported yet.",
        )
    test_year = year if year in years else years[0]

    assessments: list[AssessmentPublic] = []
    for test_id in report_service.available_tests(session, test_year):
        assessment = data.assessment(test_id)
        year_row = data.assessment_years.get((test_id, test_year))
        scheme = data.scheme_for(test_id, test_year)
        if assessment is None or scheme is None:
            continue
        assessments.append(
            AssessmentPublic(
                test_id=assessment.test_id,
                code=assessment.code,
                program=assessment.program,
                test_type=assessment.test_type,
                name=assessment.name,
                short_name=assessment.short_name,
                subject=assessment.subject,
                is_alternate=assessment.is_alternate,
                sort_order=assessment.sort_order,
                level_scheme=scheme,
                subscores=list(data.subscores_for(test_id, test_year)),
                grades=sorted(
                    report_service.available_grades(session, test_year, test_id),
                    key=lambda code: (
                        data.grades[code].sort_order if code in data.grades else 999
                    ),
                ),
                grades_note=year_row.grades_note if year_row else None,
            )
        )
    assessments.sort(key=lambda assessment: assessment.sort_order)

    return Catalog(
        test_year=test_year,
        years=years,
        assessments=assessments,
        student_groups=[
            *data.groups_for(Program.CAASPP),
            *data.groups_for(Program.ELPAC),
        ],
        grades=sorted(data.grades.values(), key=lambda grade: grade.sort_order),
    )
