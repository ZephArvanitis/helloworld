from django.contrib import admin

from .models import ApplicationUser, DeviceType, UserDevice, PendingNotification

# Register your models here.
admin.site.register(ApplicationUser)
admin.site.register(DeviceType)
admin.site.register(UserDevice)
admin.site.register(PendingNotification)