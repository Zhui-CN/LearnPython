import re
from random import randint
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from lib.captcha.captcha import captcha
from utils.response_code import RETCODE
from users.models import User
from home.models import ArticleCategory, Article


class RegisterView(View):

    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('请输入正确的手机号码')
        if not re.match(r'^[0-9A-Za-z]{3,20}$', password):
            return HttpResponseBadRequest('请输入3-20位的密码')
        if password != password2:
            return HttpResponseBadRequest('两次输入的密码不一致')
        redis_conn = get_redis_connection('default')
        sms_code_server = redis_conn.get('sms:%s' % mobile)
        if sms_code_server is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if smscode != sms_code_server.decode():
            return HttpResponseBadRequest('短信验证码错误')
        user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        login(request, user)
        response = redirect(reverse('home:index'))
        response.set_cookie('is_login', True)
        response.set_cookie('username', user.username, max_age=7 * 24 * 3600)
        return response


class ImageCodeView(View):

    def get(self, request):
        uuid = request.GET.get("uuid")
        if not uuid:
            return HttpResponseBadRequest("请求参数错误")
        text, image = captcha.generate_captcha()
        redis_coon = get_redis_connection("default")
        redis_coon.setex("img:%s" % uuid, 300, text)
        return HttpResponse(image, content_type="image/jpeg")


class SmsCodeView(View):

    def get(self, request):
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        mobile = request.GET.get('mobile')
        if not all([image_code_client, uuid, mobile]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})
        redis_conn = get_redis_connection('default')
        image_code_server = redis_conn.get('img:%s' % uuid)
        if not image_code_server:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        redis_conn.delete('img:%s' % uuid)
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})
        sms_code = '%06d' % randint(0, 999999)
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功', 'sms_code': sms_code})


class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        next_page = request.GET.get('next')
        if not all([mobile, password]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('请输入正确的手机号')
        if not re.match(r'^[0-9A-Za-z]{3,20}$', password):
            return HttpResponseBadRequest('密码最少3位，最长20位')
        # 认证字段已经在User模型中的USERNAME_FIELD = 'mobile'修改
        user = authenticate(username=mobile, password=password)
        if user is None:
            return HttpResponseBadRequest('用户名或密码错误')
        login(request, user)
        if next_page:
            response = redirect(next_page)
        else:
            response = redirect(reverse('home:index'))
        # 设置状态保持的周期
        if remember != 'on':
            # 没有记住用户：浏览器会话结束就过期
            request.session.set_expiry(0)
            # 设置cookie
            response.set_cookie('is_login', True)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        else:
            # 记住用户：None表示两周后过期
            request.session.set_expiry(None)
            # 设置cookie
            response.set_cookie('is_login', True, max_age=14 * 24 * 3600)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        return response


class LogoutView(View):

    def get(self, request):
        logout(request)
        response = redirect(reverse('home:index'))
        response.delete_cookie('is_login')
        response.delete_cookie('username')
        return response


class ForgetPasswordView(View):

    def get(self, request):
        return render(request, "forget_password.html")

    def post(self, request):
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('请输入正确的手机号码')
        if not re.match(r'^[0-9A-Za-z]{3,20}$', password):
            return HttpResponseBadRequest('请输入3-20位的密码')
        if password != password2:
            return HttpResponseBadRequest('两次输入的密码不一致')
        redis_conn = get_redis_connection('default')
        sms_code_server = redis_conn.get('sms:%s' % mobile)
        if sms_code_server is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if smscode != sms_code_server.decode():
            return HttpResponseBadRequest('短信验证码错误')
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 如果该手机号不存在，则注册个新用户
            try:
                User.objects.create_user(username=mobile, mobile=mobile, password=password)
            except Exception:
                return HttpResponseBadRequest('修改失败，请稍后再试')
        else:
            user.set_password(password)
            user.save()
        response = redirect(reverse('users:login'))
        return response


class UserCenterView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        context = {
            'username': user.username,
            'mobile': user.mobile,
            'avatar': user.avatar.url if user.avatar else None,
            'user_desc': user.user_desc
        }
        return render(request, 'center.html', context=context)

    def post(self, request):
        user = request.user
        avatar = request.FILES.get('avatar')
        username = request.POST.get('username', user.username)
        user_desc = request.POST.get('desc', user.user_desc)
        try:
            user.username = username
            user.user_desc = user_desc
            if avatar:
                user.avatar = avatar
            user.save()
        except:
            return HttpResponseBadRequest('更新失败，请稍后再试')
        response = redirect(reverse('users:center'))
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        return response


class WriteBlogView(LoginRequiredMixin, View):

    def get(self, request):
        categories = ArticleCategory.objects.all()
        context = {
            'categories': categories
        }
        return render(request, 'write_blog.html', context=context)

    def post(self, request):
        avatar = request.FILES.get('avatar')
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags')
        sumary = request.POST.get('sumary')
        content = request.POST.get('content')
        user = request.user
        if not all([avatar, title, category_id, sumary, content]):
            return HttpResponseBadRequest('参数不全')
        try:
            article_category = ArticleCategory.objects.get(id=category_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseBadRequest('没有此分类信息')

        try:
            article = Article.objects.create(author=user, avatar=avatar, category=article_category,
                                             tags=tags, title=title, sumary=sumary, content=content)
        except:
            return HttpResponseBadRequest('发布失败，请稍后再试')

        return redirect(reverse('home:index'))
