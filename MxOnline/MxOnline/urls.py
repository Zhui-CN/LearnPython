"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import xadmin
from django.urls import path, include, re_path
from users.views import LoginView, LogoutView, SendSmsView, DynamicLoginView, RegisterView
from operations.views import IndexView
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
# from MxOnline.settings import MEDIA_ROOT, STATIC_ROOT
from MxOnline.settings import MEDIA_ROOT

urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),  # 资源文件
    # re_path(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),  # 资源文件
    path('', IndexView.as_view(), name="index"),
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('dlogin/', DynamicLoginView.as_view(), name="dlogin"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('captcha/', include("captcha.urls"), name="captcha"),
    path('send_sms/', csrf_exempt(SendSmsView.as_view()), name="send_sms"),
    re_path(r'^op/', include(("operations.urls", "operations"), namespace="op")),  # 用户相关操作
    re_path(r'^org/', include(("organizations.urls", "organizations"), namespace="org")),  # 机构相关页
    re_path(r'^course/', include(("courses.urls", "courses"), namespace="course")),  # 课程相关页
    re_path(r'^users/', include(("users.urls", "courses"), namespace="users")),  # 课程相关页
    re_path(r'^ueditor/', include('DjangoUeditor.urls'))
]
