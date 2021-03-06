# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-25 10:13
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', help_text='类名', max_length=50)),
                ('desc', models.CharField(default='', help_text='类别描述', max_length=128)),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, help_text='添加时间')),
                ('change_time', models.DateTimeField(auto_now=True, help_text='修改时间')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categorys',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, help_text='添加时间')),
                ('desc', models.CharField(help_text='评论内容', max_length=256)),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
            },
        ),
        migrations.CreateModel(
            name='Good',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', help_text='商品名称', max_length=50)),
                ('image', models.CharField(default='', help_text='商品图', max_length=256)),
                ('stock', models.IntegerField(default=1, help_text='库存')),
                ('price', models.FloatField(default=1.0, help_text='价格')),
                ('desc', models.CharField(default='', help_text='商品简介', max_length=50)),
                ('color', models.CharField(default='', help_text='颜色', max_length=50)),
                ('size', models.CharField(default='', help_text='大小', max_length=50)),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, help_text='添加时间')),
                ('category', models.ManyToManyField(default='', help_text='类别', to='Users.Category')),
            ],
            options={
                'verbose_name': 'Good',
                'verbose_name_plural': 'Goods',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, help_text='添加时间')),
                ('state', models.IntegerField(default=0, help_text='订单状态:0--->未付款；1--->已付款，代发货；2--->已发货')),
                ('finish_time', models.CharField(help_text='订单付款时间', max_length=48)),
                ('all_price', models.CharField(default=0, help_text='商品总额', max_length=50)),
                ('user', models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(default=0)),
                ('price', models.FloatField(default=0)),
                ('good', models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, to='Users.Good')),
                ('order', models.ForeignKey(help_text='订单', on_delete=django.db.models.deletion.CASCADE, to='Users.Order')),
            ],
            options={
                'verbose_name': 'OrderDetail',
                'verbose_name_plural': 'OrderDetails',
            },
        ),
        migrations.CreateModel(
            name='Seiler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='员工姓名', max_length=50)),
                ('gender', models.CharField(choices=[('男', 'male'), ('女', 'female')], default='male', help_text='性别', max_length=11)),
                ('email', models.EmailField(default='', help_text='邮箱', max_length=254)),
                ('age', models.IntegerField(default=1, help_text='年龄')),
                ('mobile', models.CharField(default='', help_text='手机号码', max_length=11)),
                ('user', models.OneToOneField(help_text='商家', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Seiler',
                'verbose_name_plural': 'Seilers',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.FloatField(default=0)),
                ('user', models.OneToOneField(help_text='用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ShoppingCat',
                'verbose_name_plural': 'ShoppingCats',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCatDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(default=0)),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, help_text='添加时间')),
                ('good', models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, to='Users.Good')),
                ('shoppingcat', models.ForeignKey(help_text='购物车', on_delete=django.db.models.deletion.CASCADE, to='Users.ShoppingCat')),
            ],
            options={
                'verbose_name': 'ShoppingCatDetail',
                'verbose_name_plural': 'ShoppingCatDetails',
            },
        ),
        migrations.CreateModel(
            name='ShoppingHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, help_text='添加时间')),
                ('good', models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, to='Users.Good')),
                ('user', models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ShoppingHistory',
                'verbose_name_plural': 'ShoppingHistorys',
            },
        ),
        migrations.CreateModel(
            name='UserFav',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, help_text='添加时间')),
                ('good', models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, to='Users.Good')),
                ('user', models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'UserFav',
                'verbose_name_plural': 'UserFavs',
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', help_text='姓名', max_length=50)),
                ('age', models.IntegerField(default=1, help_text='年龄')),
                ('mobile', models.CharField(default='', help_text='手机号码', max_length=11)),
                ('address', models.CharField(default='', help_text='地址', max_length=128)),
                ('gender', models.CharField(choices=[('男', 'male'), ('女', 'female')], default='male', help_text='性别', max_length=11)),
                ('email', models.EmailField(default='', help_text='邮箱', max_length=254)),
                ('user', models.OneToOneField(help_text='用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'UserInfo',
                'verbose_name_plural': 'UserInfos',
            },
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banlance', models.FloatField(default=0, help_text='余额')),
                ('user', models.OneToOneField(help_text='用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Wallet',
                'verbose_name_plural': 'Wallets',
            },
        ),
        migrations.CreateModel(
            name='WalletDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=datetime.datetime.now, help_text='发生时间')),
                ('order', models.OneToOneField(help_text='订单', on_delete=django.db.models.deletion.CASCADE, to='Users.Order')),
                ('wallet', models.OneToOneField(help_text='钱包', on_delete=django.db.models.deletion.CASCADE, to='Users.Wallet')),
            ],
            options={
                'verbose_name': 'WalletDetails',
                'verbose_name_plural': 'WalletDetailss',
            },
        ),
        migrations.CreateModel(
            name='WatchHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, help_text='添加时间')),
                ('good', models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, to='Users.Good')),
                ('user', models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'WatchHistory',
                'verbose_name_plural': 'WatchHistorys',
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='good',
            field=models.ForeignKey(help_text='商品', on_delete=django.db.models.deletion.CASCADE, to='Users.Good'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(help_text='用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
