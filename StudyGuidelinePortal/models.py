import os
from django.db import models
from tinymce.models import HTMLField
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from autoslug import AutoSlugField


# Create your models here.
class Profile(models.Model):

    # Renaming image name according to username
    def renameImage(self, filename):
        ext = filename.split('.')[-1]
        # rename file
        filename = f'{self.user.username}.{ext}'
        return os.path.join('images/user_profile/', filename)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(
        upload_to=renameImage, default='images/user_profile/default_user.jpg', null=True)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Department(models.Model):
    dep_id = models.AutoField(primary_key=True)
    dep_name = models.CharField(max_length=400)
    dep_slug = AutoSlugField(populate_from='dep_name',
                             unique=True, null=True, default=None)

    def __str__(self):
        return self.dep_name


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=200)
    course_pic = models.ImageField(
        upload_to='images/course/', default=None, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, default=None)
    # course_pic = models.ImageField(upload_to='StudyGuidelinePortal/static/images/course/')
    course_slug = AutoSlugField(
        populate_from='course_name', unique=True, null=True, default=None)

    def __str__(self):
        return self.course_name


class Lesson(models.Model):
    lesson_id = models.AutoField(primary_key=True)
    lesson_title = models.CharField(max_length=200)
    # lesson_desc = HTMLField()
    lesson_desc = RichTextField()
    views = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson_tags = models.TextField(default="")
    lesson_summary = models.CharField(max_length=500, default="")
    time = models.DateTimeField(auto_now_add=True)
    lesson_slug = AutoSlugField(
        populate_from='lesson_title', unique=True, null=True, default=None)

    def __str__(self):
        return self.lesson_title


class Query(models.Model):
    query_id = models.AutoField(primary_key=True)
    query_title = models.CharField(max_length=500)
    query_desc = HTMLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    query_slug = AutoSlugField(
        populate_from='query_title', unique=True, null=True, default=None)

    def __str__(self):
        return self.query_title


class Answer(models.Model):
    ans_id = models.AutoField(primary_key=True)
    ans_desc = HTMLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    # likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ans_desc[:15]} | by | {self.user}'


class SimilarLinks(models.Model):
    link_id = models.AutoField(primary_key=True)
    link_title = models.CharField(max_length=300)
    link_url = models.CharField(max_length=300)
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE)

    def __str__(self):
        return self.link_title


class LessonReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    rate = models.IntegerField(default=0)
    created_at: models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} | {self.user} | {self.lesson} | {self.rate}'


class Like(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} | {self.answer}'
    
class LessonWatchTime(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    watch_time = models.TextField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} | {self.lesson} | {self.watch_time} seconds'
