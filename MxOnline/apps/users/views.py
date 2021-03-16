from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.backends import ModelBackend
from django_redis import get_redis_connection
from django.urls import reverse
from django.db.models import Q
from utils.messages import send_single_sms
from utils.random_str import generate_random
from users.models import UserProfile
from operations.models import UserFavorite, UserMessage
from organizations.models import CourseOrg, Teacher
from courses.models import Course
from pure_pagination import Paginator, PageNotAnInteger
from utils.forms import LoginForm, DynamicLoginForm, DynamicLoginPostForm, RegisterGetForm, RegisterPostForm, \
    UploadImageForm, UserInfoForm, ChangePwdForm, ChangeMobileForm


class CustomAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except:
            return None


class SendSmsView(View):
    def post(self, request, *args, **kwargs):
        send_sms_form = DynamicLoginForm(request.POST)
        result_dict = {}
        if not send_sms_form.is_valid():
            for key, value in send_sms_form.errors.items():
                result_dict[key] = value[0]
        else:
            mobile = send_sms_form.cleaned_data["mobile"]
            code = generate_random(4, 0)
            result = send_single_sms(code, mobile)
            result_dict["status"] = "success"
            result_dict["code"] = result
            redis_conn = get_redis_connection("verify_code")
            redis_conn.setex('verify_code:%s' % mobile, 300, code)
        return JsonResponse(result_dict)


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        register_get_form = RegisterGetForm()
        return render(request, "register.html", {"register_get_form": register_get_form})

    def post(self, request, *args, **kwargs):
        register_post_form = RegisterPostForm(request.POST)
        if not register_post_form.is_valid():
            register_get_form = RegisterGetForm()
            return render(
                request, "register.html",
                {"register_get_form": register_get_form, "register_post_form": register_post_form}
            )
        mobile = register_post_form.cleaned_data["mobile"]
        password = register_post_form.cleaned_data["password"]
        user = UserProfile()
        user.mobile = mobile
        user.username = mobile
        user.set_password(password)
        user.save()
        login(request, user)
        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))

        banner_courses = Course.objects.filter(is_banner=True)
        next_url = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        return render(request, "login.html",
                      {"login_form": login_form, "next_url": next_url, "banner_courses": banner_courses})

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(request.POST)
        banner_courses = Course.objects.filter(is_banner=True)
        if not login_form.is_valid():
            return render(request, "login.html", {"login_form": login_form, "banner_courses": banner_courses})
        username = login_form.cleaned_data["username"]
        password = login_form.cleaned_data["password"]
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get("next")
            return HttpResponseRedirect(reverse("index") if not next_url else next_url)
        else:
            return render(request, "login.html",
                          {"msg": "用户名或密码错误", "login_form": login_form, "banner_courses": banner_courses})


class DynamicLoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        banner_courses = Course.objects.filter(is_banner=True)
        next_url = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        return render(request, "login.html", {
            "login_form": login_form,
            "next_url": next_url,
            "banner_courses": banner_courses
        })

    def post(self, request, *args, **kwargs):
        login_form = DynamicLoginPostForm(request.POST)
        dynamic_login = True
        banner_courses = Course.objects.filter(is_banner=True)
        if not login_form.is_valid():
            d_form = DynamicLoginForm()
            return render(
                request, "login.html", {"login_form": login_form, "dynamic_login": dynamic_login, "d_form": d_form,
                                        "banner_courses": banner_courses}
            )
        mobile = login_form.cleaned_data["mobile"]
        existed_user = UserProfile.objects.filter(mobile=mobile)
        if existed_user:
            user = existed_user[0]
        else:
            user = UserProfile()
            user.mobile = mobile
            user.username = mobile
            user.set_password(generate_random(10, 2))
            user.save()
        login(request, user)
        next_url = request.GET.get("next")
        return HttpResponseRedirect(reverse("index") if not next_url else next_url)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class UserInfoView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "info"
        captcha_form = RegisterGetForm()
        data = {
            "captcha_form": captcha_form,
            "current_page": current_page,
        }
        return render(request, "usercenter-info.html", data)

    def post(self, request, *args, **kwargs):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(user_info_form.errors)


class UploadImageView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        result = dict(status="fail")
        if image_form.is_valid():
            image_form.save()
            result["status"] = "success"
        return JsonResponse(result)


class ChangePwdView(View):
    def post(self, request, *args, **kwargs):
        pwd_form = ChangePwdForm(request.POST)
        if pwd_form.is_valid():
            user = request.user
            user.set_password(pwd_form.cleaned_data["password1"])
            user.save()
            login(request, user)
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(pwd_form.errors)


class ChangeMobileView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        mobile_form = ChangeMobileForm(request.POST)
        if mobile_form.is_valid():
            mobile = mobile_form.cleaned_data["mobile"]
            if UserProfile.objects.filter(mobile=mobile):
                return JsonResponse({"mobile": "手机号已被占用"})
            user = request.user
            user.mobile = mobile
            user.username = mobile
            user.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(mobile_form.errors)


class MyFavOrgView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav"
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        org_list = [CourseOrg.objects.get(id=fav_org.fav_id) for fav_org in fav_orgs]
        data = {
            "org_list": org_list,
            "current_page": current_page,
        }
        return render(request, "usercenter-fav-org.html", data)


class MyFavTeahcerView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav"
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        teacher_list = [Teacher.objects.get(id=fav_teacher.fav_id) for fav_teacher in fav_teachers]
        data = {
            "teacher_list": teacher_list,
            "current_page": current_page,
        }
        return render(request, "usercenter-fav-teacher.html", data)


class MyFavCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav"
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        course_list = [Course.objects.get(id=fav_course.fav_id) for fav_course in fav_courses]
        data = {
            "course_list": course_list,
            "current_page": current_page,
        }
        return render(request, "usercenter-fav-course.html", data)


class MyMessageView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "mymessages"
        messages = UserMessage.objects.filter(user=request.user)
        for message in messages:
            message.has_read = True
            message.save()
        try:
            page = request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        messages = Paginator(messages, per_page=1, request=request).page(page)
        data = {
            "messages": messages,
            "current_page": current_page,
        }
        return render(request, "usercenter-message.html", data)
