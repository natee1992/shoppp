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


class ShoppingCatResource(Resource):
    '''用户购物车操作'''
    # 添加商品到购物车
    @atomic
    @userinfo_permission
    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.PUT
        good_id = data.get('good_id', False)
        num = int(data.get('num', 1))
        if not good_id:
            return params_errors({
                'msg': '没有选择商品'
            })
        try:
            good_id = abs(int(good_id))
        except Exception as e:
            return params_errors({
                'msg': '商品id格式错误'
            })
        good = Good.objects.filter(id=good_id)
        if not good:
            return json_response({
                'msg': '商品不存在'
            })
        shoppingcat = ShoppingCat.objects.filter(user=user)
        if not shoppingcat:
            shoppingcat = ShoppingCat()
            shoppingcat.user = user
            shoppingcat.save()
            shoppingcatdetail = ShoppingCatDetail()
            shoppingcatdetail.shoppingcat = shoppingcat
            shoppingcatdetail.good = good[0]
            shoppingcatdetail.num = num
            shoppingcatdetail.save()
            shoppingcat.total_price = good[0].price * num
            shoppingcat.save()
        else:
            shoppingcatdetail = ShoppingCatDetail.objects.filter(
                good=good[0], shoppingcat=shoppingcat[0])
            if shoppingcatdetail:
                shoppingcatdetail.num += num
                shoppingcatdetail.save()
                shoppingcat.total_price += good[0].price * num
                shoppingcat.save()
            else:
                shoppingcatdetail = ShoppingCatDetail()
                shoppingcatdetail.shoppingcat = shoppingcat[0]
                shoppingcatdetail.good = good[0]
                shoppingcatdetail.num = num
                shoppingcatdetail.save()
                shoppingcat[0].total_price += good[0].price * num
                shoppingcat[0].save()
        return json_response({
            'msg': '添加购物车成功'
        })

    # 查看购物车
    @userinfo_permission
    def get(self, request, *args, **kwargs):
        user = request.user
        shoppingcat = user.shoppingcat
        # 构建购物车信息列表
        all_data = {}
        all_data['data'] = []
        shoppingcatdetails = ShoppingCatDetail.objects.filter(
            shoppingcat=shoppingcat)
        if not shoppingcatdetails:
            return json_response({
                'msg': '购物车为空'
            })
        # 遍历所有属于该用户的商品列表
        for shoppingcatdetail in shoppingcatdetails:
            data = {}
            data['name'] = shoppingcatdetail.good.name
            data['num'] = shoppingcatdetail.num
            data['price'] = shoppingcatdetail.good.price
            data['good_price'] = shoppingcatdetail.good.price * \
                shoppingcatdetail.num
            all_data['data'].append(data)
        total_price = shoppingcat.total_price
        all_data['price'] = (total_price)
        return json_response({
            'data': all_data
        })


