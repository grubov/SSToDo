"""A Database sub-manager added as a command to Flask Application Manager"""

import os
from flask_script import Manager
from .models import Base, engine
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

basedir = os.path.abspath(os.path.dirname(__file__))

manager = Manager(usage="Perform database operations")
engine_init = create_engine('postgresql://postgres:postgres@localhost:5432/postgres', isolation_level='AUTOCOMMIT')


@manager.command
def init():
    """Creates database and inserts tables from SQLAlchemy models"""
    try:
        with engine_init.connect() as conn:
            conn.execute(f'CREATE DATABASE sstodo')
    except ProgrammingError:
        print(f'ProgrammingError(SQLAlchemy): Database may be already exist')
    Base.metadata.create_all(engine)


@manager.command
def update():
    """Recreates and updates database tables from SQLAlchemy models"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@manager.command
def drop():
    """Drops database tables"""
    Base.metadata.drop_all(engine)