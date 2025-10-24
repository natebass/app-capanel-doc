import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.utility.models import CensusData, Item, Message, User  # noqa

router = APIRouter(prefix='/censusdata', tags=['censusdata'])


@router.get('/', response_model=list[CensusData])
def count_of_census_data(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve census data.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    count_statement = select(func.count()).select_from(CensusData)
    count = session.exec(count_statement).one()

    statement = select(CensusData).offset(skip).limit(limit)
    census_data = session.exec(statement).all()

    return {'data': census_data, 'count': count}


@router.get('/{id}', response_model=CensusData)
def read_census_data(session: SessionDep, current_user: CurrentUser, id: str) -> Any:
    """
    Get census data by ID.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    census_data = session.get(CensusData, id)
    if not census_data:
        raise HTTPException(status_code=404, detail='Census data not found')

    return census_data


@router.post('/', response_model=CensusData)
def create_census_data(
    *, session: SessionDep, current_user: CurrentUser, census_data_in: CensusData
) -> Any:
    """
    Create new census data.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    census_data = CensusData.from_orm(census_data_in)
    session.add(census_data)
    session.commit()
    session.refresh(census_data)

    return census_data


@router.put('/{id}', response_model=CensusData)
def update_census_data(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: str,
    census_data_in: CensusData,
) -> Any:
    """
    Update census data by ID.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    census_data = session.get(CensusData, id)
    if not census_data:
        raise HTTPException(status_code=404, detail='Census data not found')

    new_census_data = CensusData.from_orm(census_data_in)
    session.add(new_census_data)
    session.commit()
    session.refresh(new_census_data)

    return new_census_data


@router.delete('/{id}', response_model=CensusData)
def delete_census_data(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Delete census data by ID.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    census_data = session.get(CensusData, id)
    if not census_data:
        raise HTTPException(status_code=404, detail='Census data not found')
    if not current_user.is_superuser and (census_data.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail='Not enough permissions')
    session.delete(census_data)
    session.commit()

    return Message(message='Census data deleted successfully')