class OrderResource(Resource):
    '''
    订单
    '''
    # 获取订单
    @userinfo_permission
    def get(self, request, *args, **kwargs):
        data = request.GET
        user = request.user
        if not user.is_authenticated():
            return not_authenticated()
        # 是否是查看单个订单
        is_single = data.get('is_single', False)
        # 单个, 需要传入 order_id
        if is_single:
            order_id = data.get('order_id', False)
            order = Order.objects.filter(pk=order_id, )
            if (not order_id or not order):
                return params_errors({
                    'msg': '不存在订单id'
                })
            # 构建详细信息字典
            data_dict = {}
            order = order[0]
            data_dict['id'] = order.id
            data_dict['user'] = order.user.username
            data_dict['add_time'] = datetime.strftime(
                order.add_time, '%Y-%m-%d')
            data_dict['state'] = order.state
            data_dict['all_price'] = order.all_price
            # 该订单的详情(orderdetail)
            data_dict['detail_data'] = []
            for orderdetail in order.orderdetail_set.all():
                orderdetail_dict = {}
                orderdetail_dict['good'] = orderdetail.good.name
                orderdetail_dict['num'] = orderdetail.num
                orderdetail_dict['price'] = orderdetail.price
            data_dict['detail_data'].append(orderdetail_dict)
            return json_response(data_dict)
        # 用户的订单列表(所有的订单)
        else:
            all_order = Order.objects.filter(user=user)
            data = []
            for order in all_order:
                order_dict = {}
                order_dict['id'] = order.id
                order_dict['all_price'] = order.all_price
                order_dict['user'] = {
                    'id': user.id,
                    'name': user.userinfo.name
                }
                data.append(order_dict)
            return json_response(data)

    # 创建订单
    @atomic
    @userinfo_permission
    def put(self, request, *args, **kwargs):
        user = request.user
        shoppingcat = user.shoppingcat
        order = Order()
        order.user = user
        order.add_time = datetime.now()
        order.state = 0
        order.all_price = shoppingcat.total_price
        order.save()
        # 购物车详情, 此处存着用户刚刚提交的所有的上碰的信息
        shopping_cat_details = user.shoppingcat.shoppingcatdetail_set.all()
        for shopping_cat_detail in shopping_cat_details:
            orderdetail = OrderDetail()
            orderdetail.order = order
            orderdetail.good = shopping_cat_detail.good
            orderdetail.num = shopping_cat_detail.num
            orderdetail.price = shopping_cat_detail.good.price * shopping_cat_detail.num
            orderdetail.save()
        # 删除购物车和购物车详情
        shopping_cat_details.delete()
        user.shoppingcat.delete()
        return json_response({
            'msg': '创建订单成功'
        })

    # 付款和发货
    @atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        order_id = data.get('order_id')
        user = request.user
        orders = Order.objects.filter(id=order_id)
        if not orders:
            return params_errors({
                'msg': '不存在的订单'
            })
        order = orders[0]

        # 1. 订单处于未付款, 需要付款

        #@userinfo_permission
        def pay(request, *args, **kwargs):
            order = orders.filter(user=user)
            if not order:
                return params_errors({
                    'msg': '不存在的订单'
                })
            order = order[0]
            # 钱包操作
            wallet = user.wallet
            # 判断此人钱包余额是否可以支付
            if wallet.banlance > float(order.all_price):
                wallet.banlance -= float(order.all_price)
                wallet.save()
                # 创建一条钱包流水记录
                waleltdetails = WalletDetails()
                waleltdetails.wallet = wallet
                waleltdetails.order = order
                waleltdetails.save()
                # 改为付款状态
                order.state = 1
                order.finish_time = datetime.now()
                order.save()
                # 首先获取订单详情, 以便添加购买历史
                orderdetails = order.orderdetail_set.all()
                for orderdetail in orderdetails:
                    # 添加购买历史
                    shopping_history = ShoppingHistory()
                    shopping_history.user = user
                    shopping_history.good = orderdetail.good
                    shopping_history.save()
                return json_response({
                    'msg': '付款成功',
                    'pay_money': order.all_price,
                    'balance': wallet.banlance,
                    'waleltdetails_id': waleltdetails.id,
                    'order_id': order.id

                })
            else:
                return params_errors({
                    'msg': '余额不足'
                })

        # 发货
        # @seiler_permission
        def send_out(request, *args, **kwargs):
            order = orders[0]
            order.state = 2
            order.save()
            return json_response({
                'msg': '发货成功'
            })

        # 此处判断订单的状态
        if order.state == 0 and hasattr(user, 'userinfo'):
            return pay(request, *args, **kwargs)
        elif order.state == 1 and hasattr(user, 'seiler'):
            return send_out(request, *args, **kwargs)
        elif order.state == 2:
            return params_errors({
                'msg': '订单已经发货'
            })
        else:
            return permission_refused()


class UserFavResource(Resource):
    '''用户收藏'''
    # 添加收藏
    @atomic
    @userinfo_permission
    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.PUT
        good_id = data.get('good_id', False)
        if not good_id:
            return params_errors({
                'msg': '没有选择商品'
            })
        try:
            good_id = abs(int(good_id))
        except Exception as e:
            return params_errors({
                'msg': '商品id格式错误'
            })
        good = Good.objects.filter(id=good_id)
        if not good:
            return json_response({
                'msg': '商品不存在'
            })
        userfav = UserFav()
        userfav.user = user
        goods = Good.objects.filter(id=good_id)
        good = goods[0]
        userfav.good = good
        userfav.save()
        return json_response({
            'msg': '添加收藏成功'
        })

    # 查看收藏
    @userinfo_permission
    def get(self, request, *args, **kwargs):
        user = request.user
        # 取出用户所有收藏商品
        userfavs = UserFav.objects.filter(user=user)
        # 构建收藏数据字典
        all_data = {}
        all_data['data'] = []
        for userfav in userfavs:
            data = {}
            data['good'] = userfav.good.name
            all_data['data'].append(data)
        return json_response({
            'data': all_data
        })

    # 删除收藏
    @userinfo_permission
    def delete(self, request, *args, **kwargs):
        user = request.user
        data = request.DELETE
        good_id = data.get('good_id', False)
        if not good_id:
            return params_errors({
                'msg': '没有选择商品'
            })
        try:
            good_id = abs(int(good_id))
        except Exception as e:
            return params_errors({
                'msg': '商品id格式错误'
            })
        good = Good.objects.filter(id=good_id)
        if not good:
            return json_response({
                'msg': '商品不存在'
            })
        userfav_good = UserFav.objects.filter(good__id=good_id)
        userfav_good[0].delete()
        return json_response({
            'msg': '已从收藏夹删除该商品'
        })
