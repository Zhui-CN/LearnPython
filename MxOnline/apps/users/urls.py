from django.urls import re_path, path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from users.views import UserInfoView, UploadImageView, ChangePwdView, ChangeMobileView, \
    MyFavOrgView, MyFavTeahcerView, MyFavCourseView, MyMessageView

urlpatterns = [
    path("info/", UserInfoView.as_view(), name="info"),
    path("image/upload/", UploadImageView.as_view(), name="image"),
    path("update/pwd/", ChangePwdView.as_view(), name="upload_pwd"),
    path("update/mobile/", ChangeMobileView.as_view(), name="upload_mobile"),
    path("mycourse/", login_required(TemplateView.as_view(template_name="usercenter-mycourse.html"), login_url="/login/"), {"current_page": "mycourse"}, name="mycourse"),
    path("myfavorg/", MyFavOrgView.as_view(), name="myfavorg"),
    path("myfavteacher/", MyFavTeahcerView.as_view(), name="myfavteacher"),
    path("myfavcourse/", MyFavCourseView.as_view(), name="myfavcourse"),
    path("mymessages/", MyMessageView.as_view(), name="mymessages"),
]
