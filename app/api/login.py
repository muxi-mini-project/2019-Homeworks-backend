import requests
from flask import jsonify, request
from . import app
from .. import db
from ..models import User


@app.route('/login/', methods = ['POST'])
def login():
    param = request.get_json()
    userName = param.get('userName')
    password = param.get('password')
    if userName is None or password is None:
        return jsonify({
                'msg': 'Invalid userName or password'
            }), 400
    payload = {
            'loginName': userName,
            'password': password,
            }
    session = requests.session()

    url = "http://spoc.ccnu.edu.cn/userLoginController/getUserProfile"
    rp = session.post(url, data=payload)
    status_code = rp.json().get('code')
    if status_code:
        return jsonify({
                'msg': 'login failed',
                }), 401
    else:
        url =  "http://spoc.ccnu.edu.cn/userInfo/getUserInfo"
        info = session.post(url).json()['data']['userInfoVO']
        userId = info.get('id')
        realName = info.get('userInfo').get('realname')
        cookie = 'SESSION' + '=' + session.cookies.get_dict()['SESSION']
        
        u = User.query.filter_by(userName=userName).first()
        if not u:
            u = User(userName=userName, name=realName)
            db.session.add(u)
            db.session.commit()
        token = u.generate_token(userId)

        js = {
                'msg': 'login successfully',
                'cookie': cookie,
                'token': token,
                'userName': userName,
                'realName': realName,
            }
        return jsonify(js), 200
