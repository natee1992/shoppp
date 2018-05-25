from random import randint
from datetime import datetime

from Api.resources import Resource
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.db.transaction import atomic

from Users.models import *
from Api.utils import *
from Api.decorators import seiler_permission


class SessionCodeResource(Resource):
    '''验证码获取'''

    def get(self, request, *args, **kwargs):
        # 构建数据字典
        data = dict()
        code = randint(1000, 10000)
        # 将验证码放入session中
        request.session['regist_code'] = code
        data = {
            'regist_code': code
        }
        # 返回json数据
        return json_response(data)


class UserResource(Resource):
    '''用户注册、更新、查看信息'''

    # 用户注册
    @atomic
    def put(self, request, *args, **kwargs):
        data = request.PUT
        username = data.get('username', '')
        password = data.get('password', '')
        ensure_password = data.get('ensure_password', '')
        code = int(data.get('code', ''))
        regist_code = request.session.get('regist_code', '')
        user = User.objects.filter(username=username)
        category = data.get('category', 'userinfo')
        # 构建用户字典
        errors = dict()
        # 判断两次输入密码是否一致
        if password != ensure_password:
            errors['password'] = '两次输入密码不一致'
        # 判断密码长度
        elif len(password) < 6:
            errors['password'] = '密码输入长度不足6位'
        # 判断验证码
        if code != regist_code:
            errors['regist_code'] = '验证码错误'
        # 判断用户名是否存在
        if not username:
            errors['username'] = '用户名为空'
        elif user:
            errors['username'] = '用户名已存在'
        if errors:
            return params_errors(errors)
        user = User.objects.create_user(username=username, password=password)
        user.save()
        if category == 'userinfo':
            userinfo = UserInfo()
            userinfo.user = user
            userinfo.name = '顾客姓名'
            userinfo.save()
        if category == 'seiler':
            seiler = Seiler()
            seiler.user = user
            seiler.name = '员工姓名'
            seiler.save()
        login(request, user)
        return json_response({
            'user_id': user.id
        })

    # 用户更新
    @atomic
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            data = request.POST
            if hasattr(user, 'userinfo'):
                userinfo = user.userinfo
                userinfo.name = data.get('name', '')
                try:
                    userinfo.age = abs(int(data.get('age', '')))
                except Exception as e:
                    userinfo.age = 18
                userinfo.mobile = data.get('mobile', '')
                userinfo.address = data.get('address', '')
                userinfo.gender = data.get('gender', 'female')
                email = data.get('email', '')
                userinfo.save()
            elif hasattr(user, 'seiler'):
                seiler = user.seiler
                seiler.name = data.get('name', '')
                seiler.gender = data.get('gender', '')
                seiler.email = data.get('email', '')
                try:
                    seiler.age = abs(int(data.get('age', '')))
                except Exception as e:
                    seiler.age = 20
                seiler.mobile = data.get('mobile', '')
                seiler.save()
            return json_response({
                'user_id': user.id
            })
        return not_authenticated()

    # 查看用户信息
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            # 构建用户信息字典
            data = dict()
            if hasattr(user, 'userinfo'):
                userinfo = user.userinfo
                data['name'] = getattr(userinfo, 'name', '')
                data['age'] = getattr(userinfo, 'age', '')
                data['mobile'] = getattr(userinfo, 'mobile', '')
                data['address'] = getattr(userinfo, 'address', '')
                data['gender'] = getattr(userinfo, 'gender', '')
                data['email'] = getattr(userinfo, 'email', '')
                return json_response(data)
            elif hasattr(user, 'seiler'):
                seiler = user.seiler
                data['name'] = getattr(seiler, 'name', '')
                data['age'] = getattr(seiler, 'age', '')
                data['mobile'] = getattr(seiler, 'mobile', '')
                data['address'] = getattr(seiler, 'address', '')
                data['gender'] = getattr(seiler, 'gender', '')
                data['email'] = getattr(seiler, 'email', '')
                return json_response(data)
            else:
                return json_response({
                    'state': 401,
                    'msg': '没有此用户信息'
                })
        return not_authenticated()


class SessionResource(Resource):
    # 查看登录状态
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return json_response({
                'msg': '已经登录'
            })
        else:
            return json_response({
                'msg': '未登录'
            })

    def put(self, request, *args, **kwargs):
        # 登录用户
        data = request.PUT
        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return json_response({
                'msg': '登录成功'
            })
        else:
            return params_errors({
                'msg': '用户名或者密码错误'
            })

    def delete(self, request, *args, **kwargs):
        # 退出登录
        logout(request)
        return json_response({
            'msg': '退出成功'
        })


class CategoryResource(Resource):
    '''类别：查看 创建 更新'''
    # 创建类别
    @atomic
    @seiler_permission
    def put(self, request, *args, **kwargs):
        data = request.PUT
        category_name = data.get('name', '')
        category_desc = data.get('desc', '')
        category = Category.objects.filter(name=category_name)
        if category:
            return json_response({
                'msg': '商品类别存在'
            })
        category = Category()
        category.name = category_name
        category.desc = category_desc
        category.save()
        return json_response({
            'category_id': category.id
        })

    # 更新类别
    @atomic
    @seiler_permission
    def post(self, request, *args, **kwargs):
        data = request.POST
        category_id = int(data.get('category_id', False))
        if not category_id:
            return params_errors({
                'msg': '没有提供要修改的类名'
            })
        categorys = Category.objects.filter(id=category_id)
        if not categorys:
            return params_errors({
                'msg': '类名不存在'
            })
        category = categorys[0]
        category.name = data.get('name', '')
        category.desc = data.get('desc', '')
        category.save()
        return json_response({
            'category_name': category.name
        })

    # 查看商品类别
    def get(self, request, *args, **kwargs):
        # 构建类别数据字典
        data = []
        categorys = Category.objects.all()
        if categorys:
            for category in categorys:
                category_data = dict()
                category_data['name'] = category.name
                category_data['desc'] = category.desc
                category_data['id'] = category.id
                try:
                    add_time = datetime.strftime(category.add_time, '%Y-%m-%d')
                except Exception as e:
                    add_time = '2018-01-01'
                category_data['add_time'] = add_time
                try:
                    change_time = datetime.strftime(
                        category.change_time, '%Y-%m-%d')
                except Exception as e:
                    change_time = '2018-01-01'
                category_data['change_time'] = change_time
                data.append(category_data)
            return json_response({
                'data': data
            })
        else:
            return json_response({
                'msg': '商品类别为空'
            })
