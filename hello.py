from flask import Flask, request, render_template, jsonify
from flask_script import Manager
from validator import Validator, Rule, request_validator
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from json_ext import JSONEncoder
from req_reader import RequestReader, request_extractor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'laotang100'

# 数据库设置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3308/test1?charset=utf8mb4'  # URL和驱动
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 追踪对象的修改并且发送信号
app.config['SQLALCHEMY_POOL_SIZE'] = 5  # 连接池最大连接数
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30  # 超时
app.config['SQLALCHEMY_POOL_RECYCLE'] = -1  # 回收
app.config['SQLALCHEMY_ECHO'] = True

# app.config['HOST'] = '0.0.0.0'
# app.config['PORT'] = 8888
# app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY'] = True

app.json_encoder = JSONEncoder

mydb = SQLAlchemy()
mydb.init_app(app)


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
        'dept_name': [Rule('required', groups=['add', 'modify']),
                      Rule('maxlength', (50,), groups=['add', 'modify'])]
    })
    id = mydb.Column("id", mydb.BigInteger, primary_key=True)
    dept_name = mydb.Column("dept_name", mydb.String(50), nullable=False)
    created_at = mydb.Column(mydb.DateTime, nullable=False)


@app.route('/')
def hello():
    return render_template('index.html', name='tang > weI ', list=list(range(5)))


@app.route('/savefile', methods=["POST"])
@request_extractor(dept=Department, dept_id=int)
def savefile(dept):
    print(dept)
    for f in request.files:
        print(f)
    Department.query.filter(Department.id == 1).update({Department.dept_name: dept.dept_name})
    # mydb.session.add(dept)
    mydb.session.commit()
    return 'bbb'


@app.route('/saveform', methods=["POST"])
@request_validator({
    'username': [Rule('required'), Rule('maxlength', (20,))],
    'email': [Rule('required'), Rule('email')],
    'salary': [Rule('required'), Rule('number')]
})
def testform():
    inputtext = request.form.get('inputtext')
    print(inputtext)
    singleselect = request.form.get('singleselect')
    print(singleselect)
    mutiselect = request.form.getlist('mutiselect')
    print(mutiselect)

    dept = Department()
    print(dept)

    for column in dept.__table__.columns:
        print(column.name, column.type.python_type)

    # va = Validator()
    # va.add_roles("inputtext",
    #              {'role':'required', 'message':'inputtext 不能为空'},
    #              {'role':'maxlength','params':(10,)},
    #              {'role':'minlength','params':(2,)},
    #              {'role':'max','params':(200,)},
    #              {'role':'min','params':(100,)},
    #              {'role':'reg','params':('^abcd\w*$',)},
    #              {'role':'email'},
    #              {'role':'ipv4'},
    #              {'role':'ipv6'},
    #              {'role':'int'},
    #              {'role':'number'},
    #              {'role':'variable'},
    #              {'role':'date'},
    #              {'role':'datetime'},
    #
    #              )
    # if not va.validate_all(request):
    #     return '<p>'+'</p><p>'.join(va.errors)+'</p>'
    # # list()
    # else:
    return 'aaaa'


@app.route('/test03')
def test03():
    u = UserInfo.query.get(2)
    return jsonify(u)


@app.route('/test04')
def test04():
    # 三个参数: 1. 当前要查询的页数 2. 每页的数量 3. 是否要返回错误
    pagination = Department.query.paginate(2, 3, False)
    print(pagination.items)  # 获取查询的结果
    print(pagination.pages)  # 总页数
    print(pagination.page)  # 当前页数
    return jsonify(pagination)


@app.route('/test05')
def test05():
    p = mydb.session.query(UserInfo.id, UserInfo.username, UserInfo.gender, UserInfo.birth,
                           Department.id.label('dept_id'), Department.dept_name, Department.created_at).join(
        Department, Department.id == UserInfo.dept_id
    ).filter(UserInfo.gender == 'Male').order_by(UserInfo.username).paginate(2, 3, False)
    return jsonify(p)


manager = Manager(app)

if __name__ == '__main__':
    manager.run()
