from info.module.profile import profile_blu
from info.utils.common import user_login_data
from flask import g, redirect, render_template, request, jsonify, session
from info.models import *
from info.utils.response_code import RET


@profile_blu.route('/info')
@user_login_data
def get_user_info():
    user = g.user
    if not user:
        return redirect('/')
    return render_template("news/user.html", data={"user_info": user.to_dict()})


@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return redirect('/')
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user_info": user.to_dict()})
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    db.session.commit()
    session["nick_name"] = nick_name
    return jsonify(errno=RET.OK, errmsg="更新成功")


@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    if not user:
        return redirect('/')
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user_info": user.to_dict()})


@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    user = g.user
    if not user:
        return redirect('/')
    if request.method == "GET":
        return render_template('news/user_pass_info.html')
    data_dict = request.json
    old_password = data_dict.get("old_password")
    new_password = data_dict.get("new_password")
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")
    user.password = new_password
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="保存成功")


@profile_blu.route('/collection')
@user_login_data
def user_collection():
    user = g.user
    if not user:
        return redirect('/')
    p = request.args.get("p", 1, int)
    paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
    collections = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    collection_dict_li = [news.to_basic_dict() for news in collections]
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collections": collection_dict_li
    }
    return render_template('news/user_collection.html', data=data)


@profile_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():
    user = g.user
    if not user:
        return redirect('/')

    if request.method == "GET":
        categories = Category.query.all()
        categories_dicts = [category.to_dict() for category in categories]
        categories_dicts.pop(0)
        return render_template('news/user_news_release.html', data={"categories": categories_dicts})

    title = request.form.get("title")
    source = "个人发布"
    digest = request.form.get("digest")
    content = request.form.get("content")
    category_id = request.form.get("category_id")
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    # news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1
    db.session.add(news)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="发布成功，等待审核")


@profile_blu.route('/news_list')
@user_login_data
def news_list():
    user = g.user
    if not user:
        return redirect('/')
    p = request.args.get("p", 1, int)
    paginate = News.query.filter(News.user_id == user.id).paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
    news_li = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_dict_li = [news_item.to_review_dict() for news_item in news_li]
    data = {"news_list": news_dict_li, "total_page": total_page, "current_page": current_page}
    return render_template('news/user_news_list.html', data=data)


@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    user = g.user
    if not user:
        return redirect('/')

    p = request.args.get("p", 1, int)
    user = g.user
    paginate = user.followed.paginate(p, constants.USER_FOLLOWED_MAX_COUNT, False)
    follows = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    user_dict_li = [follow_user.to_dict() for follow_user in follows]
    data = {"users": user_dict_li, "total_page": total_page, "current_page": current_page}
    return render_template('news/user_follow.html', data=data)


@profile_blu.route('/other_info')
@user_login_data
def other_info():
    user = g.user
    user_id = request.args.get("id", type=int)
    other = User.query.get(user_id)
    is_followed = True if user and other.followers.filter(User.id == user.id).count() > 0 else False
    data = {
        "user_info": user.to_dict() if user else None,
        "other_info": other.to_dict(),
        "is_followed": is_followed
    }
    return render_template('news/other.html', data=data)


@profile_blu.route('/other_news_list')
def other_news_list():
    p = request.args.get("p", 1, int)
    user_id = request.args.get("user_id", type=int)
    user = User.query.get(user_id)
    paginate = News.query.filter(News.user_id == user.id).paginate(p, constants.OTHER_NEWS_PAGE_MAX_COUNT, False)
    news_li = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_dict_li = [news_item.to_review_dict() for news_item in news_li]
    data = {"news_list": news_dict_li, "total_page": total_page, "current_page": current_page}
    return jsonify(errno=RET.OK, errmsg="OK", data=data)
