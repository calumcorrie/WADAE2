from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os


class UserProfile(models.Model):
    # Link UserProfile to a User model instance
    # The User model has username, email, password, date_joined and is_active attributes
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    # The additional attributes
    picture = models.ImageField(upload_to='profile_images', default='default.png', blank=True)
    starred = models.ManyToManyField('Plant', related_name='starred')

    def __str__(self):
        return self.user.username


# automatically create new UserProfile when new User is registered
@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()


@receiver(models.signals.pre_save, sender=UserProfile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old profile picture from filesystem
    when corresponding `MediaFile` object is updated.
    """
    if not instance.pk:
        return False

    try:
        old_pic = sender.objects.get(pk=instance.pk).picture
    except sender.DoesNotExist:
        return False

    new_pic = instance.picture
    if (not old_pic == new_pic) and ('default.png' not in old_pic.path):
        if os.path.isfile(old_pic.path):
            os.remove(old_pic.path)


class Category(models.Model):
    NAME_MAX_LENGTH = 40
    DESCRIPTION_MAX_LENGTH = 200

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Plant(models.Model):
    NAME_MAX_LENGTH = 40
    DESCRIPTION_MAX_LENGTH = 200
    LOCATION_MAX_LENGTH = 30

    # Django generates a unique integer id automatically
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH)
    picture = models.ImageField(upload_to='plant_images', default='default_plant.png', blank=True)
    uploadDate = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    location = models.CharField(max_length=LOCATION_MAX_LENGTH)
    views = models.IntegerField(default=0)
    isSold = models.BooleanField(default=False)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Plant, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


@receiver(models.signals.pre_save, sender=Plant)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old picture of plant from filesystem
    when corresponding `MediaFile` object is updated.
    """
    if not instance.pk:
        return False

    try:
        old_pic = sender.objects.get(pk=instance.pk).picture
    except sender.DoesNotExist:
        return False

    new_pic = instance.picture
    if (not old_pic == new_pic) and ('default_plant.png' not in old_pic.path):
        if os.path.isfile(old_pic.path):
            os.remove(old_pic.path)
