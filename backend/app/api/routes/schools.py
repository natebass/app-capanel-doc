from typing import Any

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.utility.models import School, SchoolsPublic, SchoolsSummary

router = APIRouter()


@router.get('/', response_model=SchoolsPublic)
def read_schools(
    session: SessionDep,
    q: str | None = None,
    skip: int = 0,
    limit: int = 10,
) -> Any:
    """
    Retrieve schools.
    """
    if q:
        statement = (
            select(School)
            .where(func.lower(School.school).contains(q.lower()))
            .where(School.status_type == 'Active')
            .offset(skip)
            .limit(limit)
        )
    else:
        statement = select(School).offset(skip).limit(limit)

    schools = session.exec(statement).all()
    count = len(schools)

    return SchoolsPublic(data=schools, count=count)


@router.get('/summary', response_model=SchoolsSummary)
def read_schools_summary(
    session: SessionDep,
    q: str | None = None,
    skip: int = 0,
    limit: int = 10,
) -> Any:
    """
    Retrieve schools with a summarized view.
    """
    if q:
        statement = (
            select(School)
            .where(func.lower(School.school).contains(q.lower()))
            .where(School.status_type == 'Active')
            .offset(skip)
            .limit(limit)
        )
    else:
        statement = select(School).offset(skip).limit(limit)

    schools = session.exec(statement).all()
    count = len(schools)

    return SchoolsSummary(data=schools, count=count)
