import re
from decimal import Decimal
from datetime import date, datetime
from flask import request
from functools import wraps


class Rule:
    def __init__(self, rule_name, params=(), groups=None, message=None):
        self.rule_name = rule_name
        self.params = params
        if groups is None:
            groups = ["DEFAULT"]
        self.groups = groups
        self.message = message


class Validator:

    @staticmethod
    def check_date(*args):
        s = args[0]
        match_obj = re.match('^(\d{1,4})-(\d{1,2})-(\d{1,2})$', s)
        if match_obj is None:
            return False
        else:
            year, month, day = int(match_obj.group(1)), int(match_obj.group(2)), int(match_obj.group(3))
            try:
                date(year, month, day)
            except ValueError as e:
                print(e)
                return False
            else:
                return True

    @staticmethod
    def check_datetime(*args):
        s = args[0]
        match_obj = re.match('^(\d{1,4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})$', s)
        if match_obj is None:
            return False
        else:
            year, month, day, hour, minute, second = int(match_obj.group(1)), int(match_obj.group(2)), int(
                match_obj.group(
                    3)), int(match_obj.group(4)), int(match_obj.group(5)), int(match_obj.group(6))
            try:
                datetime(year, month, day, hour, minute, second)
            except ValueError as e:
                print(e)
                return False
            else:
                return True

    @staticmethod
    def create_error(field, template, params):
        s = template
        s = s.replace('$0', field)
        for i, v in enumerate(params):
            s = s.replace('$' + str(i + 1), str(v))
        s = field+':'+s
        return s

    @staticmethod
    def get_field_value(obj, field):
        if isinstance(obj, dict):
            return obj.get(field)
        elif obj == request:
            return request.form.get(field, request.args.get(field))  # 先从post表单里取，没有再看url里的
        elif obj == request.form:
            return request.form.get(field)
        else:
            return getattr(obj, field)

    default_messages = {
        'required': '$0不能为空',
        'minlength': '最小长度不能小于$1',
        'maxlength': '最大长度不能超过$1',
        'min': '不能小于$1',
        'max': '不能大于$1',
        'reg': '格式错误',
        'email': '非法的Email',
        'ipv4': '非法的IP地址',
        'ipv6': '非法的IP地址',
        'int': '必须是整数',
        'number': '必须是数字',
        'variable': '必须是数字字母或下划线，且数组不能打头',
        'date': '必须是yyyy-MM-dd的格式',
        'datetime': '必须是yyyy-MM-dd HH:mm:ss的格式'
    }

    @classmethod
    def register_rule(cls, rule_name, check_func, message, replace=False):
        if rule_name in cls.check_funs and not replace:
            raise Exception(rule_name+' has exists, use \"replace=True\" to replace rule')

        cls.check_funs[rule_name] = check_func
        cls.default_messages[rule_name] = message

    check_funs = {
        'required': lambda v, params: v is not None and len(v) > 0,
        'minlength': lambda v, params: v is not None and len(v) > params[0],
        'maxlength': lambda v, params: v is not None and len(v) < params[0],
        'min': lambda v, params: re.match('^-?(?:(?:[1-9]\d*)|[0])(?:\.\d+)?$', v
                                          ) is not None and Decimal(v) >= Decimal(params[0]),
        'max': lambda v, params: re.match('^-?(?:(?:[1-9]\d*)|[0])(?:\.\d+)?$', v
                                          ) is not None and Decimal(v) <= Decimal(params[0]),
        'reg': lambda v, params: re.match(params[0], v, re.M) is not None,
        'email': lambda v, params: re.match('[^@]+@[^@]+\.[^@]+$', v, re.M) is not None,
        'ipv4': lambda v, params: re.match(
            '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            v) is not None,
        'ipv6': lambda v, params: re.match('^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$', v) is not None,
        'int': lambda v, params: re.match('^(?:-?[1-9]\d*)|0$', v) is not None,
        'number': lambda v, params: re.match('^-?(?:(?:[1-9]\d*)|[0])(?:\.\d+)?$', v) is not None,
        'variable': lambda v, params: re.match('^[a-zA-Z_]\w*$', v) is not None,
        'date': check_date,
        'datetime': check_datetime
    }

    # field_rules = {
    # 'id': [ Role('required', groups=['modify'])  ]
    # 'name': [ Role('required', groups=['add', 'modify'], message='name must not empty'),
    #           Role('maxlength', params=(20,), groups=['add', 'modify'], message=' $1 charater '),
    # ]
    # }
    def __init__(self, field_rules=None):
        self.errors = []
        if field_rules is None:
            self.field_rules = {}

    # 添加规则
    def add_rules(self, field, *rules):
        for rule in rules:
            if field not in self.field_rules:
                self.field_rules[field] = []
            self.field_rules[field].append(rule)

    def validate_all(self, obj):
        succeed = True
        self.errors.clear()
        for field, rules in self.field_rules.items():
            for rule in rules:
                # try:
                if rule.rule_name in Validator.check_funs:
                    result = Validator.check_funs[rule.rule_name](Validator.get_field_value(obj, field), rule.params)
                # except Exception as e:
                #     print(e)
                #     result = False
                #     rule.message = str(e)
                    if not result:
                        self.errors.append(Validator.create_error(field,  rule.params, rule.message))
                        succeed = False
                else:  # 当未找到验证函数的时候忽略
                    pass
        return succeed

    def validate(self, obj, group="DEFAULT"):
        self.errors.clear()
        for field, rules in self.field_rules.items():
            for rule in rules:
                if group in rule.groups:
                    if rule.rule_name not in Validator.check_funs:
                        raise Exception('unknow rule '+rule.rule_name)
                    result = Validator.check_funs[rule.rule_name](
                        Validator.get_field_value(obj, field), rule.params)
                    if not result:
                        self.errors.append(Validator.create_error(field, rule.params, rule.message))
                        return False
        else:
            return True

    def html_errors(self):
        return "<p>Errors:"+'</p>\n<p>'.join(self.errors)+'</p>'
# def validate_model(model, group):
#     validator = Validator()
#     for col in getattr(model, '__table__').columns:
#         validator.add_rules(col.name, Rule('required', groups=['modify']))
#     return False


def request_validator(dt):  # dt = {field:[Role1,Role2]}
    def wrapper(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # if not 'user' in session:
            #     abort(401)
            va = Validator()
            for field, vl in enumerate(dt):
                va.add_rules(field, *tuple(vl))
            if va.validate(request):
                return func(*args, **kwargs)
            else:
                return va.html_errors(), 401
        return decorated_function
    return wrapper
