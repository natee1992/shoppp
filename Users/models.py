from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserInfo(models.Model):
    '''用户信息表'''
    user = models.OneToOneField(User, help_text='用户')
    name = models.CharField(help_text='姓名', max_length=50, default='')
    age = models.IntegerField(help_text='年龄', default=1)
    mobile = models.CharField(help_text='手机号码', max_length=11, default='')
    address = models.CharField(help_text='地址', max_length=128, default='')
    gender = models.CharField(choices=(
        ('男', 'male'), ('女', 'female')), max_length=11, help_text='性别', default='male')
    email = models.EmailField(help_text='邮箱', default='')

    class Meta:
        verbose_name = "UserInfo"
        verbose_name_plural = "UserInfos"

    def __str__(self):
        return self.name


class Seiler(models.Model):
    user = models.OneToOneField(User, help_text='商家')
    name = models.CharField(help_text='员工姓名', max_length=50)
    gender = models.CharField(choices=(
        ('男', 'male'), ('女', 'female')), max_length=11, help_text='性别', default='male')
    email = models.EmailField(help_text='邮箱', default='')
    age = models.IntegerField(help_text='年龄', default=1)
    mobile = models.CharField(help_text='手机号码', max_length=11, default='')

    class Meta:
        verbose_name = "Seiler"
        verbose_name_plural = "Seilers"

    def __str__(self):
        return self.name


class Wallet(models.Model):
    '''钱包'''
    user = models.OneToOneField(User, help_text='用户')
    banlance = models.FloatField(help_text='余额', default=0)

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"

    def __str__(self):
        return self.user


class WalletDetails(models.Model):
    '''钱包流水'''
    wallet = models.OneToOneField(Wallet, help_text='钱包')
    time = models.DateTimeField(datetime.now, help_text='发生时间')
    order = models.OneToOneField('Order', help_text='订单')

    class Meta:
        verbose_name = "WalletDetails"
        verbose_name_plural = "WalletDetailss"

    def __str__(self):
        return self.wallet


class Category(models.Model):
    '''类别'''
    name = models.CharField(help_text='类名', max_length=50, default='')
    desc = models.CharField(max_length=128, help_text='类别描述', default='')
    add_time = models.DateTimeField(datetime.now, help_text='添加时间')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categorys"

    def __str__(self):
        return self.name


class Good(models.Model):
    '''商品'''
    name = models.CharField(help_text='商品名称', max_length=50, default='')
    category = models.ManyToManyField('Category', help_text='类别', default='')
    image = models.CharField(help_text='商品图', max_length=256, default='')
    stock = models.IntegerField(help_text='库存', default=1)
    price = models.FloatField(help_text='价格', default='')
    desc = models.CharField(help_text='商品简介', max_length=50, default='')
    color = models.CharField(help_text='颜色', max_length=50, default='')
    size = models.CharField(help_text='大小', max_length=50, default='')
    add_time = models.DateTimeField(datetime.now, help_text='添加时间')

    class Meta:
        verbose_name = "Good"
        verbose_name_plural = "Goods"

    def __str__(self):
        return self.name


class WatchHistory(models.Model):
    '''浏览历史'''
    user = models.ForeignKey(User, help_text='用户')
    good = models.ForeignKey('Good', help_text='商品')
    add_time = models.DateTimeField(datetime.now, help_text='添加时间')

    class Meta:
        verbose_name = "WatchHistory"
        verbose_name_plural = "WatchHistorys"

    def __str__(self):
        return self.user


class Order(models.Model):
    '''订单'''
    user = models.ForeignKey(User, help_text='用户')
    good = models.ForeignKey('Good', help_text='商品')
    add_time = models.DateTimeField(datetime.now, help_text='添加时间')
    state = models.IntegerField(
        help_text='订单状态:0--->未付款；1--->已付款，代发货；2--->已发货', default=0)
    finish_time = models.CharField(max_length=48, help_text='订单付款时间')

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.user


class Comment(models.Model):
    '''评论'''
    user = models.ForeignKey(User, help_text='用户')
    good = models.ForeignKey('Good', help_text='商品')
    add_time = models.DateTimeField(datetime.now, help_text='添加时间')
    desc = models.CharField(help_text='评论内容', max_length=256)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return user


class UserFav(models.Model):
    '''用户收藏'''
    user = models.ForeignKey(User, help_text='用户')
    good = models.ForeignKey('Good', help_text='商品')
    add_time = models.DateTimeField(datetime.now, help_text='添加时间')

    class Meta:
        verbose_name = "UserFav"
        verbose_name_plural = "UserFavs"

    def __str__(self):
        return user


class ShoppingCat(models.Model):
    '''购物车'''
    user = models.OneToOneField(User, help_text='用户')
    good = models.ManyToManyField('Good', help_text='商品')

    class Meta:
        verbose_name = "ShoppingCat"
        verbose_name_plural = "ShoppingCats"

    def __str__(self):
        return user


class ShoppingHistory(models.Model):
    '''购买历史'''
    user = models.ForeignKey(User, help_text='用户')
    good = models.ForeignKey('Good', help_text='商品')
    add_time = models.DateTimeField(datetime.now, help_text='添加时间')

    class Meta:
        verbose_name = "ShoppingHistory"
        verbose_name_plural = "ShoppingHistorys"

    def __str__(self):
        return self.user
