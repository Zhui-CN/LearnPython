import time
import calendar
from datetime import timedelta
from flask import render_template, request, session, g, redirect, url_for, jsonify
from . import admin_blu
from info.models import *
from info.utils.common import user_login_data
from info.utils import constants
from info.utils.response_code import RET


@admin_blu.route('/')
@user_login_data
def admin_index():
    user = g.user
    return render_template('admin/index.html', user=user.to_dict())


@admin_blu.route('/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template('admin/login.html')

    username = request.form.get("username")
    password = request.form.get("password")
    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数不足")

    user = User.query.filter(User.mobile == username).first()
    if not user:
        return render_template('admin/login.html', errmsg="用户不存在")

    if not user.check_passowrd(password):
        return render_template('admin/login.html', errmsg="密码错误")

    if not user.is_admin:
        return render_template('admin/login.html', errmsg="用户权限错误")

    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    session["is_admin"] = True

    return redirect(url_for('admin.admin_index'))


@admin_blu.route('/user_count')
def user_count():
    total_count = User.query.filter(User.is_admin == 0).count()

    now = time.localtime()

    # 查询月新增数
    mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
    mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
    mon_count = User.query.filter(User.is_admin == 0, User.create_time >= mon_begin_date).count()

    # 查询日新增数
    day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
    day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
    day_count = User.query.filter(User.is_admin == 0, User.create_time >= day_begin_date).count()

    # 查询图表信息
    # 获取到当天00:00:00时间

    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 定义空数组，保存数据
    active_date = []
    active_count = []

    # 依次添加数据，再反转
    for i in range(int(calendar.monthrange(now.tm_year, now.tm_mon)[1])):
        begin_date = now_date - timedelta(days=i)
        end_date = now_date - timedelta(days=(i - 1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = User.query.filter(User.is_admin == 0, User.last_login >= begin_date,
                                  User.last_login < end_date).count()
        active_count.append(count)

    active_date.reverse()
    active_count.reverse()

    data = {"total_count": total_count, "mon_count": mon_count, "day_count": day_count, "active_date": active_date,
            "active_count": active_count}

    return render_template('admin/user_count.html', data=data)


@admin_blu.route('/user_list')
def user_list():
    page = request.args.get("p", 1, type=int)
    paginate = User.query.filter(User.is_admin == 0).order_by(User.last_login.desc()).paginate(
        page, constants.ADMIN_USER_PAGE_MAX_COUNT, False
    )
    users = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    users_list = [user.to_admin_dict() for user in users]
    context = {"total_page": total_page, "current_page": current_page, "users": users_list}
    return render_template('admin/user_list.html', data=context)


@admin_blu.route('/news_review')
def news_review():
    page = request.args.get("p", 1, type=int)
    keywords = request.args.get("keywords", "")
    k = request.args.get("k", "")
    filters = [News.status != 0]
    if keywords:
        k = keywords
        filters.append(News.title.contains(keywords))
    elif k:
        filters.append(News.title.contains(keywords))
    paginate = News.query.filter(*filters).order_by(News.create_time.desc()) \
        .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

    news_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_dict_list = [news.to_review_dict() for news in news_list]
    context = {"total_page": total_page, "current_page": current_page, "news_list": news_dict_list, "k": k}
    return render_template('admin/news_review.html', data=context)


@admin_blu.route('/news_review_detail', methods=["GET", "POST"])
def news_review_detail():
    if request.method == "GET":
        news_id = request.args.get("news_id")
        if not news_id:
            return render_template('admin/news_review_detail.html', data={"errmsg": "未查询到此新闻"})
        news = News.query.get(news_id)
        if not news:
            return render_template('admin/news_review_detail.html', data={"errmsg": "未查询到此新闻"})
        return render_template('admin/news_review_detail.html', data={"news": news.to_dict()})

    news_id = request.json.get("news_id")
    action = request.json.get("action")
    news = News.query.get(news_id)

    if action == "accept":
        news.status = 0
    else:
        # 拒绝通过，需要获取原因
        reason = request.json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        news.reason = reason
        news.status = -1

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="操作成功")


@admin_blu.route('/news_edit')
def news_edit():
    page = request.args.get("p", 1, type=int)
    keywords = request.args.get("keywords", "")
    k = request.args.get("k", "")
    filters = []
    if keywords:
        k = keywords
        filters.append(News.title.contains(keywords))
    elif k:
        filters.append(News.title.contains(k))
    paginate = News.query.filter(*filters).order_by(News.create_time.desc()) \
        .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
    news_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_dict_list = [news.to_basic_dict() for news in news_list]
    context = {"total_page": total_page, "current_page": current_page, "news_list": news_dict_list, "k": k}
    return render_template('admin/news_edit.html', data=context)


@admin_blu.route('/news_edit_detail', methods=["GET", "POST"])
def news_edit_detail():
    if request.method == "GET":
        news_id = request.args.get("news_id")
        news = News.query.get(news_id)
        categories = Category.query.all()
        categories_li = []
        for category in categories:
            c_dict = category.to_dict()
            c_dict["is_selected"] = True if category.id == news.category_id else False
            categories_li.append(c_dict)
        # 移除`最新`分类
        categories_li.pop(0)
        data = {"news": news.to_dict(), "categories": categories_li}
        return render_template('admin/news_edit_detail.html', data=data)

    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 1.1 判断数据是否有值
    if not all([title, digest, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    news = News.query.get(news_id)
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="编辑成功")


@admin_blu.route('/news_category')
def get_news_category():
    categories = Category.query.all()
    categories_dicts = [category.to_dict() for category in categories]
    categories_dicts.pop(0)
    return render_template('admin/news_type.html', data={"categories": categories_dicts})


@admin_blu.route('/add_category', methods=["POST"])
def add_category():
    category_id = request.json.get("id")
    category_name = request.json.get("name")
    action = request.json.get("action")
    if action == "del":
        category = Category.query.get(category_id)
        db.session.delete(category)
    else:
        if not category_name:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        # 判断是否有分类id
        if category_id:
            category = Category.query.get(category_id)
            if not category:
                return jsonify(errno=RET.NODATA, errmsg="未查询到分类信息")
            category.name = category_name
        else:
            # 如果没有分类id，则是添加分类
            category = Category()
            category.name = category_name
            db.session.add(category)

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="保存数据成功")
