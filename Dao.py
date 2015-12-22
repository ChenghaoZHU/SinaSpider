__author__ = 'chzhu'

import sqlalchemy
import Config
from Config import TABLES
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table

class Paras(object):
    '''
    this class is equal to Parameter in this file, but it's designed for disconnection of db session
    '''
    def __init__(self, i, s, gsid):
        self.i = i
        self.s = s
        self.gsid = gsid

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

    @classmethod
    def get_all(cls):
        db = Database()
        db.connect()

        cursor = db.session.query(cls).filter(cls.is_available == '1', cls.is_deleted == '0').all()
        result = []
        for cs in cursor:
            cs.is_available = '0'
            result.append(cs.uid)

        db.close()
        return result


class Account(Base):
    __table__ = Table(TABLES['account'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)

class Parameter(Base):
    __table__ = Table(TABLES['parameter'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def get_all(cls):
        db = Database()
        db.connect()

        cursor = db.session.query(cls).filter(cls.is_available == '1').all()
        result = []
        for cs in cursor:
            cs.is_available = '0'
            i = cs.i
            s = cs.s
            gsid = cs.gsid
            result.append(Paras(i, s, gsid))

        db.close()
        return result
