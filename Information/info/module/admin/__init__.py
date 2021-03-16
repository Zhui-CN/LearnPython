from flask import Blueprint, request, url_for, session, redirect
from info.models import User

admin_blu = Blueprint("admin", __name__, url_prefix='/admin')

from . import views


@admin_blu.before_request
def before_request():
    user_id = session.get("user_id")
    is_admin = session.get("is_admin")
    if not request.url.endswith(url_for("admin.admin_login")):
        if not user_id and not is_admin:
            return redirect('/')
        elif user_id and is_admin:
            return
        elif user_id:
            user = User.query.filter(User.id == user_id).first()
            if user.is_admin:
                session["user_id"] = user.id
                session["nick_name"] = user.nick_name
                session["mobile"] = user.mobile
                session["is_admin"] = True
                return redirect(url_for('admin.admin_index'))
            else:
                return redirect('/')

    elif user_id:
        user = User.query.filter(User.id == user_id).first()
        if user.is_admin:
            session["user_id"] = user.id
            session["nick_name"] = user.nick_name
            session["mobile"] = user.mobile
            session["is_admin"] = True
            return redirect(url_for('admin.admin_index'))
