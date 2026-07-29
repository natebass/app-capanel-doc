import uuid

from pydantic.alias_generators import to_camel
from sqlmodel import Field, SQLModel
from sqlmodel.main import SQLModelConfig


class SchoolBase(SQLModel):
    """
    A school.
    Use a separate field for each part of the physical and mailing address.
    """

    # Unique identifier
    cds_code: str = Field(max_length=255, unique=True, index=True)
    nces_dist: str = Field(max_length=255)
    nces_school: str = Field(max_length=255)
    school_code: str = Field(max_length=255)

    # General school info
    status_type: str | None = Field(default=None, max_length=255)
    county: str | None = Field(default=None, max_length=255)
    district: str | None = Field(default=None, max_length=255)
    school: str | None = Field(default=None, max_length=255)

    # Physical address fields
    street: str | None = Field(default=None)
    street_abr: str | None = Field(default=None)
    city: str | None = Field(default=None, max_length=255)
    zip: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, max_length=255)

    # Mailing address fields
    mail_street: str | None = Field(default=None)
    mail_street_abr: str | None = Field(default=None)
    mail_city: str | None = Field(default=None, max_length=255)
    mail_zip: str | None = Field(default=None, max_length=255)
    mail_state: str | None = Field(default=None, max_length=255)

    # Contact info
    phone: str | None = Field(default=None, max_length=255)
    ext: str | None = Field(default=None, max_length=255)
    fax_number: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)

    # Dates
    open_date: str | None = Field(default=None, max_length=255)
    closed_date: str | None = Field(default=None, max_length=255)

    # Charter and funding
    charter: str | None = Field(default=None, max_length=255)
    charter_num: str | None = Field(default=None, max_length=255)
    funding_type: str | None = Field(default=None, max_length=255)

    # Various codes and types
    doc: str | None = Field(default=None, max_length=255)
    doc_type: str | None = Field(default=None, max_length=255)
    soc: str | None = Field(default=None, max_length=255)
    soc_type: str | None = Field(default=None, max_length=255)
    edops_code: str | None = Field(default=None, max_length=255)
    edops_name: str | None = Field(default=None, max_length=255)
    eil_code: str | None = Field(default=None, max_length=255)
    eil_name: str | None = Field(default=None, max_length=255)

    # Grade and program info
    gs_offered: str | None = Field(default=None, max_length=255)
    gs_served: str | None = Field(default=None, max_length=255)
    virtual: str | None = Field(default=None, max_length=255)
    magnet: str | None = Field(default=None, max_length=255)
    year_round_yn: str | None = Field(default=None, max_length=255)

    # Location and admin
    federal_dfc_district_id: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    adm_fname: str | None = Field(default=None, max_length=255)
    adm_lname: str | None = Field(default=None, max_length=255)

    # Metadata
    last_up_date: str | None = Field(default=None, max_length=255)
    multilingual: str | None = Field(default=None, max_length=255)

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class School(SchoolBase, table=True):
    __tablename__ = "schools"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class SchoolCreate(SchoolBase):
    pass


class SchoolPublic(SchoolBase):
    id: uuid.UUID


class SchoolsPublic(SQLModel):
    data: list[SchoolPublic]
    count: int

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class SchoolSummary(SQLModel):
    id: uuid.UUID
    school: str | None = None
    city: str | None = None
    county: str | None = None
    cds_code: str | None = None
    school_code: str | None = None

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class SchoolsSummary(SQLModel):
    data: list[SchoolSummary]
    count: int

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)
