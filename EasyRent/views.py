# -*- coding:utf-8 -*-
import os
import uuid

from copy import deepcopy
from flask import render_template, redirect, request, session, url_for, make_response, flash, jsonify, json
from qiniu import Auth, put_file
from sqlalchemy import text
import json
from urllib import urlopen, quote

from EasyRent import app, DBSession


# 登录函数
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果已经登录，则重定向到主页
    if 'is_login' in session and session['is_login']:
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        app.logger.error('username:' + username + ' password:' + password)
        if username != 'admin' or password != 'admin':
            error = '*用户名或密码不正确'
            flash(error)
            return redirect(url_for('login'))
        else:
            # 保存Cookie
            response = make_response(redirect(url_for('index')))
            if request.form.get('remember_me') is not None:
                response.set_cookie('username', username)
                response.set_cookie('password', password)
            session['is_login'] = True
            return response

    return render_template('login.html')


# 主页
@app.route('/index')
def index():
    if 'is_login' in session and session['is_login']:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


# 退出
@app.route('/logout')
def logout():
    session.pop("is_login", None)
    return redirect(url_for('login'))


# 添加租房信息
@app.route('/add_house_info', methods=['GET', 'POST'])
def add_house_info():
    if request.method == 'POST':
        # name = request.form['name']
        # phone = request.form['phone']
        # DBSession.execute(text('insert into test(name, phone) values(:name, :phone)'), {'name':name, 'phone':phone})

        # 先根据输入的地址获取经纬度
        url = 'http://api.map.baidu.com/geocoder/v2/'
        output = 'json'
        ak = 'w92IN1iDP57Z5TH2G4I9I5kzpTnNj4NC'
        # 由于本文地址变量为中文，为防止乱码，先用quote进行编码
        address = request.values.get('city') + request.values.get('region') + request.values.get('address')
        print address
        add = quote(str(address))
        uri = url + '?' + 'address=' + add + '&output=' + output + '&ak=' + ak
        req = urlopen(uri)
        res = req.read()
        temp = json.loads(res)

        # 非0状态都是地址解析失败
        if temp['status'] != 0:
            flash('地址解析失败，请重新输入地址')
            print '地址解析失败，请重新输入地址'
            return
        else:
            lat = temp['result']['location']['lat']
            lng = temp['result']['location']['lng']
            print lng, lat

        params = request.values.to_dict()
        params['lat'] = lat
        params['lng'] = lng

        # 插入数据到数据库
        DBSession.execute(text(
            'insert into house(city, region, images, address, minprice, maxprice, renttype, installation_wifi, installation_kitchen, installation_hoods, installation_water_heater, installation_washer, installation_toilet, pay_month, pay_season, pay_half, pay_year, longimage, lat, lng)' +
            'values(:city, :region, :images, :address, :minprice, :maxprice, :renttype, :installation_wifi, :installation_kitchen, :installation_hoods, :installation_water_heater, :installation_washer, :installation_toilet, :pay_month, :pay_season, :pay_half, :pay_year, :longimage, :lat, :lng)'),
                          params)
        DBSession.commit()
        DBSession.close()
        app.logger.error('添加成功')
        flash('添加成功')
        # return redirect(url_for('add_house_info'))
        return jsonify({'code': 200, 'msg': '添加成功'})
    return render_template('add_house_info.html')


# 上传图片到七牛
@app.route('/uploadFileToQiniu')
def uploadFileToQiniu():
    # if request.method == 'POST':
    # 需要填写你的 Access Key 和 Secret Key
    access_key = '-hmIOQEIQgnx_3dolengCAqBFqYF-07ntqFvENxd'
    secret_key = '7N7h6SINhsDjzhVbyaVo5hECxYRDvNcJMYREojXL'
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'images-server'
    # 上传到七牛后保存的文件名
    key = str(uuid.uuid1()) + '.png'
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    # 要上传文件的本地路径
    # localfile = request.values.get('path')
    basepath = os.path.dirname(__file__)
    localfile = os.path.join(basepath, 'static' + os.path.sep + 'uploads', 'temp.png')
    print(localfile)
    ret, info = put_file(token, key, localfile)
    print(ret)
    if info.status_code == 200:
        return jsonify({'code': 200, 'msg': '上传图片成功', 'path': ret['key']})
    else:
        return jsonify({'code': 201, 'msg': '上传图片失败'})


# 上传图片到服务器
@app.route('/uploadFileToServer', methods=['POST'])
def uploadFileToServer():
    if request.method == 'POST':
        basepath = os.path.dirname(__file__)
        file = request.files['file']
        file.save(os.path.join(basepath, 'static' + os.path.sep + 'uploads', 'temp.png'))
        return redirect(url_for('uploadFileToQiniu'))


# ====================================================================客户端相关接口====================================================================
@app.route('/get_house_info/<int:size>/<int:page>', methods=['POST'])
def get_house_info(size, page):
    # res叫做ResultProxy      rows[0]叫做RowProxy

    if request.method == 'POST':
        # 获取传递过来的参数
        cityIndex = request.values.get('cityIndex')
        regionIndex = request.values.get('regionIndex')
        priceIndex = request.values.get('priceIndex')
        # print cityIndex
        # print regionIndex
        # print priceIndex

        # 城市目前只有贵阳，只判断区域和价格范围即可
        regionSql = ''
        priceSql = ''
        if regionIndex == '0':
            regionSql = ' where 1=1'
        elif regionIndex == '1':
            regionSql = ' where region=' + '"观山湖区"'
        elif regionIndex == '2':
            regionSql = ' where region=' + '"南明区"'
        elif regionIndex == '3':
            regionSql = ' where region=' + '"云岩区"'
        elif regionIndex == '4':
            regionSql = ' where region=' + '"花溪区"'

        if priceIndex == '0':
            priceSql = ' and 1=1 '
        elif priceIndex == '1':
            priceSql = ' and minprice<1000 '
        elif priceIndex == '2':
            priceSql = ' and ((minprice>=1000 and minprice<=1500) or (maxprice>=1000 and maxprice<=1500)) '
        elif priceIndex == '3':
            priceSql = ' and ((minprice>=1500 and minprice<=2000) or (maxprice>=1500 and maxprice<=2000)) '
        elif priceIndex == '4':
            priceSql = ' and ((minprice>=2000 and minprice<=2500) or (maxprice>=2000 and maxprice<=2500)) '
        elif priceIndex == '5':
            priceSql = ' and maxprice>2500 '

        offset = (page - 1) * size
        res = DBSession.execute(text('select * from house' + regionSql + priceSql + 'order by id DESC limit :offset, :size'),
                                {'offset': offset, 'size': size})
        rows = res.fetchall()
        # print rows[0].id

        # dictData = dict(rows[0].items())
        jsonData = json.dumps([(dict(row.items())) for row in rows])
        DBSession.commit()
        DBSession.close()

        print jsonData
        return jsonData


# 获取联系方式
@app.route('/get_contact')
def get_contact():
    res = DBSession.execute(text('select * from contact'))
    row = res.fetchone()
    jsonData = json.dumps(dict(row.items()))
    DBSession.commit()
    DBSession.close()

    print jsonData
    return jsonData