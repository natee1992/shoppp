from random import randint
from datetime import datetime

from Api.resources import Resource
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.db.transaction import atomic

from Users.models import *
from Api.utils import *
from Api.decorators import *


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
            wallet = Wallet()
            wallet.user = userinfo.user
            wallet.save()
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
                data['username'] = user.username
                data['wallet'] = user.wallet.banlance
                return json_response(data)
            elif hasattr(user, 'seiler'):
                seiler = user.seiler
                data['name'] = getattr(seiler, 'name', '')
                data['age'] = getattr(seiler, 'age', '')
                data['mobile'] = getattr(seiler, 'mobile', '')
                data['address'] = getattr(seiler, 'address', '')
                data['gender'] = getattr(seiler, 'gender', '')
                data['email'] = getattr(seiler, 'email', '')
                data['username'] = user.username
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


class WalletResource(Resource):
    '''钱包操作'''
    # 充值
    @atomic
    @userinfo_permission
    def post(self, request, *args, **kwargs):
        data = request.POST
        user = request.user
        wallet = user.wallet
        # 充值金额处理
        try:
            banlance_this = abs(int(data.get('banlance', 0)))
        except Exception as e:
            return params_errors({
                'msg': '充值金额数据类型错误'
            })
        wallet.banlance += banlance_this
        wallet.save()
        return json_response({
            'banlance': wallet.banlance
        })

    # 查看钱包余额
    @userinfo_permission
    def get(self, request, *args, **kwargs):
        user = request.user
        banlance = user.wallet.banlance
        return json_response({
            'banlance': banlance
        })


class GoodResource(Resource):
    '''
    商品管理
    '''
    @atomic
    @seiler_permission
    def put(self, request, *args, **kwargs):
        error_dict = {}
        data = request.PUT
        name = data.get('name', '')
        goods = Good.objects.filter(name=name)
        try:
            category_id = int(data.get('category_id', 0))
            category = Category.objects.filter(pk=category_id)
        except Exception:
            error_dict['category'] = '类别id错误'
        try:
            stock = int(data.get('stock', 1))
            price = float(data.get('price', 0))
        except Exception:
            error_dict['stock'] = '库存或者价格类型错误'
        if not category:
            error_dict['category'] = '不存在商品类别'
        if goods:
            error_dict['good'] = '已经添加过的商品'
        if error_dict:
            return params_errors(error_dict)
        if not name:
            error_dict['name'] = '未输入商品的名称'
        good = Good()
        good.name = name
        good.image = data.get('image', '')
        good.stock = stock
        good.price = price
        good.desc = data.get('desc', '')
        good.color = data.get('color', '')
        good.size = data.get('size', '')
        good.save()
        good.category.set(category)
        good.save()
        return json_response({
            'msg': '添加商品成功'
        })

     # 所有商品
    def get(self, request, *args, **kwargs):
        all_goods = Good.objects.all()
        data = []
        for good in all_goods:
            good_dict = {}
            good_dict['id'] = good.id
            good_dict['name'] = good.name
            good_dict['image'] = good.image
            data.append(good_dict)
        return json_response(data)

    @atomic
    @seiler_permission
    def post(self, request, *args, **kwargs):
        error_dict = {}
        data = request.POST
        try:
            good_id = int(data.get('good_id', 0))
            good = Good.objects.get(pk=good_id)
        except Exception:
            return params_errors({
                'msg': '不存在的id'
            })
        try:
            category_id = int(data.get('category_id', 0))
            category = Category.objects.filter(pk=category_id)
        except Exception:
            error_dict['category'] = '类别id错误'
        try:
            stock = int(data.get('stock', 1))
            price = float(data.get('price', 0))
        except Exception:
            error_dict['stock'] = '库存或者价格类型错误'
        if error_dict:
            return params_errors(error_dict)
        good.name = data.get('name')
        good.image = data.get('image', '')
        good.stock = stock
        good.price = price
        good.desc = data.get('desc', '')
        good.color = data.get('color', '')
        good.size = data.get('size', '')
        good.save()
        good.category.set(category)
        good.save()
        return json_response({
            'id': good.id,
            'name': good.name,
            'msg': '商品更新成功'
        })

    @atomic
    @seiler_permission
    def delete(self, request, *args, **kwargs):
        data = request.DELETE
        try:
            good_id = int(data.get('good_id', 0))
            good = Good.objects.get(pk=good_id)
        except Exception:
            return params_errors({
                'msg': '商品不存在'
            })
        good.delete()
        return json_response({
            'msg': '删除成功'
        })


# class OrderResource(Resource):
#     '''用户订单操作'''
#     # 创建订单
#     @atomic
#     @userinfo_permission
#     def put(self, request, *args, **kwargs):
#         user = request.user
#         data = request.PUT
#         good = data.get('good_id', False)
#         if
#         order = Order()
#         order.user = user

        # data = request.GET
        # try:
        #     good_id = int(data.get('good_id', 0))
        #     good = Good.objects.get(pk=good_id)
        # except Exception:
        #     return params_errors({
        #         'msg': '不存在的id'
        #     })
        # good_dict = {}
        # good_dict['id'] = good.id
        # good_dict['name'] = good.name
        # good_dict['image'] = good.image
        # good_dict['stock'] = good.stock
        # good_dict['price'] = good.price
        # good_dict['desc'] = good.desc
        # good_dict['color'] = good.color
        # good_dict['size'] = good.size
        # good_dict['add_time'] = datetime.strftime(good.add_time, '%Y-%m-%d')
        # good_dict['category'] = [{
        #     category.id,
        #     category.name,
        #     category.desc
        # } for category in good.category_set.all()]
        # return json_response(good_dict)
