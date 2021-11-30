from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
from django.contrib.auth.models import PermissionsMixin
from django_resized import ResizedImageField
from django.conf import settings
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("User must have a username")
        user_obj = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_staff_user(self, email, username, password):
        user_obj = self.create_user(
            email,
            username=username,
            password=password,
        )

        user_obj.is_staff = True
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, email, username, password):
        user_obj = self.create_user(
            email,
            username=username,
            password=password,
        )
        user_obj.is_admin = True
        user_obj.is_staff = True
        user_obj.is_active = True
        user_obj.save(using=self._db)
        return user_obj

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(
        max_length=255, null=True, blank=True, unique=True, validators=[alphanumeric])
    is_active = models.BooleanField(default=True)  # can login
    is_staff = models.BooleanField(default=False)  # staff user non superuser
    is_admin = models.BooleanField(default=False)  # superuser
    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True, null=True, blank=True)
    last_login = models.DateTimeField(
        verbose_name='last login', auto_now=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    def get_email(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True  # self.admin

    def has_module_perms(self, app_label):
        return True

    def get_profile_image_path(self):
        return 'media/' + str(self.profile_image)

    @property
    def _is_staff(self):
        return self.is_staff

    @property
    def _is_admin(self):
        return self.is_admin

    @property
    def _is_active(self):
        return self.is_active


phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$' 'eneter correct phone number')
class Profile(models.Model):
    '''is private
    multiple images 
    blocking/unblocking users 
    achievements
    social accounts
    '''
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    avatar = ResizedImageField(
        upload_to='images/profile_pics/', default='images/profile_pics/default_icon.jpg', quality=70, crop=['middle', 'center'], size=[320, 320], blank=True, null=True)
    following = models.ManyToManyField(
        'self', related_name='followers', blank=True, symmetrical=False)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    gender = models.CharField(
        max_length=6, choices=GENDER, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    mobile =  models.CharField(blank=True, null=True, validators=[alphanumeric], unique=True, max_length=15)
    location = models.CharField(max_length=150, null=True, blank=True)
    language = models.CharField(max_length=150, null=True, blank=True)
    country = models.CharField(max_length=150, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    # hide user email, image, username, etc.
    is_private_account = models.BooleanField(null=True, blank=True)


    def __str__(self):
        return self.user.username
