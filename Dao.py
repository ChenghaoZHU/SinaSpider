__author__ = 'chzhu'

import sqlalchemy
import Config
from Config import TABLES
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
Base = declarative_base()

ENGINE_INFO = 'mysql+pymysql://' + Config.DB_USER + ':' + Config.DB_PASSWD + '@' + Config.DB_HOST + '/' + Config.DB_DATABASE + '?charset=' + Config.DB_CHARSET
ENGINE = sqlalchemy.create_engine(ENGINE_INFO)

class Database(object):

    def __init__(self):
        self.engine = ENGINE

    def connect(self):
        self.connection = self.engine.connect()
        Session = sessionmaker(bind=self.engine, autocommit=False)
        self.session = Session()

    def close(self):
        self.session.commit()
        self.session.close()
        self.connection.close()
class Followee(Base):
    __table__ = Table(TABLES['followee'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)
class Follower(Base):
    __table__ = Table(TABLES['follower'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)
class Job(Base):
    __table__ = Table(TABLES['job'], Base.metadata, autoload=True, autoload_with=ENGINE)
    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)
class Education(Base):
    __table__ = Table(TABLES['education'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)
class User(Base):
    __table__ = Table(TABLES['user'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)
class Timeline(Base):
    __table__ = Table(TABLES['timeline'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)
class Task(Base):
    __table__ = Table(TABLES['task'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)
class Account(Base):
    __table__ = Table(TABLES['account'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)
