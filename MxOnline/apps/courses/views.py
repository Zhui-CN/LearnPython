from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, PageNotAnInteger
from courses.models import Course, CourseTag, CourseResource, Video
from operations.models import UserFavorite, UserCourse, CourseComments
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


class CourseListView(View):
    def get(self, request, *args, **kwargs):
        s_type = "course"
        sort = request.GET.get("sort", "")
        keywords = request.GET.get("keywords", "")
        hot_courses = Course.objects.order_by("-click_nums")[:3]
        all_courses = Course.objects.order_by("-add_time")
        if keywords:
            all_courses = all_courses.filter(
                Q(name__icontains=keywords) | Q(desc__icontains=keywords) | Q(detail__icontains=keywords)
            )
        if sort == "students":
            all_courses = all_courses.order_by("-students")
        elif sort == "hot":
            all_courses = all_courses.order_by("-click_nums")
        try:
            page = request.GET.get("page", 1)
        except PageNotAnInteger:
            page = 1
        courses = Paginator(all_courses, per_page=2, request=request).page(page)

        data = {
            "all_courses": courses,
            "sort": sort,
            "hot_courses": hot_courses,
            "keywords": keywords,
            "s_type": s_type,
        }
        return render(request, "course-list.html", data)


class CourseDetailView(View):
    def get(self, request, course_id, *args, **kwargs):
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        has_fav_org = False
        has_fav_course = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True

        tags = course.coursetag_set.all()
        tag_ls = [tag.tag for tag in tags]
        course_tags = CourseTag.objects.filter(tag__in=tag_ls).exclude(course__id=course.id)
        related_course = list(set([course_tag.course for course_tag in course_tags]))
        data = {
            "course": course,
            "has_fav_org": has_fav_org,
            "has_fav_course": has_fav_course,
            "related_course": related_course,
        }
        return render(request, "course-detail.html", data)


class CourseLessonView(LoginRequiredMixin, View):
    login_url = "/login"

    def get(self, request, course_id, *args, **kwargs):
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
            course.students += 1
            course.save()

        course_resource = CourseResource.objects.filter(course=course)
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]
        data = {
            "course": course,
            "course_resource": course_resource,
            "related_courses": related_courses,
        }
        return render(request, "course-video.html", data)


class CourseCommentsView(LoginRequiredMixin, View):
    login_url = "/login"

    def get(self, request, course_id, *args, **kwargs):
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        comments = CourseComments.objects.filter(course=course)

        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
            course.students += 1
            course.save()

        course_resource = CourseResource.objects.filter(course=course)
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]
        data = {
            "course": course,
            "course_resource": course_resource,
            "related_courses": related_courses,
            "comments": comments,
        }
        return render(request, "course-comment.html", data)


class VideoView(View):
    login_url = "/login"

    def get(self, request, course_id, video_id, *args, **kwargs):
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        video = Video.objects.get(id=int(video_id))

        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
            course.students += 1
            course.save()

        course_resource = CourseResource.objects.filter(course=course)
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]
        data = {
            "course": course,
            "course_resource": course_resource,
            "related_courses": related_courses,
            "video": video,
        }
        return render(request, "course-play.html", data)
