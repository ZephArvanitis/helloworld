from django.contrib import admin

from .models import ApplicationUser, DeviceType, UserDevice

# Register your models here.
admin.site.register(ApplicationUser)
admin.site.register(DeviceType)
admin.site.register(UserDevice)