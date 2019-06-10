from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy as _

from .models import User

# admin.site.register(User)


class CustomLoginAdminSite(AdminSite):
    site_title = _('Event hosting Admin site')
    site_header = _('Administrator')
    index_title = _('CustomLogin')
    login_template = 'accounts/templates/admin/login_template.html'

admin_site = CustomLoginAdminSite()
admin_site.register(User)
