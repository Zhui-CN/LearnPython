import redis
import logging
from flask import Flask, g, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config
from logging.handlers import RotatingFileHandler
from info.utils.common import do_index_class, user_login_data

db = SQLAlchemy()
redis_store = None


def create_app(config_name):
    """通过传入不同的配置名字，初始化其对应配置的应用实例"""
    setup_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT,
                                    decode_responses=True)
    CSRFProtect(app)
    Session(app)
    app.add_template_filter(do_index_class, "index_class")

    from info.module.index import index_blu
    from info.module.passport import passport_blu
    from info.module.news import news_blu
    from info.module.profile import profile_blu
    from info.module.admin import admin_blu
    app.register_blueprint(news_blu)
    app.register_blueprint(index_blu)
    app.register_blueprint(passport_blu)
    app.register_blueprint(profile_blu)
    app.register_blueprint(admin_blu)

    @app.errorhandler(404)
    @user_login_data
    def page_not_found(_):
        user = g.user
        data = {"user_info": user.to_dict() if user else None}
        return render_template('news/404.html', data=data)

    return app


def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
