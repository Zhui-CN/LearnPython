from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from operations.models import UserFavorite, CourseComments, Banner
from utils.forms import UserFavForm, CommentForm
from courses.models import Course
from organizations.models import CourseOrg, Teacher


class IndexView(View):
    def get(self, request, *args, **kwargs):
        banners = Banner.objects.all().order_by("index")
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)
        course_orgs = CourseOrg.objects.all()[:15]
        data = {
            "banners": banners,
            "courses": courses,
            "banner_courses": banner_courses,
            "course_orgs": course_orgs,
        }
        return render(request, "index.html", data)


class AddFavView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status:": "fail", "msg": "用户未登录"})

        user_fav_form = UserFavForm(request.POST)
        if user_fav_form.is_valid():
            fav_id = user_fav_form.cleaned_data["fav_id"]
            fav_type = user_fav_form.cleaned_data["fav_type"]
            existed_record = UserFavorite.objects.filter(user=request.user, fav_id=fav_id, fav_type=fav_type)
            if existed_record:
                existed_record.delete()
                if fav_type == 1:
                    course = Course.objects.get(id=fav_id)
                    course.fav_nums -= 1
                    course.save()
                elif fav_type == 2:
                    course_ogr = CourseOrg.objects.get(id=fav_id)
                    course_ogr.fav_nums -= 1
                    course_ogr.save()
                elif fav_type == 3:
                    teacher = Teacher.objects.get(id=fav_id)
                    teacher.fav_nums -= 1
                    teacher.save()
                return JsonResponse({"status": "success", "msg": "收藏"})
            else:
                user_fav = UserFavorite()
                course_ogr = CourseOrg.objects.get(id=fav_id)
                course_ogr.fav_nums += 1
                course_ogr.save()
                user_fav.fav_id = fav_id
                user_fav.user = request.user
                user_fav.fav_type = fav_type
                user_fav.save()
                return JsonResponse({"status": "success", "msg": "已收藏"})
        else:
            return JsonResponse({"status": "fail", "msg": "参数错误"})


class CommentView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status:": "fail", "msg": "用户未登录"})

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            course = comment_form.cleaned_data["course"]
            comments = comment_form.cleaned_data["comments"]
            comment = CourseComments()
            comment.user = request.user
            comment.comments = comments
            comment.course = course
            comment.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "fail", "msg": "参数错误"})
