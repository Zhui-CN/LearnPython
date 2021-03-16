from . import index_blu
from flask import render_template, current_app, request, jsonify, g
from info.models import News, Category
from info.utils import constants
from info.utils.response_code import RET
from info.utils.common import user_login_data


@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')


@index_blu.route('/')
@user_login_data
def index():
    news_ls = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    click_news_list = [news.to_basic_dict() for news in news_ls]

    categories = Category.query.all()
    categories_ls = [category.to_dict() for category in categories]

    data = {
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
        "categories": categories_ls,
    }
    return render_template('news/index.html', data=data)


@index_blu.route('/newslist')
def get_news_list():
    args_dict = request.args
    page = args_dict.get("page", 1, int)
    per_page = args_dict.get("per_page", constants.HOME_PAGE_MAX_NEWS, int)
    category_id = args_dict.get("cid", 1, int)

    filters = [News.status == 0] if category_id == 1 else [News.status == 0, News.category_id == category_id]
    paginate = News.query.filter(*filters).order_by(News.create_time.desc()) \
        .paginate(page, per_page, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_ls = [news.to_basic_dict() for news in items]
    return jsonify(errno=RET.OK, errmsg="OK", totalPage=total_page,
                   currentPage=current_page, newsList=news_ls, cid=category_id)
