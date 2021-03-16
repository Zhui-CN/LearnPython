from . import news_blu
from flask import render_template, g, request, jsonify
from info.utils.common import user_login_data
from info.utils.response_code import RET
from info.models import *


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    news_ls = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    click_news_list = [news.to_basic_dict() for news in news_ls]
    news = News.query.get(news_id)
    news.clicks += 1

    # 判断用户是否收藏过该新闻
    is_collected = True if g.user and news in g.user.collection_news else False

    # 当前登录用户是否关注当前新闻作者
    is_followed = True if g.user and news.user and news.user.followers.filter(User.id == g.user.id).count() > 0 else False

    comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()

    comment_like_ids = []

    comment_ids = [comment.id for comment in comments] if g.user else []
    if len(comment_ids) > 0:
        # 取到当前用户在当前新闻的所有评论点赞的记录
        comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                 CommentLike.user_id == g.user.id).all()
        # 取出记录中所有的评论id
        comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]

    comment_list = []
    for item in comments if comments else []:
        comment_dict = item.to_dict()
        comment_dict["is_like"] = True if g.user and item.id in comment_like_ids else False
        comment_list.append(comment_dict)

    data = {
        "news": news.to_dict(),
        "user_info": g.user.to_dict() if g.user else None,
        "is_collected": is_collected,
        "is_followed": is_followed,
        "comments": comment_list,
        "click_news_list": click_news_list
    }
    return render_template('news/detail.html', data=data)


@news_blu.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    json_data = request.json
    news_id = json_data.get("news_id")
    action = json_data.get("action")
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    news = News.query.get(news_id)
    user.collection_news.append(news) if action == "collect" else user.collection_news.remove(news)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route('/news_comment', methods=["POST"])
@user_login_data
def add_news_comment():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    data_dict = request.json
    news_id = data_dict.get("news_id")
    comment_str = data_dict.get("comment")
    parent_id = data_dict.get("parent_id")
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id
    db.session.add(comment)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


@news_blu.route('/comment_like', methods=["POST"])
@user_login_data
def set_comment_like():
    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    data_dict = request.json
    comment_id = data_dict.get("comment_id")
    action = data_dict.get("action")
    comment = Comment.query.get(comment_id)
    if action == "add":
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = g.user.id
            comment.like_count += 1
            db.session.add(comment_like)
    else:
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if comment_like:
            comment.like_count -= 1
            db.session.delete(comment_like)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route('/followed_user', methods=["POST"])
@user_login_data
def followed_user():
    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    user_id = request.json.get("user_id")
    action = request.json.get("action")
    target_user = User.query.get(user_id)
    # 根据不同操作做不同逻辑
    if action == "follow":
        if target_user.followers.filter(User.id == g.user.id).count() > 0:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前已关注")
        target_user.followers.append(g.user)
    else:
        if target_user.followers.filter(User.id == g.user.id).count() > 0:
            target_user.followers.remove(g.user)

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="操作成功")
