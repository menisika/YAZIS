from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from src.dispatch.config import settings

engine = create_engine(settings.database_url, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
