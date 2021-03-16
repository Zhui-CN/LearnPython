import re
from django import forms
from captcha.fields import CaptchaField
from django_redis import get_redis_connection
from users.models import UserProfile
from operations.models import UserAsk
from operations.models import UserFavorite, CourseComments


class RegisterGetForm(forms.Form):
    captcha = CaptchaField()


class RegisterPostForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    code = forms.CharField(required=True, min_length=4, max_length=4)
    password = forms.CharField(required=True)

    def clean_code(self):
        mobile = self.data.get("mobile")
        code = self.data.get("code")
        redis_conn = get_redis_connection("verify_code")
        redis_code = redis_conn.get('verify_code:%s' % mobile)
        if redis_code.decode() != code:
            raise forms.ValidationError("验证码不正确")
        return code

    def clean_mobile(self):
        mobile = self.data.get("mobile")
        user = UserProfile.objects.filter(mobile=mobile)
        if user:
            raise forms.ValidationError("手机号码已注册")
        return mobile


class LoginForm(forms.Form):
    username = forms.CharField(required=True, min_length=3)
    password = forms.CharField(required=True, min_length=3)


class DynamicLoginForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    captcha = CaptchaField()


class DynamicLoginPostForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    code = forms.CharField(required=True, min_length=4, max_length=4)

    def clean_code(self):
        mobile = self.data.get("mobile")
        code = self.data.get("code")
        redis_conn = get_redis_connection("verify_code")
        redis_code = redis_conn.get('verify_code:%s' % mobile)
        if redis_code.decode() != code:
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data


class AddAskForm(forms.ModelForm):
    mobile = forms.CharField(max_length=11, min_length=11, required=True)

    class Meta:
        model = UserAsk
        fields = ["name", "mobile", "course_name"]

    def clean_mobile(self):
        mobile = self.data.get("mobile")
        regex_mobile = r"^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        if not re.match(mobile, regex_mobile):
            raise forms.ValidationError("手机号码不正确", code="mobile_invalid")
        return mobile


class UserFavForm(forms.ModelForm):
    class Meta:
        model = UserFavorite
        fields = ["fav_id", "fav_type"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = CourseComments
        fields = ["course", "comments"]


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["image"]


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["nick_name", "gender", "birthday", "address"]


class ChangePwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=3)
    password2 = forms.CharField(required=True, min_length=3)

    def clean(self):
        pwd1 = self.data.get("password1")
        pwd2 = self.data.get("password2")
        if pwd1 != pwd2:
            raise forms.ValidationError("密码不一致")
        return self.cleaned_data


class ChangeMobileForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    code = forms.CharField(required=True, min_length=4, max_length=4)

    def clean_code(self):
        mobile = self.data.get("mobile")
        code = self.data.get("code")
        redis_conn = get_redis_connection("verify_code")
        redis_code = redis_conn.get('verify_code:%s' % mobile)
        if redis_code and redis_code.decode() == code:
            return self.cleaned_data
        raise forms.ValidationError("验证码不正确")
