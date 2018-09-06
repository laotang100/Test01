# coding: utf-8
from datetime import date, datetime
from flask_sqlalchemy import BaseQuery
from decimal import Decimal

from sqlalchemy import BIGINT, Column, DECIMAL, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class JsonModel:

    @staticmethod
    def format_obj(val, pattern=None):
        if val is None:
            return None
        obj = val
        if isinstance(val, datetime):
            obj = val.strftime(pattern if (pattern is not None) else "%Y-%m-%d %H:%M:%S")
        elif isinstance(val, date):
            obj = val.strftime(pattern if (pattern is not None) else "%Y-%m-%d")
        elif isinstance(val, BaseQuery):
            obj = [i.jsondata() for i in val]
        elif isinstance(val, JsonModel):
            obj = val.jsondata()
        elif isinstance(val, Decimal):
            obj = str(val)
        # else:
        #     obj = str(obj)
        return obj

    def __init__(self):
        self.ignores = []
        self.formats = {}

    def jsondata(self):
        d = dict()
        for c in self.__table__.columns:
            v = getattr(self, c.name)
            d[c.name] = JsonModel.format_obj(v)
        return d


class Department(Base, JsonModel):
    __tablename__ = 'department'

    id = Column(BIGINT(20), primary_key=True)
    dept_name = Column(String(50))
    created_at = Column(DateTime)


class Userinfo(Base, JsonModel):
    __tablename__ = 'userinfo'

    id = Column(BIGINT(20), primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    dept_id = Column(ForeignKey('department.id'), index=True)
    gender = Column(String(50))
    birth = Column(Date)
    salary = Column(DECIMAL(10, 2))

    dept = relationship('Department')
