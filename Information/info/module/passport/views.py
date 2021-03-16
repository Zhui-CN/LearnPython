import re
import random
from flask import current_app, jsonify, session
from flask import make_response
from flask import request
from info import redis_store
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blu
from info.models import *
from info.utils import constants


@passport_blu.route('/image_code')
def get_image_code():
    code_id = request.args.get('code_id')
    name, text, image = captcha.generate_captcha()
    redis_store.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


@passport_blu.route('/smscode', methods=["POST"])
def send_sms():
    param_dict = request.json
    mobile = param_dict.get("mobile")
    image_code = param_dict.get("image_code")
    image_code_id = param_dict.get("image_code_id")
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match("^1[3578][0-9]{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")

    real_image_code = redis_store.get("ImageCode_" + image_code_id)
    if real_image_code:
        real_image_code = real_image_code
        redis_store.delete("ImageCode_" + image_code_id)
    else:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    if image_code.lower() != real_image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    user = User.query.filter_by(mobile=mobile).first()
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")
    result = random.randint(0, 999999)
    sms_code = "%06d" % result
    current_app.logger.debug("短信验证码的内容：%s" % sms_code)
    redis_store.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    return jsonify(errno=RET.OK, errmsg="发送成功验证码为%s" % sms_code)


@passport_blu.route('/register', methods=["POST"])
def register():
    json_data = request.json
    mobile = json_data.get("mobile")
    sms_code = json_data.get("smscode")
    pwd = json_data.get("password")
    if not all([mobile, sms_code, pwd]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    real_sms_code = redis_store.get("SMS_" + mobile)
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    redis_store.delete("SMS_" + mobile)
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = pwd
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    return jsonify(errno=RET.OK, errmsg="OK")


@passport_blu.route('/login', methods=["POST"])
def login():
    json_data = request.json
    mobile = json_data.get("mobile")
    password = json_data.get("password")
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    user = User.query.filter_by(mobile=mobile).first()
    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    user.last_login = datetime.now()
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="OK")


@passport_blu.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return jsonify(errno=RET.OK, errmsg="OK")
