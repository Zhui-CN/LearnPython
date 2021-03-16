import xadmin

from courses.models import Course, Lesson, Video, CourseResource, CourseTag, BannerCourse
from xadmin.layout import Fieldset, Main, Side, Row
from import_export import resources


class CourseAdmin:
    list_display = ["name", "desc", "detail", "degree", "learn_times", "students", "teacher"]
    search_fields = ["name", "desc", "detail", "degree", "students"]
    list_filter = ["name", "teacher__name", "desc", "detail", "degree", "learn_times", "students"]
    list_editable = ["degree", "desc"]


class LessonAdmin:
    list_display = ["course", "name", "add_time"]
    search_fields = ["course", "name"]
    list_filter = ["course__name", "name", "add_time"]


class VideoAdmin:
    list_display = ["lesson", "name", "add_time"]
    search_fields = ["lesson", "name"]
    list_filter = ["lesson", "name", "add_time"]


class CourseResourceAdmin:
    list_display = ["course", "name", "file", "add_time"]
    search_fields = ["course", "name", "file"]
    list_filter = ["course", "name", "file", "add_time"]


class CourseTagAdmin:
    list_display = ["course", "tag", "add_time"]
    search_fields = ["course", "tag"]
    list_filter = ["course", "tag", "add_time"]


class LessonInline:
    model = Lesson
    # style = "tab"
    extra = 0


class CourseResourceInline:
    model = CourseResource
    style = "tab"
    extra = 1


class MyCourseResource(resources.ModelResource):
    class Meta:
        model = Course


class NewCourseAdmin:
    import_export_args = {'import_resource_class': MyCourseResource, 'export_resource_class': MyCourseResource}
    list_display = ["name", "desc", "show_image", "go_to", "detail", "degree", "learn_times", "students", "teacher"]
    search_fields = ["name", "desc", "detail", "degree", "students"]
    list_filter = ["name", "teacher__name", "desc", "detail", "degree", "learn_times", "students"]
    list_editable = ["degree", "desc"]
    readonly_fields = ["students", "click_nums", "fav_nums"]
    # exclude = ["click_nums", "fav_nums"]
    ordering = ["-click_nums"]
    model_icon = " fa fa-book"
    inlines = [LessonInline, CourseResourceInline]
    style_fields = {
        "detail": "ueditor"
    }

    def queryset(self):
        qs = super().queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(teacher=self.request.user.teacher)
        return qs

    def get_form_layout(self):
        self.form_layout = (
            Main(
                Fieldset("讲师信息", "teacher", "course_org", css_class='unsort no_title'),
                Fieldset(
                    "基本信息", "name", "desc",
                    Row("learn_times", "degree"),
                    Row("category", "tag"),
                    "need_know", "teacher_tell", "detail"
                ),
            ),
            Side(
                Fieldset("访问信息", 'fav_nums', 'click_nums', 'students'),
                Fieldset("选择信息", 'is_banner', 'is_classics'),
            )
        )
        return super(NewCourseAdmin, self).get_form_layout()


class BannerCourseAdmin:
    list_display = ["name", "desc", "detail", "degree", "learn_times", "students", "teacher"]
    search_fields = ["name", "desc", "detail", "degree", "students"]
    list_filter = ["name", "teacher__name", "desc", "detail", "degree", "learn_times", "students"]
    list_editable = ["degree", "desc"]

    def queryset(self):
        qs = super().queryset()
        qs = qs.filter(is_banner=True)
        return qs


# xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Course, NewCourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
xadmin.site.register(CourseTag, CourseTagAdmin)
