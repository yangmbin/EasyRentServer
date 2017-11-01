#-*- coding=utf-8 -*-
import sys

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config.from_object('config')
engine = create_engine('mysql+pymysql://root:root@127.0.0.1/easyrent?charset=utf8')
DB_Session = scoped_session(sessionmaker(bind=engine))
DBSession = DB_Session

# 图片服务器地址
imageServer = 'http://oxcptmnzi.bkt.clouddn.com/'


from EasyRent import views