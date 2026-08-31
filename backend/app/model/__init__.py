"""SQLModel table and schema exports.

The assessment tables model the CAASPP and ELPAC research files directly: see
:mod:`app.model.reference` for the lookups the state publishes alongside those
files and :mod:`app.model.results` for the two fact tables that hold every
reported figure.
"""

from app.model.census_data import (
    CensusCreate,
    CensusData,
    CensusDataPublic,
    CensusDataPublicList,
    CensusUpdate,
)
from app.model.dashboard import (
    DEFAULT_VARIANT,
    DashboardColorCell,
    DashboardCutpoint,
    DashboardIndicator,
    DashboardIndicatorResult,
    DashboardStudentGroup,
)
from app.model.enrollment import EnrollmentRate
from app.model.growth import GrowthResult
from app.model.ingest import IngestFile, IngestRun, IngestStatus
from app.model.item import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.model.local_indicators import (
    LocalIndicatorPriority,
    LocalIndicatorResult,
)
from app.model.other import Message, Token, TokenPayload
from app.model.reference import (
    ApiModel,
    Assessment,
    AssessmentYear,
    CharterFunding,
    Entity,
    EntityLevel,
    GradeLevel,
    MetOrAboveSource,
    PerformanceLevel,
    PerformanceLevelScheme,
    Program,
    StudentGroup,
    SubscoreDefinition,
    SubscoreKind,
)
from app.model.results import AssessmentResult, AssessmentSubscore
from app.model.school import School, SchoolCreate, SchoolPublic, SchoolsPublic
from app.model.user import (
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
)

__all__ = [
    "ApiModel",
    "Assessment",
    "AssessmentResult",
    "AssessmentSubscore",
    "AssessmentYear",
    "CensusCreate",
    "CensusData",
    "CensusDataPublic",
    "CensusDataPublicList",
    "CensusUpdate",
    "DEFAULT_VARIANT",
    "CharterFunding",
    "DashboardColorCell",
    "DashboardCutpoint",
    "DashboardIndicator",
    "DashboardIndicatorResult",
    "DashboardStudentGroup",
    "EnrollmentRate",
    "Entity",
    "EntityLevel",
    "GradeLevel",
    "GrowthResult",
    "IngestFile",
    "IngestRun",
    "IngestStatus",
    "Item",
    "LocalIndicatorPriority",
    "LocalIndicatorResult",
    "ItemCreate",
    "ItemPublic",
    "ItemUpdate",
    "ItemsPublic",
    "Message",
    "MetOrAboveSource",
    "PerformanceLevel",
    "PerformanceLevelScheme",
    "Program",
    "School",
    "SchoolCreate",
    "SchoolPublic",
    "SchoolsPublic",
    "StudentGroup",
    "SubscoreDefinition",
    "SubscoreKind",
    "Token",
    "TokenPayload",
    "UpdatePassword",
    "User",
    "UserCreate",
    "UserPublic",
    "UserRegister",
    "UserUpdate",
    "UsersPublic",
]
