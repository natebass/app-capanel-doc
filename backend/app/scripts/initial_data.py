import logging

from sqlmodel import Session

from app.core.database import engine, init_db
from app.scripts.gcp_utils import load_repo_env_if_present

load_repo_env_if_present(__file__, scope="initial_data")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    """Creating initial data."""
    init()


if __name__ == "__main__":
    main()
