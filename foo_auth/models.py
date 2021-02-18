from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, username="", email="", first_name="", last_name="", password="", user_type="CONTROLROOM", commit=True):


        user = self.model(
        	username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )

        user.set_password(password)
        if commit:
            user.save(using=self._db)
            
        return user

    def create_superuser(self,username, password, first_name="", last_name="" ):
        user = self.create_user(
        	username = username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            commit=False,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=50, unique = True, primary_key=True)
    email = models.EmailField(verbose_name=_('email address'), max_length=255, blank=True)

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    user_type = models.CharField(_('user type'), max_length=10, blank=True, default="NONE")
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    # is_superuser field provided by PermissionsMixin
    # groups field provided by PermissionsMixin
    # user_permissions field provided by PermissionsMixin

    date_joined = models.DateTimeField(
        _('date joined'), default=timezone.now
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []#'first_name', 'last_name']

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def __str__(self):
        return '{} <{}>'.format(self.get_full_name(), self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True