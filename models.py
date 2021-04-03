from django.db import models


# Create your models here.
class ApplicationUser(models.Model):
    """Represent the user we might want to notify of...things.
    """
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)

    @property
    def devices(self):
        """Get devices associated with this user.
        """
        return UserDevice.objects.filter(user=self)


class UserDevice(models.Model):
    """Represent a user's device
    """
    user = models.ForeignKey('ApplicationUser', on_delete=models.CASCADE)
    device_type = models.ForeignKey('DeviceType', on_delete=models.CASCADE)
    device_token = models.CharField(max_length=100)


class DeviceType(models.Model):
    """Devices come in various types (e.g. mobile vs desktop). Describe type.
    """
    type_name = models.CharField(max_length=30)