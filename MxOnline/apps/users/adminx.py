import xadmin


class AdminXGlobalSettings:
    site_title = "教学后台管理系统"
    site_footer = "在线教育"
    # menu_style = "accordion"  # 菜单栏收缩


class AdminXBaseSettings:
    enable_themes = True
    use_bootswatch = True


xadmin.site.register(xadmin.views.CommAdminView, AdminXGlobalSettings)
xadmin.site.register(xadmin.views.BaseAdminView, AdminXBaseSettings)
