from datetime import date, datetime
from decimal import Decimal
from flask_sqlalchemy import Model
from flask import request
from functools import wraps


class RequestReader:
    @staticmethod
    def is_empty_str(s):
        return s is None or len(s) == 0

    def __init__(self, req):
        self.req = req

    def read_str(self, field, default_value=None):
        s = self.req.form.get(field)
        return s if s is not None else self.req.args.get(field, default_value)

    def read_int(self, field, default_value=None):
        str_value = self.read_str(field)
        return int(str_value) if not RequestReader.is_empty_str(str_value) else default_value

    def read_bigint(self, field, default_value=None):
        str_value = self.read_str(field)
        return int(str_value) if not RequestReader.is_empty_str(str_value) else default_value

    def read_decimal(self, field, default_value=None):
        str_value = self.read_str(field)
        return Decimal(str_value) if not RequestReader.is_empty_str(str_value) else default_value

    def read_datetime(self, field, fmt='%Y-%m-%d %H:%M:%S', default_value=None):
        str_value = self.read_str(field)
        return datetime.strptime(str_value, fmt) if not RequestReader.is_empty_str(str_value) else default_value

    def read_date(self, field, fmt='%Y-%m-%d', default_value=None):
        str_value = self.read_str(field)
        return self.read_datetime(field, fmt).date() if not RequestReader.is_empty_str(str_value) else default_value

    def read_any(self, field, cls=str, default_value=None):
        if cls == str:
            return self.read_str(field, default_value)
        elif cls == int:
            return self.read_int(field, default_value)
        elif cls == date:
            return self.read_date(field, default_value=default_value)
        elif cls == datetime:
            return self.read_datetime(field, default_value=default_value)
        elif cls == Decimal:
            return self.read_decimal(field, default_value)
        elif issubclass(cls, Model):
            return self.read_model(cls)

    def read_model(self, model_cls):
        model = None
        for column in getattr(model_cls, '__table__').columns:

            fd, cls = column.name, column.type.python_type
            fv = self.read_any(fd, cls)
            if fv is not None:
                if model is None:
                    model = model_cls()
                setattr(model, fd, fv)
        return model


def request_extractor(**types):
    def wrapper(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            for name, cls in types.items():
                req_reader = RequestReader(request)
                group = None
                if isinstance(cls, set):
                    cls = cls[0]
                    group = cls[1]
                obj = req_reader.read_any(name, cls)

                vali = getattr(cls, '__validator__', None)
                if group is not None and vali is not None:
                    if obj is None:
                        return 'can not read '+cls+' from request', 401
                    if not vali.validate(obj, group):
                        return vali.html_errors(), 401

                kwargs[name] = obj
            return func(*args, **kwargs)

        return decorated_function

    return wrapper
