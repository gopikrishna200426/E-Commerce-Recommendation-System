import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine(db_uri: str = "sqlite:///database/ecommerce.db", echo: bool = False) -> Engine:
    """Return a SQLAlchemy engine for the configured database URI.

    If SQLite, ensure directory exists.
    """
    if db_uri.startswith("sqlite"):
        # sqlite:///path/to/db.sqlite
        path = db_uri.split("///")[-1]
        dirpath = os.path.dirname(path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
    engine = create_engine(db_uri, echo=echo, future=True)
    return engine
