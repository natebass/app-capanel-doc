import uuid

from pydantic.alias_generators import to_camel
from sqlmodel import Field, Session, SQLModel, col, select
from sqlmodel.main import SQLModelConfig


class CensusDataBase(SQLModel):
    """
    Shared properties for CensusData (Normalized)
    """

    academic_year: int = Field(index=True)
    aggregation_level: str = Field(index=True)
    cds_code: str = Field(index=True, max_length=14)
    charter: str | None = Field(default=None, max_length=255)
    reporting_category: str = Field(max_length=255)
    total_enr: int = Field(default=0)
    gr_tk: int = Field(default=0)
    gr_kn: int = Field(default=0)
    gr_1: int = Field(default=0)
    gr_2: int = Field(default=0)
    gr_3: int = Field(default=0)
    gr_4: int = Field(default=0)
    gr_5: int = Field(default=0)
    gr_6: int = Field(default=0)
    gr_7: int = Field(default=0)
    gr_8: int = Field(default=0)
    gr_9: int = Field(default=0)
    gr_10: int = Field(default=0)
    gr_11: int = Field(default=0)
    gr_12: int = Field(default=0)

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)


class CensusData(CensusDataBase, table=True):
    __tablename__ = "census_data"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    @classmethod
    def get_total_students_in_school(
        cls, session: Session, school_code: str, reporting_category: str
    ) -> dict[str, int | None]:
        """
        Return a dictionary with key 'total-students' that is either row.total_enr or None.
        """
        row = session.exec(
            select(cls).where(
                col(cls.cds_code) == school_code,
                col(cls.reporting_category) == reporting_category,
            )
        ).first()
        if row:
            return {"total-students": row.total_enr}
        else:
            return {"total-students": None}

    @classmethod
    def get_total_students_in_school_by_grade(
        cls, session: Session, school_code: str, reporting_category: str
    ) -> dict[str, list[int]]:
        """
        Return a dictionary with key 'total_students_by_grade' and value as a list of student counts for grades TK through 12 for this row.
        """
        found_row = session.exec(
            select(cls).where(
                col(cls.cds_code) == school_code,
                col(cls.reporting_category) == reporting_category,
            )
        ).first()
        if not found_row:
            return {"total_students_by_grade": []}

        return {
            "total_students_by_grade": [
                found_row.gr_tk,
                found_row.gr_kn,
                found_row.gr_1,
                found_row.gr_2,
                found_row.gr_3,
                found_row.gr_4,
                found_row.gr_5,
                found_row.gr_6,
                found_row.gr_7,
                found_row.gr_8,
                found_row.gr_9,
                found_row.gr_10,
                found_row.gr_11,
                found_row.gr_12,
            ]
        }

    @classmethod
    def get_total_students_in_district(
        cls, session: Session, district_code: str, reporting_category: str
    ) -> dict[str, int | None]:
        """
        Return a dictionary with key 'total-students' that is either row.total_enr or None.
        0 is a valid value.
        If no row is found, return {'total-students': None}.
        """
        row = session.exec(
            select(cls).where(
                col(cls.cds_code) == district_code,
                col(cls.reporting_category) == reporting_category,
            )
        ).first()
        if row:
            return {"total-students": row.total_enr}
        else:
            return {"total-students": None}

    @classmethod
    def get_total_students_in_district_by_grade(
        cls, session: Session, district_code: str, reporting_category: str
    ) -> dict[str, list[int]]:
        """
        Return a dictionary with key 'total_students_by_grade' and value as a list of student counts for grades TK through 12 for this district.
        If no row is found, return {'total_students_by_grade': []}.
        """
        found_row = session.exec(
            select(cls).where(
                col(cls.cds_code) == district_code,
                col(cls.reporting_category) == reporting_category,
            )
        ).first()
        if not found_row:
            return {"total_students_by_grade": []}

        return {
            "total_students_by_grade": [
                found_row.gr_tk,
                found_row.gr_kn,
                found_row.gr_1,
                found_row.gr_2,
                found_row.gr_3,
                found_row.gr_4,
                found_row.gr_5,
                found_row.gr_6,
                found_row.gr_7,
                found_row.gr_8,
                found_row.gr_9,
                found_row.gr_10,
                found_row.gr_11,
                found_row.gr_12,
            ]
        }

    @classmethod
    def get_total_students_in_county(
        cls, session: Session, county_code: str, reporting_category: str
    ) -> dict[str, int | None]:
        """
        Return a dictionary with key 'total-students' that is either row.total_enr or None.
        0 is a valid value.
        If no row is found, return {'total-students': None}.
        """
        row = session.exec(
            select(cls).where(
                col(cls.cds_code) == county_code,
                col(cls.reporting_category) == reporting_category,
            )
        ).first()
        if row:
            return {"total-students": row.total_enr}
        else:
            return {"total-students": None}

    @classmethod
    def get_total_students_in_county_by_grade(
        cls, session: Session, county_code: str, reporting_category: str
    ) -> dict[str, list[int]]:
        """
        Return a dictionary with key 'total_students_by_grade' and value as a list of student counts for grades TK through 12 for this county.
        If no row is found, return {'total_students_by_grade': []}.
        """
        found_row = session.exec(
            select(cls).where(
                col(cls.cds_code) == county_code,
                col(cls.reporting_category) == reporting_category,
            )
        ).first()
        if not found_row:
            return {"total_students_by_grade": []}

        return {
            "total_students_by_grade": [
                found_row.gr_tk,
                found_row.gr_kn,
                found_row.gr_1,
                found_row.gr_2,
                found_row.gr_3,
                found_row.gr_4,
                found_row.gr_5,
                found_row.gr_6,
                found_row.gr_7,
                found_row.gr_8,
                found_row.gr_9,
                found_row.gr_10,
                found_row.gr_11,
                found_row.gr_12,
            ]
        }


class CensusCreate(CensusDataBase):
    """
    Properties to receive on item creation
    """

    pass


class CensusUpdate(CensusDataBase):
    """
    Properties to receive on item update
    """

    pass


class CensusDataPublic(CensusDataBase):
    """
    Properties to return via API, id is always required
    """

    id: uuid.UUID


class CensusDataPublicList(SQLModel):
    data: list[CensusDataPublic]
    count: int

    model_config = SQLModelConfig(alias_generator=to_camel, populate_by_name=True)
