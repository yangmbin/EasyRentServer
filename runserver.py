#-*- coding=utf-8 -*-
from EasyRent import app

if __name__ == '__main__':
    # app.run(debug=True, ssl_context='adhoc')
    #app.run(debug=True, host='0.0.0.0', port=80, threaded=True)
    #app.run(debug=True, host='0.0.0.0', port=80, threaded=True, ssl_context=('ssl/214295754730911.crt', 'ssl/214295754730911.key'))
    app.run(debug=True, threaded=True)