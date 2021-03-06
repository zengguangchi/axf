import hashlib
import random

import time
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from app.models import Wheel, Nav, Mustbuy, Shop, Mainshow, Foodtype, Goods, User, Cart, Order, OrderGoods


def generate_password(param):
    md5 = hashlib.md5()
    md5.update(param.encode('utf-8'))
    return md5.hexdigest()


def generate_token():
    temp = str(time.time()) + str(random.random())
    md5 = hashlib.md5()
    md5.update(temp.encode('utf-8'))
    return md5.hexdigest()


def index(request):
    wheels = Wheel.objects.all()
    navs = Nav.objects.all()

    mustbuys = Mustbuy.objects.all()
    shops = Shop.objects.all()
    shophead = shops[0]
    shoptabs = shops[1:3]
    shopclass_list = shops[3:7]
    shopcommends = shops[7:11]
    mainshows = Mainshow.objects.all()

    response_dir = {
        'wheels': wheels,
        'navs': navs,
        'mustbuys': mustbuys,
        'shophead': shophead,
        'shoptabs': shoptabs,
        'shopclass_list': shopclass_list,
        'shopcommends': shopcommends,
        'mainshows': mainshows
    }

    return render(request, 'index/index.html', context=response_dir)


def market(request, childid='0', sortid='0'):
    foodtypes = Foodtype.objects.all()

    index = int(request.COOKIES.get('index', '0'))

    categoryid = foodtypes[index].typeid

    if childid == '0':
        goods_list = Goods.objects.filter(categoryid=categoryid)
    else:
        goods_list = Goods.objects.filter(categoryid=categoryid).filter(childcid=childid)

    if sortid == '1':
        goods_list = goods_list.order_by('-productnum')
    elif sortid == '2':
        goods_list = goods_list.order_by('price')
    elif sortid == '3':
        goods_list = goods_list.order_by('-price')

    childtypenames = foodtypes[index].childtypenames

    childtype_list = []

    for item in childtypenames.split('#'):
        item_arr = item.split(':')
        temp_dir = {
            'name': item_arr[0],
            'id': item_arr[1]
        }

        childtype_list.append(temp_dir)

    response_dir = {
        'foodtypes': foodtypes,
        'goods_list': goods_list,
        'childtype_list': childtype_list,
        'childid': childid
    }

    token = request.session.get('token')
    userid = cache.get(token)

    if userid:
        user = User.objects.get(pk=userid)
        carts = user.cart_set.all()
        response_dir['carts'] = carts
    return render(request, 'market/market.html', context=response_dir)


def cart(request):
    token = request.session.get('token')
    user = None
    if token:
        userid = cache.get(token)
        if userid:
            user = User.objects.get(pk=userid)
            carts = Cart.objects.filter(user=user).exclude(number=0)
            isall = True
            for cart in carts:
                if not cart.isselect:
                    isall = False
            data = {
                'user': user,
                'carts': carts,
                'isall': isall
            }




        else:
            data = {}
        return render(request, 'cart/cart.html', data)


def mine(request):
    token = request.session.get('token')
    userid = cache.get(token)

    user = None
    if userid:
        user = User.objects.get(pk=userid)

    return render(request, 'mine/mine.html', context={'user': user})


def login(request):
    if request.method == 'GET':
        return render(request, 'mine/login.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = generate_password(request.POST.get('password'))

        try:
            user = User.objects.get(email=email)
            if user.password == password:
                token = generate_token()
                cache.set(token, user.id, 60 * 60 * 5)
                request.session['token'] = token
                return redirect('axf:mine')
            else:
                return render(request, 'mine/login.html', context={'err': "密码错误"})
        except:
            return render(request, 'mine/login.html', context={'err': "用户不存在"})


def register(request):
    if request.method == "GET":
        return render(request, 'mine/register.html')
    elif request.method == 'POST':
        user = User()
        user.email = request.POST.get('email')
        user.password = generate_password(request.POST.get('password'))
        user.name = request.POST.get('name')
        user.save()
        token = generate_token()
        cache.set(token, user.id, 60 * 60 * 5)
        request.session['token'] = token
        return redirect('axf:mine')


def logout(request):
    request.session.flush()
    return render(request, 'mine/mine.html')


def addcart(request):
    token = request.session.get('token')

    if token:
        userid = cache.get(token)
        user = User.objects.get(pk=userid)
        goodsid = request.GET.get('goodsid')
        goods = Goods.objects.get(pk=goodsid)
        carts = Cart.objects.filter(user=user).filter(goods=goods)
        if carts.exists():
            cart = carts.first()
            cart.number = cart.number + 1
            cart.save()

        else:
            cart = Cart()
            cart.user = user
            cart.goods = goods
            cart.number = 1
            cart.save()
        return JsonResponse({'msg': '添加成功', 'status': 1, 'number': cart.number})

    else:
        return JsonResponse({'msg': '请登录', 'status': 0})


def sucart(request):
    token = request.session.get('token')
    userid = cache.get(token)
    user = User.objects.get(pk=userid)
    goodsid = request.GET.get('goodsid')
    goods = Goods.objects.get(pk=goodsid)
    cart = Cart.objects.filter(user=user).filter(goods=goods).first()
    cart.number = cart.number - 1
    cart.save()
    data = {
        'msg': '删减商品成功',
        'status': 1,
        'number': cart.number
    }
    return JsonResponse(data)


def changecartselect(request):
    cartid = request.GET.get('cartid')
    cart = Cart.objects.get(pk=cartid)
    cart.isselect = not cart.isselect
    cart.save()
    data = {
        'msg': '修改状态成功',
        'status': 1,
        'isselect': cart.isselect
    }
    return JsonResponse(data)


def changecartall(request):
    isall = request.GET.get('isall')
    token = request.session.get('token')
    userid = cache.get(token)
    user = User.objects.get(pk=userid)
    carts = user.cart_set.all()
    if isall == "true":
        isall = False
    else:
        isall = True

    for cart in carts:
        cart.isselect = isall
        cart.save()
    data = {
        'msg': '全选状态修改',
        'status': 1
    }
    return JsonResponse(data)


def generate_identifier():
    temp = str(time.time()) + str(random.randrange(1000, 10000))
    return temp


def generateorder(request):
    token = request.session.get('token')
    userid = cache.get(token)
    user = User.objects.get(pk=userid)
    order = Order()
    order.user = user
    order.identifier = generate_identifier()
    order.save()
    carts = user.cart_set.filter(isselect=True)
    for cart in carts:
        ordergoods = OrderGoods()
        ordergoods.order = order
        ordergoods.goods = cart.goods
        ordergoods.number = cart.number
        ordergoods.save()
        cart.delete()
    return render(request, 'order/orderdetail.html', context={'order': order})


def orderlist(request):
    token = request.session.get('token')
    userid = cache.get(token)
    user = User.objects.get(pk=userid)
    orders = user.order_set.all()
    return render(request, 'order/orderlist.html', context={'orders': orders})


def orderdetail(request, identifier):
    order = Order.objects.filter(identifier=identifier).first()

    return render(request, 'order/orderdetail.html', context={'order': order})
