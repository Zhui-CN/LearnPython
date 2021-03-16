import xadmin

from organizations.models import Teacher, CourseOrg, City


class TeacherAdmin:
    list_display = ["org", "name", "work_years", "work_company"]
    search_fields = ["org", "name", "work_years", "work_company"]
    list_filter = ["org", "name", "work_years", "work_company"]


class CourseOrgAdmin:
    list_display = ["name", "desc", "click_nums", "fav_nums"]
    search_fields = ["name", "desc", "click_nums", "fav_nums"]
    list_filter = ["name", "desc", "click_nums", "fav_nums"]
    style_fields = {
        "desc": "ueditor"
    }


class CityAdmin:
    list_display = ["id", "name", "desc", "add_time"]
    search_fields = ["name", "desc"]
    list_filter = ["name", "desc", "add_time"]
    list_editable = ["name", "desc"]


xadmin.site.register(Teacher, TeacherAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(City, CityAdmin)
