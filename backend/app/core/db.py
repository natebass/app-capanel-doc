import csv
from pathlib import Path

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.utility import crud
from app.utility.models import School, User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

    # Populate schools using the provided model, if the table is empty
    if not session.exec(select(School)).first():
        file_path = Path('app/resources/pubschls.txt')
        if not file_path.exists():
            # Silently return if the file doesn't exist
            return

        schools_to_create = []
        try:
            with open(file_path, encoding='utf-8') as tsv_file:
                reader = csv.DictReader(tsv_file, delimiter='\t')

                for row in reader:
                    # Helper to convert "No Data" or empty strings to None
                    def clean_value(value: str | None) -> str | None:
                        return (
                            value
                            if value and value.strip().lower() != 'no data'
                            else None
                        )

                    # Helper to safely convert a string to a float
                    def to_float(value: str | None) -> float | None:
                        if value is None:
                            return None
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return None

                    # A CDSCode is required as it's the unique identifier
                    cds_code = clean_value(row.get('CDSCode'))
                    if not cds_code:
                        continue  # Skip rows without a primary identifier

                    school_in = School(
                        # Map all fields from the TSV row to the School model
                        cds_code=cds_code,
                        nces_dist=clean_value(row.get('NCESDist')),
                        nces_school=clean_value(row.get('NCESSchool')),
                        status_type=clean_value(row.get('StatusType')),
                        county=clean_value(row.get('County')),
                        district=clean_value(row.get('District')),
                        school=clean_value(row.get('School')),
                        street=clean_value(row.get('Street')),
                        street_abr=clean_value(row.get('StreetAbr')),
                        city=clean_value(row.get('City')),
                        zip=clean_value(row.get('Zip')),
                        state=clean_value(row.get('State')),
                        mail_street=clean_value(row.get('MailStreet')),
                        mail_street_abr=clean_value(row.get('MailStrAbr')),
                        mail_city=clean_value(row.get('MailCity')),
                        mail_zip=clean_value(row.get('MailZip')),
                        mail_state=clean_value(row.get('MailState')),
                        phone=clean_value(row.get('Phone')),
                        ext=clean_value(row.get('Ext')),
                        fax_number=clean_value(row.get('FaxNumber')),
                        website=clean_value(row.get('WebSite')),
                        open_date=clean_value(row.get('OpenDate')),
                        closed_date=clean_value(row.get('ClosedDate')),
                        charter=clean_value(row.get('Charter')),
                        charter_num=clean_value(row.get('CharterNum')),
                        funding_type=clean_value(row.get('FundingType')),
                        doc=clean_value(row.get('DOC')),
                        doc_type=clean_value(row.get('DOCType')),
                        soc=clean_value(row.get('SOC')),
                        soc_type=clean_value(row.get('SOCType')),
                        edops_code=clean_value(row.get('EdOpsCode')),
                        edops_name=clean_value(row.get('EdOpsName')),
                        eil_code=clean_value(row.get('EILCode')),
                        eil_name=clean_value(row.get('EILName')),
                        gs_offered=clean_value(row.get('GSoffered')),
                        gs_served=clean_value(row.get('GSserved')),
                        virtual=clean_value(row.get('Virtual')),
                        magnet=clean_value(row.get('Magnet')),
                        year_round_yn=clean_value(row.get('YearRoundYN')),
                        federal_dfc_district_id=clean_value(
                            row.get('FederalDFCDistrictID')
                        ),
                        latitude=to_float(clean_value(row.get('Latitude'))),
                        longitude=to_float(clean_value(row.get('Longitude'))),
                        adm_fname=clean_value(row.get('AdmFName')),
                        adm_lname=clean_value(row.get('AdmLName')),
                        last_up_date=clean_value(row.get('LastUpDate')),
                        multilingual=clean_value(row.get('Multilingual')),
                    )
                    schools_to_create.append(school_in)

            # Use add_all for efficient bulk insertion
            session.add_all(schools_to_create)
            session.commit()

        except Exception:
            # If any error occurs, roll back the entire transaction
            session.rollback()
