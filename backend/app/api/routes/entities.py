"""Endpoints for finding and navigating reporting entities.

Entities are the state, its counties, the districts inside them and the schools
inside those, all keyed by the 14-character CDS code the research files use.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from sqlmodel import col, func, or_, select

from app.api.deps import SessionDep
from app.model.reference import Entity, EntityLevel
from app.model.reports import EntityAncestry, EntityList, EntityPublic
from app.service.reports import entity_public

router = APIRouter(prefix="/entities", tags=["entities"])

CACHE_CONTROL = "public, max-age=300"


def load_entity(session: SessionDep, cds_code: str) -> Entity:
    """Fetch an entity or raise a 404."""
    entity = session.get(Entity, cds_code)
    if entity is None:
        raise HTTPException(status_code=404, detail=f"Unknown entity {cds_code}")
    return entity


@router.get("/search")
def search_entities(
    session: SessionDep,
    response: Response,
    q: str | None = Query(default=None, description="Name or CDS code fragment."),
    level: EntityLevel | None = None,
    county_code: str | None = Query(default=None, alias="countyCode"),
    district_code: str | None = Query(default=None, alias="districtCode"),
    charter: bool | None = None,
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> EntityList:
    """Find entities by name or CDS code."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    statement = select(Entity)
    if q:
        needle = f"%{q.strip().lower()}%"
        statement = statement.where(
            or_(
                func.lower(col(Entity.display_name)).like(needle),
                func.lower(func.coalesce(col(Entity.district_name), "")).like(needle),
                col(Entity.cds_code).like(f"{q.strip()}%"),
            )
        )
    if level is not None:
        statement = statement.where(Entity.entity_level == level)
    if county_code:
        statement = statement.where(Entity.county_code == county_code.zfill(2))
    if district_code:
        statement = statement.where(Entity.district_code == district_code.zfill(5))
    if charter is not None:
        statement = statement.where(col(Entity.is_charter).is_(charter))

    count = session.exec(select(func.count()).select_from(statement.subquery())).one()
    rows = session.exec(
        statement.order_by(col(Entity.entity_level), col(Entity.display_name))
        .offset(offset)
        .limit(limit)
    ).all()
    return EntityList(data=[entity_public(entity) for entity in rows], count=count)


@router.get("/{cds_code}")
def read_entity(
    session: SessionDep, response: Response, cds_code: str
) -> EntityAncestry:
    """One entity together with the entities it rolls up into."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds_code)

    ancestors: list[EntityPublic] = []
    cursor = entity
    while cursor.parent_cds_code:
        parent = session.get(Entity, cursor.parent_cds_code)
        if parent is None:
            break
        ancestors.append(entity_public(parent))
        cursor = parent
    return EntityAncestry(entity=entity_public(entity), ancestors=ancestors)


@router.get("/{cds_code}/children")
def read_children(
    session: SessionDep,
    response: Response,
    cds_code: str,
    q: str | None = None,
    charter: bool | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> EntityList:
    """The entities directly inside this one."""
    response.headers["Cache-Control"] = CACHE_CONTROL
    entity = load_entity(session, cds_code)
    statement = select(Entity).where(Entity.parent_cds_code == entity.cds_code)
    if q:
        statement = statement.where(
            func.lower(col(Entity.display_name)).like(f"%{q.strip().lower()}%")
        )
    if charter is not None:
        statement = statement.where(col(Entity.is_charter).is_(charter))

    count = session.exec(select(func.count()).select_from(statement.subquery())).one()
    rows = session.exec(
        statement.order_by(col(Entity.display_name)).offset(offset).limit(limit)
    ).all()
    return EntityList(data=[entity_public(child) for child in rows], count=count)
