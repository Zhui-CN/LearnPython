from utils.forms import AddAskForm
from django.shortcuts import render
from django.views.generic.base import View
from organizations.models import CourseOrg, City, Teacher
from pure_pagination import Paginator, PageNotAnInteger
from django.http import JsonResponse
from operations.models import UserFavorite
from django.db.models import Q


class OrgView(View):
    def get(self, request, *args, **kwargs):
        s_type = "org"
        ct = request.GET.get("ct", "")
        city_id = request.GET.get("city", "")
        sort = request.GET.get("sort", "")
        keywords = request.GET.get("keywords", "")
        all_org = CourseOrg.objects.all()
        hot_ogrs = all_org.order_by("-click_nums")[:3]
        if ct: all_org = all_org.filter(category=ct)
        if city_id and city_id.isdigit(): all_org = all_org.filter(city_id=int(city_id))
        org_nums = len(all_org)
        all_citys = City.objects.all()

        if keywords:
            all_org = all_org.filter(Q(name__icontains=keywords) | Q(desc__icontains=keywords))

        if sort == "students":
            all_org = all_org.order_by("-students")
        elif sort == "courses":
            all_org = all_org.order_by("-course_nums")

        try:
            page = request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        orgs = Paginator(all_org, per_page=5, request=request).page(page)
        data = {
            "all_orgs": orgs,
            "org_nums": org_nums,
            "all_citys": all_citys,
            "ct": ct,
            "city_id": city_id,
            "sort": sort,
            "hot_ogrs": hot_ogrs,
            "keywords": keywords,
            "s_type": s_type,
        }
        return render(request, "org-list.html", data)


class AddAskView(View):
    def post(self, request, *args, **kwargs):
        ask_form = AddAskForm(request.POST)
        if ask_form.is_valid():
            ask_form.save(commit=True)
            resp_dict = {
                "status": "success"
            }
        else:
            resp_dict = {
                "status": "fail",
                "msg": "添加出错"
            }

        return JsonResponse(resp_dict)


class OrgHomeView(View):
    def get(self, request, org_id, *args, **kwargs):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_courses = course_org.course_set.all()[:3]
        all_teacher = course_org.teacher_set.all()[:1]
        data = {
            "all_courses": all_courses,
            "all_teacher": all_teacher,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav,
        }
        return render(request, "org-detail-homepage.html", data)


class OrgTeacherView(View):
    def get(self, request, org_id, *args, **kwargs):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_teacher = course_org.teacher_set.all()
        data = {
            "all_teacher": all_teacher,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav,
        }
        return render(request, "org-detail-teachers.html", data)


class OrgCourseView(View):
    def get(self, request, org_id, *args, **kwargs):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        all_courses = course_org.course_set.all()

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        try:
            page = request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        courses = Paginator(all_courses, per_page=5, request=request).page(page)

        data = {
            "all_courses": courses,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav,
        }
        return render(request, "org-detail-course.html", data)


class OrgDescView(View):
    def get(self, request, org_id, *args, **kwargs):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        data = {
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav,
        }
        return render(request, "org-detail-desc.html", data)


class TeacherListView(View):
    def get(self, request, *args, **kwargs):
        s_type = "teacher"
        sort = request.GET.get("sort", "")
        keywords = request.GET.get("keywords", "")
        all_teachers = Teacher.objects.all()
        teacher_nums = len(all_teachers)
        hot_teachers = Teacher.objects.all().order_by("-click_nums")[:3]
        if keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=keywords))
        if sort == "hot":
            all_teachers = all_teachers.order_by("-click_nums")
        try:
            page = request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        teachers = Paginator(all_teachers, per_page=1, request=request).page(page)
        data = {
            "teachers": teachers,
            "teacher_nums": teacher_nums,
            "sort": sort,
            "hot_teachers": hot_teachers,
            "keywords": keywords,
            "s_type": s_type,
        }
        return render(request, "teachers-list.html", data)


class TeacherDetailView(View):
    def get(self, request, teacher_id, *args, **kwargs):
        teacher = Teacher.objects.get(id=int(teacher_id))

        teacher_fav = False
        org_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
                teacher_fav = True
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                org_fav = True

        hot_teachers = Teacher.objects.all().order_by("-click_nums")[:3]

        data = {
            "teacher": teacher,
            "teacher_fav": teacher_fav,
            "org_fav": org_fav,
            "hot_teachers": hot_teachers,
        }
        return render(request, "teacher-detail.html", data)
