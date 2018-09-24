from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

engine = create_engine('postgresql://postgres:postgres@localhost:5432/sstodo')

session_factory = sessionmaker(bind=engine)
DBSession = scoped_session(session_factory)
# DBSession = sessionmaker(bind=engine)
db_session = DBSession()

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    username = Column('username', String(24), unique=True, nullable=False)
    password = Column('password', String(24), nullable=False)
    user = relationship('ToDo', backref='User', cascade='all,delete')

    def __init__(self, data):
        self.username = data['username']
        self.password = data['password']

    def __str__(self):
        return f'"username": "{self.username}", "password": "{self.password}"'

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'username': str(self.username),
            'password': str(self.password)
        }

    @classmethod
    def filter_by_username(cls, username, session):
        username = session.query(cls).filter(cls.username == username).first()
        return username


class ToDo(Base):
    __tablename__ = 'todo'
    todo_id = Column('todo_id', Integer, primary_key=True, autoincrement=True)
    title = Column('title', String(100), nullable=False)
    description = Column('description', String(300), nullable=True)
    done = Column('done', Boolean, nullable=False)
    user_id = Column('user_id', Integer, ForeignKey('user.id'))

    def __init__(self, user_id, data):
        self.title = data['title']
        self.description = data['description']
        self.done = data['done']
        self.user_id = user_id

    @classmethod
    def filter_by_id(cls, todo_id, session):
        todo_id = session.query(cls).filter(cls.todo_id == todo_id).first()
        return todo_id
