# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from validator import Validator, Rule

mydb = SQLAlchemy()


class UserInfo(mydb.Model):
    __tablename__ = 'userinfo'
    __json_excludes__ = ['password']
    __validator__ = Validator({
        'id': [Rule('required', groups=['modify'])],
        'username': [Rule('required', groups=['add']),
                     Rule('maxlength', (50,), groups=['add'])],
        'password': [Rule('required', groups=['add']), Rule('maxlength', (50,), groups=['add'])],
        'dept_id': [Rule('required', groups=['add', 'modify'])],
        'gender': [Rule('required', groups=['add', 'modify'])],
        'birth': [Rule('required', groups=['add', 'modify']), Rule('date', groups=['add', 'modify'])],
        'salary': [Rule('required', groups=['add', 'modify']), Rule('number', groups=['add', 'modify']),
                   Rule('min', groups=['add', 'modify'])]
    })
    id = mydb.Column(mydb.BigInteger, primary_key=True)
    username = mydb.Column(mydb.String(50), nullable=False)
    password = mydb.Column(mydb.String(50), nullable=False)
    dept_id = mydb.Column(mydb.BigInteger, mydb.ForeignKey('department.id'), nullable=True)
    gender = mydb.Column(mydb.String(50), nullable=False)
    birth = mydb.Column(mydb.DATE, nullable=False)
    salary = mydb.Column(mydb.DECIMAL, nullable=True)
    # dept = relationship('Department')


class Department(mydb.Model):
    __tablename__ = 'department'
    __json_excludes__ = []
    __validator__ = Validator({
        'id': [Rule('required', groups=["modify"])],
        'dept_name': [
            Rule('required', groups=['add', 'modify']),
            Rule('maxlength', (50,), groups=['add', 'modify'])
        ]
    })
    id = mydb.Column("id", mydb.BigInteger, primary_key=True)
    dept_name = mydb.Column("dept_name", mydb.String(50), nullable=False)
    created_at = mydb.Column(mydb.DateTime, nullable=False)
