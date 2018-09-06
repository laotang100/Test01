import json
from datetime import date, datetime
from decimal import Decimal
from flask_sqlalchemy import BaseQuery, Model, Pagination


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H-%M-%S')
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, Model):
            d = dict()
            for col in getattr(o, '__table__').columns:
                if not hasattr(o, '__json_excludes__') or col.name not in getattr(o, '__json_excludes__'):
                    d[col.name] = getattr(o, col.name)
            return d
        if isinstance(o, BaseQuery):
            return [m for m in o]
        if isinstance(o, Pagination):
            return {
                'pages': o.pages,
                'has_next': o.has_next,
                'has_prev': o.has_prev,
                'items': o.items,
                'next_num': o.next_num,
                'page': o.page,
                'per_page': o.per_page,
                'prev_num': o.prev_num,
                'total': o.total
            }
        # 上面这些满足不了只能走下面的默认抛异常了
        return json.JSONEncoder.default(self, o)
