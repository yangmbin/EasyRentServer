#-*- coding=utf-8 -*-
import sys

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config.from_object('config')
engine = create_engine('mysql+pymysql://root:root@127.0.0.1/easyrent?charset=utf8')
DB_Session = sessionmaker(bind=engine)
DBSession = DB_Session()


from EasyRent import views