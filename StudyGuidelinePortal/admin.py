from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Query)
admin.site.register(Answer)
admin.site.register(SimilarLinks)
admin.site.register(LessonReview)
admin.site.register(Like)
admin.site.register(Profile)
admin.site.register(Department)
admin.site.register(LessonWatchTime)
admin.site.register(MyCourse)


# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'product', 'rate', 'created_at')
# readonly_fields = ['created_at']
