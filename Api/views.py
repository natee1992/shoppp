from random import randint

from Api.resources import Resource
from django.contrib.auth.models import User

from Users.models import *
from Api.utils import json_response, params_errors


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

    def put(self, request, *args, **kwargs):
        data = request.PUT
        username = data.get('username', '')
        password = data.get('password', '')
        ensure_password = data.get('ensure_password', '')
        code = data.get('code', '')
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
